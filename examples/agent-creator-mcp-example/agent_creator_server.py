#!/usr/bin/env python3
"""
Agent Creator MCP Server

An MCP server that helps create Weave agent configurations by asking
interactive questions. This server provides tools for:
- Starting a new agent creation session
- Answering questions to build the configuration
- Generating the final agent YAML configuration

Usage:
    python agent_creator_server.py

The server communicates via stdio using the Model Context Protocol.
"""

import json
import sys
from typing import Any, Dict, List, Optional
import asyncio


class AgentCreatorSession:
    """Manages the state of an agent creation session"""

    def __init__(self):
        self.agent_name: Optional[str] = None
        self.description: Optional[str] = None
        self.model: Optional[str] = None
        self.tools: List[str] = []
        self.temperature: float = 0.7
        self.max_tokens: int = 1000
        self.inputs: Optional[str] = None
        self.outputs: Optional[str] = None
        self.current_step = 0

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """Get the next question to ask the user"""
        questions = [
            {
                "step": 0,
                "question": "What is the name of your agent?",
                "field": "agent_name",
                "hint": "Choose a descriptive name (e.g., 'researcher', 'writer', 'analyzer')",
                "example": "content_researcher"
            },
            {
                "step": 1,
                "question": "What is the purpose of this agent?",
                "field": "description",
                "hint": "Describe what this agent does in 1-2 sentences",
                "example": "Researches topics and gathers relevant information from various sources"
            },
            {
                "step": 2,
                "question": "Which LLM model should this agent use?",
                "field": "model",
                "hint": "Choose from: gpt-4, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet, claude-3-haiku",
                "example": "gpt-4"
            },
            {
                "step": 3,
                "question": "What tools should this agent have access to?",
                "field": "tools",
                "hint": "Comma-separated list. Available: web_search, calculator, text_length, json_validator, string_formatter",
                "example": "web_search, summarizer"
            },
            {
                "step": 4,
                "question": "What temperature should the model use? (0.0-1.0)",
                "field": "temperature",
                "hint": "Lower = more deterministic, Higher = more creative. Default is 0.7",
                "example": "0.7"
            },
            {
                "step": 5,
                "question": "Maximum tokens for responses?",
                "field": "max_tokens",
                "hint": "Maximum length of generated responses. Default is 1000",
                "example": "1000"
            },
            {
                "step": 6,
                "question": "Does this agent depend on another agent's output? (optional)",
                "field": "inputs",
                "hint": "Name of another agent this one depends on, or leave empty",
                "example": "researcher (or leave empty)"
            },
            {
                "step": 7,
                "question": "What should the output be named?",
                "field": "outputs",
                "hint": "Name for this agent's output that other agents can reference",
                "example": "research_summary"
            }
        ]

        if self.current_step < len(questions):
            return questions[self.current_step]
        return None

    def set_answer(self, field: str, value: str) -> bool:
        """Set the answer for a field and validate it"""
        try:
            if field == "agent_name":
                if not value or not value.replace("_", "").isalnum():
                    return False
                self.agent_name = value
            elif field == "description":
                self.description = value
            elif field == "model":
                valid_models = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus",
                               "claude-3-sonnet", "claude-3-haiku"]
                if value not in valid_models:
                    return False
                self.model = value
            elif field == "tools":
                if value.strip():
                    self.tools = [t.strip() for t in value.split(",")]
                else:
                    self.tools = []
            elif field == "temperature":
                temp = float(value)
                if not 0.0 <= temp <= 1.0:
                    return False
                self.temperature = temp
            elif field == "max_tokens":
                tokens = int(value)
                if tokens < 1:
                    return False
                self.max_tokens = tokens
            elif field == "inputs":
                self.inputs = value if value.strip() else None
            elif field == "outputs":
                self.outputs = value if value.strip() else None
            else:
                return False

            self.current_step += 1
            return True
        except (ValueError, AttributeError):
            return False

    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return (self.agent_name is not None and
                self.model is not None and
                self.current_step >= 8)

    def generate_yaml(self) -> str:
        """Generate the Weave YAML configuration"""
        config = {
            "version": "1.0",
            "agents": {
                self.agent_name: {
                    "model": self.model
                }
            }
        }

        agent_config = config["agents"][self.agent_name]

        if self.tools:
            agent_config["tools"] = self.tools

        if self.inputs:
            agent_config["inputs"] = self.inputs

        if self.outputs:
            agent_config["outputs"] = self.outputs

        if self.temperature != 0.7 or self.max_tokens != 1000:
            agent_config["config"] = {}
            if self.temperature != 0.7:
                agent_config["config"]["temperature"] = self.temperature
            if self.max_tokens != 1000:
                agent_config["config"]["max_tokens"] = self.max_tokens

        # Convert to YAML-like format
        yaml_lines = ["version: \"1.0\"", "", "agents:"]
        yaml_lines.append(f"  {self.agent_name}:")

        if self.description:
            yaml_lines.append(f"    # {self.description}")

        yaml_lines.append(f"    model: \"{self.model}\"")

        if self.tools:
            tools_str = "[" + ", ".join(self.tools) + "]"
            yaml_lines.append(f"    tools: {tools_str}")

        if self.inputs:
            yaml_lines.append(f"    inputs: \"{self.inputs}\"")

        if self.outputs:
            yaml_lines.append(f"    outputs: \"{self.outputs}\"")

        if self.temperature != 0.7 or self.max_tokens != 1000:
            yaml_lines.append("    config:")
            if self.temperature != 0.7:
                yaml_lines.append(f"      temperature: {self.temperature}")
            if self.max_tokens != 1000:
                yaml_lines.append(f"      max_tokens: {self.max_tokens}")

        return "\n".join(yaml_lines)


