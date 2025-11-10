# Tool Calling System - Quick Reference

## Key Files at a Glance

### Tool System Core
| File | Purpose | Key Components |
|------|---------|-----------------|
| `src/weave/tools/__init__.py` | Public API exports | Tool, ToolParameter, ToolResult, ToolCall, ToolDefinition, ToolExecutor, MCPClient, MCPServer |
| `src/weave/tools/models.py` | Data models | ParameterType, ToolParameter, ToolDefinition, ToolCall, ToolResult, Tool |
| `src/weave/tools/executor.py` | Tool execution engine | ToolExecutor class with registration, listing, and execution |
| `src/weave/tools/builtin.py` | 9 built-in tools | calculator, text_length, json_validator, string_formatter, list_operations, http_request, file_read, file_write, file_list |
| `src/weave/tools/mcp_client.py` | MCP integration | MCPClient, MCPServer, JSON-RPC communication |

### Runtime Integration
| File | Purpose | Tool-Related Methods |
|------|---------|----------------------|
| `src/weave/runtime/executor.py` | Weave execution engine | _initialize_tools(), _prepare_tools(), _handle_tool_calls() |
| `src/weave/runtime/llm_executor.py` | LLM API calls | _call_openai(), _call_anthropic() (both support tool passing) |

### Configuration
| File | Purpose | Tool-Related Models |
|------|---------|---------------------|
| `src/weave/core/models.py` | Config data models | Agent.tools, CustomToolDef, MCPServerConfig, WeaveConfig |
| `src/weave/parser/config.py` | Config file parsing | load_config(), load_config_from_path() |

### CLI
| File | Purpose | Commands |
|------|---------|----------|
| `src/weave/cli/app.py` | Typer CLI application | `weave tools`, `weave mcp` |

### Documentation
| File | Purpose | Coverage |
|------|---------|----------|
| `docs/guides/tool-calling.md` | Tool calling guide | Built-in tools, custom tools, execution, testing |
| `docs/guides/mcp.md` | MCP integration guide | MCP setup, server configuration, popular servers |

### Examples
| File | Purpose | Demonstrates |
|------|---------|---------------|
| `examples/agent-creator-mcp-example/.weave.yaml` | MCP usage | Tool references in agents |
| `examples/agent-creator-mcp-example/agent_creator_server.py` | MCP server | Building MCP servers |

---

## Tool Definition Class Hierarchy

```
ToolDefinition (tool schema/definition)
├── name: str
├── description: str
├── parameters: List[ToolParameter]
│   └── ToolParameter
│       ├── name: str
│       ├── type: ParameterType (enum)
│       ├── description: str
│       ├── required: bool
│       ├── default: Any
│       ├── enum: List[Any]
│       ├── items: Dict (array schema)
│       └── properties: Dict (object schema)
├── returns: Optional[str]
├── category: str
├── tags: List[str]
└── mcp_server: Optional[str] (external tool marker)

Tool (runtime tool instance)
├── definition: ToolDefinition
└── handler: Optional[Callable]
    └── async def execute(arguments) -> ToolResult

ToolCall (tool invocation request)
├── tool_name: str
├── arguments: Dict[str, Any]
└── call_id: Optional[str]

ToolResult (tool execution result)
├── tool_name: str
├── call_id: Optional[str]
├── success: bool
├── result: Optional[Any]
├── error: Optional[str]
└── execution_time: float
```

---

## Registration Flow

```
ToolExecutor.__init__()
├── _load_builtin_tools()
│   └── get_builtin_tools() → List[Tool]
│       └── register_tool(tool) → tools[tool_name] = tool
└── _load_mcp_tools()
    ├── mcp_client.list_servers()
    └── For each enabled server:
        ├── mcp_client.get_server_tools(server_name)
        └── register_tool(tool) with mcp_server field set
```

---

## Execution Flow

