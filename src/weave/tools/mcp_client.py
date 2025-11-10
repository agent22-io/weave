"""MCP (Model Context Protocol) client for tool integration."""

import os
import json
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

from weave.tools.models import ToolDefinition, ToolParameter, ParameterType


@dataclass
class MCPServer:
    """MCP server configuration."""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    enabled: bool = True
    description: str = ""


class MCPClient:
    """Client for interacting with MCP servers via stdio."""

    def __init__(self, weave_config: Optional[Any] = None):
        """Initialize MCP client.

        Args:
            weave_config: Weave configuration containing MCP server definitions
        """
        self.servers: Dict[str, MCPServer] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.config_path = Path.home() / ".weave" / "mcp_config.yaml"

        # Load MCP servers from weave config
        if weave_config and hasattr(weave_config, "mcp_servers"):
            for name, server_config in weave_config.mcp_servers.items():
                self.servers[name] = MCPServer(
                    name=name,
                    command=server_config.get("command", ""),
                    args=server_config.get("args", []),
                    env=server_config.get("env", {}),
                    enabled=server_config.get("enabled", True),
                    description=server_config.get("description", ""),
                )

        # Also load from config file if exists
        if self.config_path.exists():
            self._load_from_config()

    def _load_from_config(self):
        """Load MCP servers from config file."""
        try:
            import yaml
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            if config and "mcp_servers" in config:
                for name, server_config in config["mcp_servers"].items():
                    if name not in self.servers:
                        self.servers[name] = MCPServer(
                            name=name,
                            command=server_config.get("command", ""),
                            args=server_config.get("args", []),
                            env=server_config.get("env", {}),
                            enabled=server_config.get("enabled", True),
                            description=server_config.get("description", ""),
                        )
        except Exception:
            # Silently fail if config doesn't exist or is invalid
            pass

    def list_servers(self) -> List[MCPServer]:
        """List all configured MCP servers."""
        return list(self.servers.values())

    def start_server(self, server_name: str) -> bool:
        """Start an MCP server process.

        Args:
            server_name: Name of the server to start

        Returns:
            True if server started successfully
        """
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")

        if server_name in self.processes:
            # Already running
            return True

        server = self.servers[server_name]
        if not server.enabled:
            return False

        try:
            # Start server process with stdio communication
            env = os.environ.copy()
            env.update(server.env)

            process = subprocess.Popen(
                [server.command] + server.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1
            )

            self.processes[server_name] = process

            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {
                        "name": "weave",
                        "version": "0.1.0"
                    }
                }
            }

            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    return True

            return False

        except Exception as e:
            if server_name in self.processes:
                del self.processes[server_name]
            raise Exception(f"Failed to start MCP server {server_name}: {e}")

    def stop_server(self, server_name: str):
        """Stop an MCP server process."""
        if server_name in self.processes:
            process = self.processes[server_name]
            process.terminate()
            process.wait(timeout=5)
            del self.processes[server_name]

    def get_server_tools(self, server_name: str) -> List[ToolDefinition]:
        """Get available tools from an MCP server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of tool definitions from the server
        """
        if server_name not in self.servers:
            return []

        server = self.servers[server_name]
        if not server.enabled:
            return []

        # Start server if not running
        if server_name not in self.processes:
            if not self.start_server(server_name):
                return []

        try:
            process = self.processes[server_name]

            # Send tools/list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            if not response_line:
                return []

            response = json.loads(response_line)
            if "result" not in response:
                return []

            # Parse tools from response
            tools = []
            for tool_data in response["result"].get("tools", []):
                parameters = []
                input_schema = tool_data.get("inputSchema", {})

                for param_name, param_info in input_schema.get("properties", {}).items():
                    param_type = self._parse_param_type(param_info.get("type", "string"))
                    parameters.append(ToolParameter(
                        name=param_name,
                        type=param_type,
                        description=param_info.get("description", ""),
                        required=param_name in input_schema.get("required", [])
                    ))

                tools.append(ToolDefinition(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    parameters=parameters,
                    category="mcp",
                    mcp_server=server_name
                ))

            return tools

        except Exception as e:
            print(f"Error getting tools from {server_name}: {e}")
            return []

    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if server_name not in self.processes:
            if not self.start_server(server_name):
                return {"error": f"Failed to start MCP server: {server_name}"}

        try:
            process = self.processes[server_name]

            # Send tools/call request
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            process.stdin.write(json.dumps(call_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            if not response_line:
                return {"error": "No response from MCP server"}

            response = json.loads(response_line)

            if "result" in response:
                return response["result"]
            elif "error" in response:
                return {"error": response["error"]}
            else:
                return {"error": "Invalid response from MCP server"}

        except Exception as e:
            return {"error": f"Error calling tool {tool_name}: {e}"}

    def _parse_param_type(self, json_type: str) -> ParameterType:
        """Convert JSON schema type to ParameterType."""
        type_map = {
            "string": ParameterType.STRING,
            "number": ParameterType.NUMBER,
            "integer": ParameterType.NUMBER,
            "boolean": ParameterType.BOOLEAN,
            "array": ParameterType.ARRAY,
            "object": ParameterType.OBJECT,
        }
        return type_map.get(json_type, ParameterType.STRING)

    def __del__(self):
        """Clean up: stop all running servers."""
        for server_name in list(self.processes.keys()):
            try:
                self.stop_server(server_name)
            except:
                pass