class AgentCreatorMCPServer:
    """MCP Server for creating Weave agent configurations"""

    def __init__(self):
        self.sessions: Dict[str, AgentCreatorSession] = {}

    def start_session(self, session_id: str) -> Dict[str, Any]:
        """Start a new agent creation session"""
        session = AgentCreatorSession()
        self.sessions[session_id] = session

        first_question = session.get_next_question()

        return {
            "session_id": session_id,
            "status": "started",
            "message": "Agent creation session started! I'll guide you through creating a Weave agent.",
            "next_question": first_question
        }

    def answer_question(self, session_id: str, answer: str) -> Dict[str, Any]:
        """Process an answer and return the next question or final config"""
        if session_id not in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} not found. Please start a new session."
            }

        session = self.sessions[session_id]
        current_question = session.get_next_question()

        if not current_question:
            return {
                "status": "error",
                "message": "No pending question in this session."
            }

        # Validate and set the answer
        field = current_question["field"]
        if not session.set_answer(field, answer):
            return {
                "status": "error",
                "message": f"Invalid answer for {field}. {current_question['hint']}",
                "retry_question": current_question
            }

        # Check if we're done
        if session.is_complete():
            yaml_config = session.generate_yaml()
            return {
                "status": "complete",
                "message": "Agent configuration created successfully!",
                "agent_name": session.agent_name,
                "configuration": yaml_config
            }

        # Get next question
        next_question = session.get_next_question()
        return {
            "status": "continue",
            "message": f"Answer recorded: {answer}",
            "next_question": next_question,
            "progress": f"{session.current_step}/8 questions answered"
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a session"""
        if session_id not in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} not found."
            }

        session = self.sessions[session_id]
        return {
            "status": "active",
            "session_id": session_id,
            "progress": f"{session.current_step}/8 questions answered",
            "current_question": session.get_next_question(),
            "is_complete": session.is_complete()
        }

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools"""
        return [
            {
                "name": "start_agent_creation",
                "description": "Start a new interactive agent creation session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Unique identifier for this session"
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "answer_question",
                "description": "Answer the current question in an agent creation session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier"
                        },
                        "answer": {
                            "type": "string",
                            "description": "Answer to the current question"
                        }
                    },
                    "required": ["session_id", "answer"]
                }
            },
            {
                "name": "get_session_status",
                "description": "Get the current status and progress of a session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier"
                        }
                    },
                    "required": ["session_id"]
                }
            }
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return {
                "tools": self.list_available_tools()
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "start_agent_creation":
                result = self.start_session(arguments.get("session_id"))
            elif tool_name == "answer_question":
                result = self.answer_question(
                    arguments.get("session_id"),
                    arguments.get("answer")
                )
            elif tool_name == "get_session_status":
                result = self.get_session_status(arguments.get("session_id"))
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }

        elif method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "agent-creator",
                    "version": "1.0.0"
                }
            }

        return {
            "error": {
                "code": -32601,
                "message": f"Unknown method: {method}"
            }
        }

    async def run(self):
        """Run the MCP server on stdio"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)

                # Add request ID to response
                if "id" in request:
                    response["id"] = request["id"]

                response["jsonrpc"] = "2.0"

                print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                if "id" in request:
                    error_response["id"] = request["id"]
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point"""
    server = AgentCreatorMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
