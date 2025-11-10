"""Tool calling models and schemas."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ParameterType(str, Enum):
    """Parameter types for tool definitions."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ToolParameter(BaseModel):
    """Parameter definition for a tool."""

    name: str
    type: ParameterType
    description: str = ""
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    items: Optional[Dict[str, Any]] = None  # For array types
    properties: Optional[Dict[str, Any]] = None  # For object types


class ToolDefinition(BaseModel):
    """Complete tool definition with JSON Schema."""

    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    returns: Optional[str] = None
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    mcp_server: Optional[str] = None  # If tool comes from MCP server

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert tool definition to JSON Schema format."""
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type.value,
                "description": param.description,
            }

            if param.enum:
                prop["enum"] = param.enum
            if param.items:
                prop["items"] = param.items
            if param.properties:
                prop["properties"] = param.properties
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


class ToolCall(BaseModel):
    """A request to call a tool."""

    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    call_id: Optional[str] = None


class ToolResult(BaseModel):
    """Result from a tool execution."""

    tool_name: str
    call_id: Optional[str] = None
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class Tool(BaseModel):
    """Runtime tool with callable implementation."""

    definition: ToolDefinition
    handler: Optional[Any] = None  # Callable function

    class Config:
        arbitrary_types_allowed = True

    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given arguments."""
        import time

        start_time = time.time()

        try:
            # Validate arguments against parameters
            self._validate_arguments(arguments)

            # If handler exists, call it
            if self.handler:
                if callable(self.handler):
                    result = self.handler(**arguments)
                else:
                    raise ValueError(f"Handler for {self.definition.name} is not callable")
            else:
                # Mock execution for tools without handlers
                result = {
                    "status": "executed",
                    "tool": self.definition.name,
                    "arguments": arguments,
                }

            execution_time = time.time() - start_time

            return ToolResult(
                tool_name=self.definition.name,
                success=True,
                result=result,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                tool_name=self.definition.name,
                success=False,
                error=str(e),
                execution_time=execution_time,
            )

    def _validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate arguments against tool parameters."""
        param_map = {p.name: p for p in self.definition.parameters}

        # Check required parameters
        for param in self.definition.parameters:
            if param.required and param.name not in arguments:
                raise ValueError(f"Missing required parameter: {param.name}")

        # Check unknown parameters
        for arg_name in arguments:
            if arg_name not in param_map:
                raise ValueError(f"Unknown parameter: {arg_name}")

        # Basic type checking
        for arg_name, arg_value in arguments.items():
            param = param_map[arg_name]
            if not self._check_type(arg_value, param.type):
                raise ValueError(
                    f"Invalid type for {arg_name}: expected {param.type.value}, "
                    f"got {type(arg_value).__name__}"
                )

    def _check_type(self, value: Any, expected_type: ParameterType) -> bool:
        """Basic type checking for parameter values."""
        type_map = {
            ParameterType.STRING: str,
            ParameterType.NUMBER: (int, float),
            ParameterType.INTEGER: int,
            ParameterType.BOOLEAN: bool,
            ParameterType.ARRAY: list,
            ParameterType.OBJECT: dict,
        }

        expected_py_type = type_map.get(expected_type)
        if expected_py_type:
            return isinstance(value, expected_py_type)
        return True
