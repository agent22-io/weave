"""MCP (Model Context Protocol) client for tool integration."""

import json
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field

from weave.tools.models import ToolDefinition, ToolParameter, ParameterType, ToolResult


class MCPServer(BaseModel):
    """MCP server configuration."""

    name: str
    command: str  # Command to start the MCP server
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    description: str = ""
    enabled: bool = True


class MCPClient:
    """Client for interacting with MCP servers."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize MCP client.

        Args:
            config_path: Path to MCP configuration file (default: .weave/mcp.yaml)
        """
        self.config_path = config_path or Path(".weave/mcp.yaml")
        self.servers: Dict[str, MCPServer] = {}
        self._server_processes: Dict[str, Any] = {}

        if self.config_path.exists():
            self.load_config()

    def load_config(self) -> None:
        """Load MCP server configurations from file."""
        import yaml

        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)

            if data and "servers" in data:
                for name, config in data["servers"].items():
                    self.servers[name] = MCPServer(name=name, **config)

        except Exception as e:
            print(f"Warning: Failed to load MCP config: {e}")

    def save_config(self) -> None:
        """Save MCP server configurations to file."""
        import yaml

        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "servers": {
                name: {
                    "command": server.command,
                    "args": server.args,
                    "env": server.env,
                    "description": server.description,
                    "enabled": server.enabled,
                }
                for name, server in self.servers.items()
            }
        }

        with open(self.config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def add_server(self, server: MCPServer) -> None:
        """Add an MCP server configuration."""
        self.servers[server.name] = server
        self.save_config()

    def remove_server(self, name: str) -> None:
        """Remove an MCP server configuration."""
        if name in self.servers:
            del self.servers[name]
            self.save_config()

    def list_servers(self) -> List[MCPServer]:
        """List all configured MCP servers."""
        return list(self.servers.values())

    def get_server_tools(self, server_name: str) -> List[ToolDefinition]:
        """Get available tools from an MCP server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of tool definitions available from the server
        """
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")

        server = self.servers[server_name]
        if not server.enabled:
            return []

        # For v1, return mock tools
        # In v2, this would make actual MCP protocol calls
        return self._get_mock_server_tools(server_name)

    def _get_mock_server_tools(self, server_name: str) -> List[ToolDefinition]:
        """Get mock tools for demonstration (v1 implementation)."""
        mock_tools = {
            "filesystem": [
                ToolDefinition(
                    name="read_file",
                    description="Read contents of a file",
                    parameters=[
                        ToolParameter(
                            name="path",
                            type=ParameterType.STRING,
                            description="Path to the file",
                            required=True,
                        )
                    ],
                    category="filesystem",
                    mcp_server=server_name,
                ),
                ToolDefinition(
                    name="write_file",
                    description="Write contents to a file",
                    parameters=[
                        ToolParameter(
                            name="path",
                            type=ParameterType.STRING,
                            description="Path to the file",
                            required=True,
                        ),
                        ToolParameter(
                            name="content",
                            type=ParameterType.STRING,
                            description="Content to write",
                            required=True,
                        ),
                    ],
                    category="filesystem",
                    mcp_server=server_name,
                ),
            ],
            "web": [
                ToolDefinition(
                    name="fetch_url",
                    description="Fetch content from a URL",
                    parameters=[
                        ToolParameter(
                            name="url",
                            type=ParameterType.STRING,
                            description="URL to fetch",
                            required=True,
                        )
                    ],
                    category="web",
                    mcp_server=server_name,
                ),
            ],
            "database": [
                ToolDefinition(
                    name="query_database",
                    description="Execute a database query",
                    parameters=[
                        ToolParameter(
                            name="query",
                            type=ParameterType.STRING,
                            description="SQL query to execute",
                            required=True,
                        )
                    ],
                    category="database",
                    mcp_server=server_name,
                ),
            ],
        }

        # Return tools based on server name pattern
        for key in mock_tools:
            if key in server_name.lower():
                return mock_tools[key]

        return []

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> ToolResult:
        """Call a tool on an MCP server.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            ToolResult with execution result
        """
        import time

        start_time = time.time()

        if server_name not in self.servers:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Unknown MCP server: {server_name}",
                execution_time=time.time() - start_time,
            )

        server = self.servers[server_name]
        if not server.enabled:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"MCP server '{server_name}' is disabled",
                execution_time=time.time() - start_time,
            )

        # For v1, return mock results
        # In v2, this would make actual MCP protocol calls
        result = {
            "status": "executed",
            "tool": tool_name,
            "server": server_name,
            "arguments": arguments,
            "mock": True,
        }

        return ToolResult(
            tool_name=tool_name,
            success=True,
            result=result,
            execution_time=time.time() - start_time,
        )

    def create_example_config(self) -> None:
        """Create an example MCP configuration file."""
        self.servers = {
            "filesystem": MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"],
                description="File system operations (read, write, list)",
                enabled=True,
            ),
            "web": MCPServer(
                name="web",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-fetch"],
                description="Web fetching and scraping",
                enabled=True,
            ),
            "github": MCPServer(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_TOKEN": "${GITHUB_TOKEN}"},
                description="GitHub API integration",
                enabled=False,
            ),
        }
        self.save_config()
