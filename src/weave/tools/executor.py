"""Tool execution engine."""

from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

from weave.tools.models import Tool, ToolCall, ToolDefinition, ToolResult
from weave.tools.mcp_client import MCPClient


class ToolExecutor:
    """Manages and executes tools for agents."""

    def __init__(self, mcp_config_path: Optional[Path] = None):
        """Initialize tool executor.

        Args:
            mcp_config_path: Path to MCP configuration file
        """
        self.tools: Dict[str, Tool] = {}
        self.mcp_client = MCPClient(mcp_config_path)

        # Load built-in tools
        self._load_builtin_tools()

        # Load tools from MCP servers
        self._load_mcp_tools()

    def _load_builtin_tools(self) -> None:
        """Load built-in tools."""
        from weave.tools.builtin import get_builtin_tools

        for tool in get_builtin_tools():
            self.register_tool(tool)

    def _load_mcp_tools(self) -> None:
        """Load tools from configured MCP servers."""
        for server in self.mcp_client.list_servers():
            if server.enabled:
                tools = self.mcp_client.get_server_tools(server.name)
                for tool_def in tools:
                    # Create tool without handler (will use MCP client)
                    tool = Tool(definition=tool_def, handler=None)
                    self.register_tool(tool)

    def register_tool(self, tool: Tool) -> None:
        """Register a tool for execution.

        Args:
            tool: Tool to register
        """
        self.tools[tool.definition.name] = tool

    def register_tool_function(
        self, definition: ToolDefinition, handler: Callable
    ) -> None:
        """Register a tool with a callable handler.

        Args:
            definition: Tool definition
            handler: Callable function to execute the tool
        """
        tool = Tool(definition=definition, handler=handler)
        self.register_tool(tool)

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool if found, None otherwise
        """
        return self.tools.get(tool_name)

    def list_tools(
        self, category: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[ToolDefinition]:
        """List available tools.

        Args:
            category: Filter by category
            tags: Filter by tags

        Returns:
            List of tool definitions
        """
        tools = []

        for tool in self.tools.values():
            # Apply filters
            if category and tool.definition.category != category:
                continue

            if tags:
                if not any(tag in tool.definition.tags for tag in tags):
                    continue

            tools.append(tool.definition)

        return tools

    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call.

        Args:
            tool_call: Tool call request

        Returns:
            ToolResult with execution result
        """
        tool = self.get_tool(tool_call.tool_name)

        if not tool:
            return ToolResult(
                tool_name=tool_call.tool_name,
                call_id=tool_call.call_id,
                success=False,
                error=f"Unknown tool: {tool_call.tool_name}",
            )

        # If tool is from MCP server, use MCP client
        if tool.definition.mcp_server:
            result = await self.mcp_client.call_tool(
                tool.definition.mcp_server, tool_call.tool_name, tool_call.arguments
            )
            result.call_id = tool_call.call_id
            return result

        # Otherwise, execute locally
        result = await tool.execute(tool_call.arguments)
        result.call_id = tool_call.call_id
        return result

    async def execute_tools(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute multiple tool calls.

        Args:
            tool_calls: List of tool calls

        Returns:
            List of tool results
        """
        results = []
        for tool_call in tool_calls:
            result = await self.execute_tool(tool_call)
            results.append(result)
        return results

    def get_tool_schemas(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """Get JSON schemas for tools.

        Args:
            tool_names: List of tool names

        Returns:
            List of tool schemas in JSON format
        """
        schemas = []
        for tool_name in tool_names:
            tool = self.get_tool(tool_name)
            if tool:
                schemas.append(tool.definition.to_json_schema())
        return schemas
