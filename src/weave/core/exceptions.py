"""Custom exceptions for Weave with helpful error messages."""

from typing import Optional, List


class WeaveError(Exception):
    """Base exception for all Weave errors with helpful suggestions."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        """Initialize error with message and optional suggestion.

        Args:
            message: Error message
            suggestion: Helpful suggestion for fixing the error
        """
        self.message = message
        self.suggestion = suggestion

        # Format full message
        full_message = message
        if suggestion:
            full_message += f"\n\n💡 Suggestion: {suggestion}"

        super().__init__(full_message)


class ConfigError(WeaveError):
    """Configuration parsing or validation error."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        file_path: Optional[str] = None,
        line: Optional[int] = None,
    ):
        """Initialize config error.

        Args:
            message: Error message
            suggestion: Helpful suggestion
            file_path: Path to config file with error
            line: Line number where error occurred
        """
        self.file_path = file_path
        self.line = line

        # Add location info if available
        if file_path:
            location = f"\n📁 File: {file_path}"
            if line:
                location += f" (line {line})"
            message = location + "\n" + message

        super().__init__(message, suggestion)


class GraphError(WeaveError):
    """Dependency graph error (cycles, invalid structure, etc)."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        affected_agents: Optional[List[str]] = None,
    ):
        """Initialize graph error.

        Args:
            message: Error message
            suggestion: Helpful suggestion
            affected_agents: List of agents involved in the error
        """
        self.affected_agents = affected_agents

        if affected_agents:
            message += f"\n📊 Affected agents: {', '.join(affected_agents)}"

        super().__init__(message, suggestion)


class ExecutionError(WeaveError):
    """Runtime execution error."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        agent_name: Optional[str] = None,
        run_id: Optional[str] = None,
    ):
        """Initialize execution error.

        Args:
            message: Error message
            suggestion: Helpful suggestion
            agent_name: Name of agent that failed
            run_id: Run ID for inspection
        """
        self.agent_name = agent_name
        self.run_id = run_id

        if agent_name:
            message = f"🤖 Agent '{agent_name}' failed:\n" + message

        if run_id:
            message += f"\n🔍 Inspect run: weave inspect {run_id}"

        super().__init__(message, suggestion)


class ToolError(WeaveError):
    """Tool execution error."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        tool_name: Optional[str] = None,
    ):
        """Initialize tool error.

        Args:
            message: Error message
            suggestion: Helpful suggestion
            tool_name: Name of tool that failed
        """
        self.tool_name = tool_name

        if tool_name:
            message = f"🔧 Tool '{tool_name}' failed:\n" + message

        super().__init__(message, suggestion)


class LLMError(WeaveError):
    """LLM API error."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize LLM error.

        Args:
            message: Error message
            suggestion: Helpful suggestion
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name
        """
        self.provider = provider
        self.model = model

        if provider and model:
            message = f"🤖 {provider.upper()} {model} error:\n" + message

        super().__init__(message, suggestion)
