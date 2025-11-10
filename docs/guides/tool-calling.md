# Tool Calling

Weave provides a powerful tool calling system that allows agents to interact with external functions, APIs, and services. This guide covers everything you need to know about using tools in your agents.

## Overview

Tools are functions that agents can call to perform specific tasks. Weave supports:

- **Built-in Tools** - Ready-to-use tools for common tasks
- **Custom Tools** - Define your own tools with Python functions
- **MCP Tools** - Tools from Model Context Protocol servers

## Built-in Tools

Weave comes with several built-in tools:

### Math Tools

**calculator** - Evaluate mathematical expressions
```bash
weave tools --schema calculator
```

Example usage:
```python
{
  "expression": "2 + 2 * 5"
}
# Returns: 12
```

### Text Tools

**text_length** - Count characters, words, and lines
```python
{
  "text": "Hello world\nThis is a test"
}
# Returns: {characters: 27, words: 5, lines: 2}
```

**string_formatter** - Format strings with variables
```python
{
  "template": "Hello {name}, you are {age} years old",
  "variables": {"name": "Alice", "age": 30}
}
# Returns: "Hello Alice, you are 30 years old"
```

### Data Tools

**json_validator** - Validate and parse JSON
```python
{
  "json_string": '{"key": "value"}'
}
# Returns: {valid: true, parsed: {...}}
```

**list_operations** - Perform list operations
```python
{
  "operation": "sum",
  "items": [1, 2, 3, 4, 5]
}
# Returns: {result: 15}
```

## Listing Tools

View all available tools:

```bash
# List all tools
weave tools

# Filter by category
weave tools --category math
weave tools --category text
weave tools --category data

# Filter by tags
weave tools --tags "json,parsing"

# View detailed schema
weave tools --schema calculator
```

## Tool Configuration in Agents

Specify tools in your agent configuration:

```yaml
agents:
  data_processor:
    model: "gpt-4"
    tools:
      - calculator
      - json_validator
      - list_operations
    outputs: "processed_data"
```

## Creating Custom Tools

### Define Tool Schema

Create a tool definition:

```python
from weave.tools import ToolDefinition, ToolParameter, ParameterType

my_tool = ToolDefinition(
    name="weather_lookup",
    description="Get weather for a location",
    parameters=[
        ToolParameter(
            name="location",
            type=ParameterType.STRING,
            description="City name or ZIP code",
            required=True
        ),
        ToolParameter(
            name="units",
            type=ParameterType.STRING,
            description="Temperature units (celsius/fahrenheit)",
            required=False,
            default="celsius",
            enum=["celsius", "fahrenheit"]
        )
    ],
    category="weather",
    tags=["weather", "api", "data"]
)
```

### Implement Tool Function

```python
def weather_lookup(location: str, units: str = "celsius") -> dict:
    """Get weather for a location."""
    # Your implementation here
    response = requests.get(f"https://api.weather.com/{location}")
    data = response.json()

    # Convert units if needed
    if units == "fahrenheit":
        data['temp'] = data['temp'] * 9/5 + 32

    return {
        "location": location,
        "temperature": data['temp'],
        "conditions": data['conditions'],
        "units": units
    }
```

### Register Tool

```python
from weave.tools import ToolExecutor, Tool

executor = ToolExecutor()
tool = Tool(definition=my_tool, handler=weather_lookup)
executor.register_tool(tool)
```

## Tool Execution

### Programmatic Execution

```python
from weave.tools import ToolExecutor, ToolCall
import asyncio

# Create executor
executor = ToolExecutor()

# Create tool call
call = ToolCall(
    tool_name="calculator",
    arguments={"expression": "10 + 20"}
)

# Execute
result = asyncio.run(executor.execute_tool(call))

print(f"Success: {result.success}")
print(f"Result: {result.result}")
print(f"Execution time: {result.execution_time}s")
```

### Multiple Tool Calls

```python
calls = [
    ToolCall(tool_name="calculator", arguments={"expression": "5 * 5"}),
    ToolCall(tool_name="text_length", arguments={"text": "Hello World"}),
]

results = asyncio.run(executor.execute_tools(calls))

for result in results:
    print(f"{result.tool_name}: {result.result}")
```