```
Agent Configuration (.weave.yaml)
    ↓
Executor._execute_agent(agent, agent_name)
    ├── agent.tools → List[str] tool names
    ├── _prepare_tools(tool_names) → List[Dict] JSON schemas
    │   └── For each tool_name:
    │       └── tool_executor.get_tool(name)
    │           └── tool_def.to_json_schema()
    │
    └── llm_executor.execute_agent(agent, context, tools)
        ├── _call_openai(tools=schemas)
        │   └── Extract tool_calls from OpenAI response
        │
        └── _call_anthropic(tools=schemas)
            └── Extract tool_use blocks from Anthropic response
                ↓
        Executor._handle_tool_calls(tool_calls)
            └── For each tool_call:
                ├── tool_executor.execute_tool(ToolCall)
                │   ├── Tool.execute(arguments)
                │   │   ├── _validate_arguments()
                │   │   ├── handler(**arguments)
                │   │   └── ToolResult(success=True/False)
                │   │
                │   └── Return ToolResult
                │
                └── Append to results
```

---

## Configuration Examples

### In YAML
```yaml
agents:
  my_agent:
    model: "gpt-4"
    tools: [calculator, json_validator, http_request]

tools:
  custom_math:
    description: "Custom math tool"
    parameters:
      value:
        type: "number"
        required: true

mcp_servers:
  filesystem:
    command: "npx"
    args: ["@modelcontextprotocol/server-filesystem"]
    enabled: true
```

### In Python
```python
from weave.tools import (
    ToolDefinition, ToolParameter, ParameterType,
    Tool, ToolExecutor, ToolCall
)

# Define
definition = ToolDefinition(
    name="my_tool",
    description="Does something",
    parameters=[
        ToolParameter(
            name="input",
            type=ParameterType.STRING,
            required=True
        )
    ]
)

def my_handler(input: str):
    return {"result": input.upper()}

tool = Tool(definition=definition, handler=my_handler)

# Register
executor = ToolExecutor()
executor.register_tool(tool)

# Execute
result = await executor.execute_tool(
    ToolCall(tool_name="my_tool", arguments={"input": "hello"})
)
```

---

## CLI Quick Commands

```bash
# List all tools
weave tools

# Filter by category
weave tools --category math

# Filter by tags
weave tools --tags json,validation

# Show JSON schema for tool
weave tools --schema calculator

# List MCP servers
weave mcp

# Create example MCP config
weave mcp --init

# List tools from specific server
weave mcp --server-tools filesystem

# Add MCP server
weave mcp --add myserver --command "python server.py"

# Remove MCP server
weave mcp --remove myserver
```

---

## Built-in Tools Summary

### Math
- `calculator`: Evaluate math expressions safely

### Text
- `text_length`: Count chars/words/lines
- `string_formatter`: Format strings with variables

### Data
- `json_validator`: Validate and parse JSON
- `list_operations`: Operations on lists (sum, sort, etc.)

### Web
- `http_request`: Make HTTP requests

### Filesystem
- `file_read`: Read file contents
- `file_write`: Write to files
- `file_list`: List directory contents

---

## Key Integration Points

1. **Configuration Loading** (`parser/config.py`)
   - Parses tool and MCP server definitions from YAML
   - Validates against Pydantic models

2. **Tool Registration** (`tools/executor.py`)
   - Loads built-in tools
   - Loads tools from MCP servers
   - Maintains registry by tool name

3. **Tool Preparation** (`runtime/executor.py`)
   - Converts tool definitions to JSON schemas
   - Passes schemas to LLM for context

4. **LLM Integration** (`runtime/llm_executor.py`)
   - Sends tool schemas to OpenAI/Anthropic
   - Extracts tool calls from responses
   - Creates ToolCall objects

5. **Tool Execution** (`tools/executor.py`)
   - Validates arguments
   - Executes handler function
   - Returns ToolResult with metrics

---

## Known Issues

1. **Line 436 in executor.py**: Calls `execute_async()` but method is `execute_tool()`
2. **Sync/Async handlers**: Tool.execute() doesn't handle async handlers properly
3. **Tool validation**: Not validated at config load time, only at execution

---

## Most Important Methods to Understand

1. **ToolExecutor.execute_tool()** - Execute single tool
2. **Executor._prepare_tools()** - Convert to JSON schemas
3. **Executor._handle_tool_calls()** - Process LLM tool calls
4. **LLMExecutor._call_openai/_call_anthropic()** - LLM integration
5. **MCPClient.call_tool()** - Execute MCP server tools
6. **Tool.to_json_schema()** - Convert definition to schema
