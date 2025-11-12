"""
OpenAI-compatible API server for Weave agents.

This module provides a headless OpenAI-compatible REST API endpoint
that allows Weave agents to be consumed as if they were OpenAI chat models.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import AsyncIterator, Optional, Dict, Any, List
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    raise ImportError(
        "FastAPI and uvicorn are required for OpenAI mode. "
        "Install with: pip install 'weave-cli[api]'"
    )

from ..parser.config import load_config_from_path
from ..runtime.llm_executor import LLMExecutor
from ..core.sessions import ConversationSession
from ..core.models import WeaveConfig


# OpenAI-compatible request/response models
class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


class OpenAIServer:
    """OpenAI-compatible server for Weave agents."""

    def __init__(
        self,
        agent_name: str,
        config_path: Path,
        host: str = "0.0.0.0",
        port: int = 8000,
        verbose: bool = True
    ):
        self.agent_name = agent_name
        self.config_path = config_path
        self.host = host
        self.port = port
        self.verbose = verbose
        self.app = FastAPI(title="Weave OpenAI-Compatible API")
        self.weave_config: Optional[WeaveConfig] = None
        self.agent_obj = None

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.on_event("startup")
        async def startup_event():
            """Load configuration on startup."""
            try:
                self.weave_config = load_config_from_path(self.config_path)
                if self.agent_name not in self.weave_config.agents:
                    available = ", ".join(self.weave_config.agents.keys())
                    raise ValueError(
                        f"Agent '{self.agent_name}' not found. "
                        f"Available agents: {available}"
                    )
                self.agent_obj = self.weave_config.agents[self.agent_name]
                self._log(f"✓ Loaded agent: {self.agent_name}")
                self._log(f"✓ Model: {self.agent_obj.model}")
                self._log(f"✓ Server started on http://{self.host}:{self.port}")
                self._log(f"✓ Endpoint: http://{self.host}:{self.port}/v1/chat/completions")
            except Exception as e:
                self._log(f"✗ Failed to load configuration: {e}", error=True)
                raise

        @self.app.get("/")
        async def root():
            """Root endpoint with server info."""
            return {
                "name": "Weave OpenAI-Compatible API",
                "agent": self.agent_name,
                "model": self.agent_obj.model if self.agent_obj else None,
                "endpoints": ["/v1/chat/completions"]
            }

        @self.app.get("/v1/models")
        async def list_models():
            """List available models (OpenAI-compatible)."""
            return {
                "object": "list",
                "data": [
                    {
                        "id": self.agent_name,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "weave"
                    }
                ]
            }

        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """
            OpenAI-compatible chat completions endpoint.

            Supports both streaming and non-streaming responses.
            """
            try:
                # Log request
                self._log_request(request)

                # Create session
                session_id = str(uuid.uuid4())[:8]
                session = ConversationSession(
                    session_id=session_id,
                    weave_name="api",
                    agent_name=self.agent_obj.name
                )

                # Initialize executor (no console for headless mode)
                executor = LLMExecutor(
                    console=None,
                    verbose=False,
                    config=self.weave_config,
                    session=session
                )

                # Extract user message
                user_message = self._extract_user_message(request.messages)
                if not user_message:
                    raise HTTPException(status_code=400, detail="No user message found")

                # Handle streaming vs non-streaming
                if request.stream:
                    return StreamingResponse(
                        self._stream_response(
                            executor,
                            user_message,
                            request,
                            session_id
                        ),
                        media_type="text/event-stream"
                    )
                else:
                    return await self._non_stream_response(
                        executor,
                        user_message,
                        request,
                        session_id
                    )

            except HTTPException:
                raise
            except Exception as e:
                self._log(f"✗ Error processing request: {e}", error=True)
                raise HTTPException(status_code=500, detail=str(e))

    def _extract_user_message(self, messages: List[Message]) -> str:
        """Extract the last user message from the conversation."""
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content
        return ""

    async def _non_stream_response(
        self,
        executor: LLMExecutor,
        user_message: str,
        request: ChatCompletionRequest,
        session_id: str
    ) -> ChatCompletionResponse:
        """Generate a non-streaming response."""
        # Execute agent
        context = {"task": user_message}
        response = await executor.execute_agent(self.agent_obj, context)

        # Log response
        self._log_response(response.content, session_id)

        # Build OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

        return ChatCompletionResponse(
            id=completion_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=response.content),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=len(user_message.split()),
                completion_tokens=len(response.content.split()),
                total_tokens=len(user_message.split()) + len(response.content.split())
            )
        )

    async def _stream_response(
        self,
        executor: LLMExecutor,
        user_message: str,
        request: ChatCompletionRequest,
        session_id: str
    ) -> AsyncIterator[str]:
        """Generate a streaming response."""
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created = int(time.time())

        # Execute agent
        context = {"task": user_message}
        response = await executor.execute_agent(self.agent_obj, context)

        # Log response
        self._log_response(response.content, session_id)

        # Stream the response in chunks
        words = response.content.split()
        for i, word in enumerate(words):
            chunk = ChatCompletionChunk(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta={"content": word + " "},
                        finish_reason=None
                    )
                ]
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            await asyncio.sleep(0.01)  # Small delay for streaming effect

        # Send final chunk
        final_chunk = ChatCompletionChunk(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[
                ChatCompletionChunkChoice(
                    index=0,
                    delta={},
                    finish_reason="stop"
                )
            ]
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    def _log(self, message: str, error: bool = False):
        """Log a message to stdout."""
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prefix = "ERROR" if error else "INFO"
            print(f"[{timestamp}] [{prefix}] {message}", flush=True)

    def _log_request(self, request: ChatCompletionRequest):
        """Log an incoming request."""
        user_msg = self._extract_user_message(request.messages)
        preview = user_msg[:100] + "..." if len(user_msg) > 100 else user_msg
        self._log(f"→ Request: model={request.model}, stream={request.stream}")
        self._log(f"  Message: {preview}")

    def _log_response(self, content: str, session_id: str):
        """Log a response."""
        preview = content[:100] + "..." if len(content) > 100 else content
        self._log(f"← Response: session={session_id}")
        self._log(f"  Content: {preview}")

    def run(self):
        """Run the server."""
        self._log(f"Starting Weave OpenAI-Compatible API server...")
        self._log(f"Agent: {self.agent_name}")
        self._log(f"Config: {self.config_path}")

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning" if self.verbose else "error"
        )


def start_openai_server(
    agent_name: str,
    config_path: Path,
    host: str = "0.0.0.0",
    port: int = 8000,
    verbose: bool = True
):
    """
    Start an OpenAI-compatible API server for a Weave agent.

    Args:
        agent_name: Name of the agent from config
        config_path: Path to the config file
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8000)
        verbose: Enable verbose logging (default: True)
    """
    server = OpenAIServer(
        agent_name=agent_name,
        config_path=config_path,
        host=host,
        port=port,
        verbose=verbose
    )
    server.run()
