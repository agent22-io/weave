"""Real LLM execution engine for Weave agents."""

import os
import time
import asyncio
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass

from rich.console import Console

if TYPE_CHECKING:
    from ..core.models import Agent, WeaveConfig

# Optional imports for LLM providers
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class LLMResponse:
    """Response from an LLM API call."""

    content: str
    model: str
    tokens_used: int
    execution_time: float
    finish_reason: str
    tool_calls: List[Dict[str, Any]] = None


class LLMExecutor:
    """
    Real LLM execution engine.

    Supports:
    - OpenAI (GPT-4, GPT-3.5, etc.)
    - Anthropic (Claude 3)
    - Local models (future)
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        verbose: bool = False,
        config: Optional["WeaveConfig"] = None,
    ):
        """Initialize LLM executor.

        Args:
            console: Rich console for output
            verbose: Enable verbose logging
            config: Weave configuration
        """
        self.console = console or Console()
        self.verbose = verbose
        self.config = config

        # Initialize API clients
        self._init_openai()
        self._init_anthropic()

    def _init_openai(self) -> None:
        """Initialize OpenAI client."""
        if not HAS_OPENAI:
            if self.verbose:
                self.console.print("[yellow]OpenAI not installed. Run: pip install openai[/yellow]")
            self.openai_client = None
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            if self.verbose:
                self.console.print("[yellow]OPENAI_API_KEY not set[/yellow]")
            self.openai_client = None
            return

        self.openai_client = openai.OpenAI(api_key=api_key)

    def _init_anthropic(self) -> None:
        """Initialize Anthropic client."""
        if not HAS_ANTHROPIC:
            if self.verbose:
                self.console.print("[yellow]Anthropic not installed. Run: pip install anthropic[/yellow]")
            self.anthropic_client = None
            return

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            if self.verbose:
                self.console.print("[yellow]ANTHROPIC_API_KEY not set[/yellow]")
            self.anthropic_client = None
            return

        self.anthropic_client = anthropic.Anthropic(api_key=api_key)

    async def execute_agent(
        self,
        agent: "Agent",
        context: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Execute an agent using real LLM API.

        Args:
            agent: Agent configuration
            context: Execution context (inputs from other agents, etc.)
            tools: Available tools for the agent

        Returns:
            LLMResponse with agent output
        """
        start_time = time.time()

        # Build prompt
        system_prompt = self._build_system_prompt(agent)
        user_prompt = self._build_user_prompt(agent, context)

        # Get model configuration
        temperature = 0.7
        max_tokens = 1000

        if agent.llm_config:
            temperature = agent.llm_config.temperature
            max_tokens = agent.llm_config.max_tokens

        # Determine provider from model name
        model = agent.model.lower()

        if "gpt" in model or "openai" in model:
            response = await self._call_openai(
                model=agent.model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
            )
        elif "claude" in model or "anthropic" in model:
            response = await self._call_anthropic(
                model=agent.model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
            )
        else:
            raise ValueError(f"Unsupported model: {agent.model}")

        response.execution_time = time.time() - start_time
        return response

    def _build_system_prompt(self, agent: "Agent") -> str:
        """Build system prompt for agent."""
        parts = []

        # Add capabilities if present
        if agent.capabilities:
            caps = ", ".join(agent.capabilities)
            parts.append(f"You are an AI agent with these capabilities: {caps}")

        # Add custom prompt
        if agent.prompt:
            parts.append(agent.prompt)
        else:
            parts.append("You are a helpful AI assistant.")

        # Add tool instructions if agent has tools
        if agent.tools:
            parts.append(
                f"\nYou have access to the following tools: {', '.join(agent.tools)}"
            )
            parts.append("Use these tools when appropriate to complete the task.")

        return "\n\n".join(parts)

    def _build_user_prompt(self, agent: "Agent", context: Dict[str, Any]) -> str:
        """Build user prompt from context."""
        parts = []

        # Add input from previous agent if present
        if agent.inputs and agent.inputs in context:
            input_data = context[agent.inputs]
            parts.append(f"Input from {agent.inputs}:")
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    parts.append(f"  {key}: {value}")
            else:
                parts.append(f"  {input_data}")

        # Add any global context
        if "task" in context:
            parts.append(f"\nTask: {context['task']}")

        if not parts:
            parts.append("Please analyze and respond based on your instructions.")

        return "\n".join(parts)

    async def _call_openai(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Call OpenAI API."""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Set OPENAI_API_KEY.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add tools if provided
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        if self.verbose:
            self.console.print(f"[dim]Calling OpenAI {model}...[/dim]")

        try:
            response = self.openai_client.chat.completions.create(**kwargs)

            # Extract response
            message = response.choices[0].message
            content = message.content or ""

            # Extract tool calls if present
            tool_calls = None
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                    for tc in message.tool_calls
                ]

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=response.usage.total_tokens,
                execution_time=0,  # Set by caller
                finish_reason=response.choices[0].finish_reason,
                tool_calls=tool_calls,
            )

        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]OpenAI API error: {e}[/red]")
            raise

    async def _call_anthropic(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Call Anthropic API."""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized. Set ANTHROPIC_API_KEY.")

        # Map model name to Anthropic format
        if not model.startswith("claude-"):
            model = f"claude-{model}"

        kwargs = {
            "model": model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add tools if provided (Anthropic format)
        if tools:
            kwargs["tools"] = tools

        if self.verbose:
            self.console.print(f"[dim]Calling Anthropic {model}...[/dim]")

        try:
            response = self.anthropic_client.messages.create(**kwargs)

            # Extract content
            content = ""
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "arguments": block.input,
                    })

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                execution_time=0,  # Set by caller
                finish_reason=response.stop_reason,
                tool_calls=tool_calls if tool_calls else None,
            )

        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Anthropic API error: {e}[/red]")
            raise