## Tool Parameters

### Parameter Types

Weave supports standard JSON Schema types:

```python
ParameterType.STRING    # Text strings
ParameterType.NUMBER    # Floating point numbers
ParameterType.INTEGER   # Whole numbers
ParameterType.BOOLEAN   # true/false
ParameterType.ARRAY     # Lists
ParameterType.OBJECT    # Dictionaries
```

### Parameter Options

```python
ToolParameter(
    name="level",
    type=ParameterType.STRING,
    description="Log level",
    required=True,          # Is parameter required?
    default="info",         # Default value
    enum=["debug", "info", "error"]  # Allowed values
)
```

### Array Parameters

```python
ToolParameter(
    name="tags",
    type=ParameterType.ARRAY,
    description="List of tags",
    items={"type": "string"}  # Array item schema
)
```

### Object Parameters

```python
ToolParameter(
    name="config",
    type=ParameterType.OBJECT,
    description="Configuration object",
    properties={
        "timeout": {"type": "number"},
        "retry": {"type": "boolean"}
    }
)
```

## Error Handling

Tools return a `ToolResult` with success status:

```python
result = await executor.execute_tool(call)

if result.success:
    print(f"Result: {result.result}")
else:
    print(f"Error: {result.error}")
```

## Best Practices

### 1. Clear Descriptions

```python
# Good
description="Calculate the sum of an array of numbers"

# Bad
description="Math function"
```

### 2. Validate Inputs

```python
def my_tool(value: int) -> dict:
    if value < 0:
        raise ValueError("Value must be positive")
    return {"result": value * 2}
```

### 3. Structured Outputs

```python
# Good - Structured response
return {
    "status": "success",
    "data": result,
    "metadata": {"timestamp": time.time()}
}

# Bad - Inconsistent response
return result  # Could be any type
```

### 4. Proper Error Messages

```python
try:
    result = expensive_operation()
    return {"success": True, "result": result}
except Exception as e:
    return {"success": False, "error": str(e)}
```

### 5. Category Organization

Group related tools:

```python
category="web"      # Web scraping, HTTP requests
category="data"     # Data processing, transformation
category="file"     # File operations
category="api"      # External API calls
category="text"     # Text manipulation
```

## Tool Categories

Common categories for organizing tools:

- **math** - Mathematical operations
- **text** - Text processing and formatting
- **data** - Data manipulation and validation
- **web** - Web requests and scraping
- **file** - File system operations
- **api** - External API integrations
- **database** - Database queries
- **image** - Image processing
- **audio** - Audio processing
- **nlp** - Natural language processing

## Advanced Features

### Tool Versioning

```python
ToolDefinition(
    name="data_processor",
    description="Process data - v2.0",
    # ... parameters ...
    tags=["v2", "data", "processing"]
)
```

### Tool Chaining

```python
# Tool 1: Fetch data
result1 = await executor.execute_tool(
    ToolCall(tool_name="fetch_url", arguments={"url": "..."})
)

# Tool 2: Parse data
result2 = await executor.execute_tool(
    ToolCall(
        tool_name="json_validator",
        arguments={"json_string": result1.result}
    )
)
```

### Conditional Tool Usage

```python
if data_type == "json":
    tool_name = "json_validator"
elif data_type == "xml":
    tool_name = "xml_parser"

result = await executor.execute_tool(
    ToolCall(tool_name=tool_name, arguments={"data": data})
)
```

## Testing Tools

```python
import pytest
from weave.tools import Tool, ToolCall

def test_calculator():
    tool = Tool(definition=calculator_def, handler=calculator_func)
    call = ToolCall(tool_name="calculator", arguments={"expression": "2+2"})

    result = asyncio.run(tool.execute(call.arguments))

    assert result.success
    assert result.result["result"] == 4
```

## Next Steps

- Learn about [MCP Integration](mcp.md) for external tools
- Explore [Plugin System](plugins.md) for extending Weave
- See [Examples](../../examples/) for complete tool implementations
