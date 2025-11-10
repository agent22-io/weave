# Weave Tool Calling System - Complete Analysis

## Executive Summary

The Weave framework implements a comprehensive tool calling system that enables AI agents to invoke external functions and services. The system integrates:
1. Built-in tools for common operations
2. Custom tool definitions via YAML configuration
3. MCP (Model Context Protocol) servers for external tool providers
4. Seamless LLM integration with OpenAI and Anthropic

---

## 1. Tool Calling Implementation Locations

### Core Files Structure
```
/home/user/weave/src/weave/tools/
├── __init__.py              # Public API exports
├── models.py                # Tool models and schemas
├── executor.py              # Tool execution engine
├── builtin.py               # Built-in tool implementations
└── mcp_client.py            # MCP server integration
```

### Key Integration Points
- **Runtime Executor**: `/home/user/weave/src/weave/runtime/executor.py` (lines 98-125)
- **LLM Executor**: `/home/user/weave/src/weave/runtime/llm_executor.py` (lines 217-422)
- **Core Models**: `/home/user/weave/src/weave/core/models.py` (defines Agent tools, CustomToolDef)
- **CLI**: `/home/user/weave/src/weave/cli/app.py` (tools and mcp commands)

---

## 2. Tool Definition and Models

### Core Tool Model Classes (models.py)

#### ParameterType Enum
```python
ParameterType.STRING     # Text strings
ParameterType.NUMBER     # Floating point numbers
ParameterType.INTEGER    # Whole numbers
ParameterType.BOOLEAN    # true/false
ParameterType.ARRAY      # Lists
ParameterType.OBJECT     # Dictionaries
```

#### ToolParameter (BaseModel)
- `name`: Parameter name
- `type`: ParameterType
- `description`: Parameter description
- `required`: Whether parameter is required
- `default`: Default value
- `enum`: Allowed values
- `items`: Array item schema (for array types)
- `properties`: Object properties (for object types)

#### ToolDefinition (BaseModel)
```python
class ToolDefinition(BaseModel):
    name: str                              # Unique tool identifier
    description: str                       # Tool description
    parameters: List[ToolParameter]        # Input parameters
    returns: Optional[str]                 # Return type description
    category: str = "general"              # Tool category
    tags: List[str]                        # Searchable tags
    mcp_server: Optional[str]              # MCP server if external
    
    def to_json_schema() -> Dict:          # Converts to JSON Schema format
```

#### ToolCall (BaseModel)
```python
class ToolCall(BaseModel):
    tool_name: str                         # Name of tool to call
    arguments: Dict[str, Any]              # Tool arguments
    call_id: Optional[str]                 # Unique call identifier
```

#### ToolResult (BaseModel)
```python
class ToolResult(BaseModel):
    tool_name: str                         # Tool that was executed
    call_id: Optional[str]                 # Matching call_id
    success: bool                          # Execution success flag
    result: Optional[Any]                  # Tool output
    error: Optional[str]                   # Error message if failed
    execution_time: float                  # Execution duration in seconds
```

#### Tool (BaseModel)
```python
class Tool(BaseModel):
    definition: ToolDefinition             # Tool schema/definition
    handler: Optional[Any]                 # Callable function
    
    async def execute(arguments) -> ToolResult:
        # Validates arguments, executes handler, returns result
```

---

## 3. Tool Registration and Loading

### ToolExecutor Class (executor.py)

**Primary Responsibility**: Manages tool registry and execution

**Key Methods**:
```python
class ToolExecutor:
    def __init__(mcp_config_path: Optional[Path] = None):
        self.tools: Dict[str, Tool] = {}
        self.mcp_client = MCPClient(mcp_config_path)
        self._load_builtin_tools()      # Load built-in tools
        self._load_mcp_tools()          # Load MCP server tools
    
    def register_tool(tool: Tool) -> None:
        # Register a tool for execution
    
    def register_tool_function(definition, handler) -> None:
        # Register with callable handler
    
    def get_tool(tool_name: str) -> Optional[Tool]:
        # Retrieve tool by name
    
    def list_tools(category=None, tags=None) -> List[ToolDefinition]:
        # Query available tools with filters
    
    async def execute_tool(tool_call: ToolCall) -> ToolResult:
        # Execute single tool call
    
    async def execute_tools(tool_calls: List[ToolCall]) -> List[ToolResult]:
        # Execute multiple tool calls
    
    def get_tool_schemas(tool_names: List[str]) -> List[Dict]:
        # Get JSON schemas for LLM
```

---

## 4. Built-in Tools

### Available Built-in Tools (builtin.py)

**Math Category**:
- `calculator`: Evaluate mathematical expressions safely

**Text Category**:
- `text_length`: Count characters, words, and lines
- `string_formatter`: Format strings with template variables

**Data Category**:
- `json_validator`: Validate and parse JSON strings
- `list_operations`: Perform list operations (append, count, sum, sort, reverse, unique)

**Web Category**:
- `http_request`: Make HTTP requests (GET, POST, PUT, DELETE, PATCH)

**Filesystem Category**:
- `file_read`: Read file contents
- `file_write`: Write content to files
- `file_list`: List files in directory with pattern matching

**Each tool includes**:
- Implementation function with parameter validation
- ToolDefinition with complete schema
- Error handling and structured responses

### Example: Calculator Tool
```python
def calculator(expression: str) -> Dict[str, Any]:
    """Safely evaluate mathematical expressions using AST."""
    # Implementation using ast module for safety
    
Tool(
    definition=ToolDefinition(
        name="calculator",
        description="Evaluate mathematical expressions safely",
        parameters=[ToolParameter(name="expression", ...)],
        category="math",
        tags=["calculator", "math", "arithmetic"]
    ),
    handler=calculator
)
```

---

## 5. Tool Configuration

### Configuration in YAML (.weave.yaml)

#### Agent Tool Definition
```yaml
agents:
  my_agent:
    model: "gpt-4"
    tools:                        # List of tool names
      - calculator
      - json_validator
      - http_request
    outputs: "result"
```

#### Custom Tool Definition
```yaml
tools:
  my_custom_tool:
    description: "What this tool does"
    category: "custom"            # Tool category
    tags: ["custom", "special"]   # Searchable tags
    parameters:
      param_name:
        type: "string"            # Parameter type
        description: "Param description"
        required: true            # Is required?
        default: null             # Default value
        enum: [...]               # Allowed values
```

#### MCP Server Configuration
```yaml
mcp_servers:
  my_server:
    command: "python"             # Command to start server
    args: ["server.py"]           # Command arguments
    env:
      API_KEY: "${API_KEY}"       # Environment variables
    description: "Server description"
    enabled: true                 # Enable/disable server
```

### Configuration Models (core/models.py)

```python
class ToolParameterDef(BaseModel):
    type: str                      # Parameter type
    description: str = ""
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None

class CustomToolDef(BaseModel):
    description: str
    parameters: Dict[str, ToolParameterDef]
    category: str = "general"
    tags: List[str] = []
    handler: Optional[str]         # Python module path

class MCPServerConfig(BaseModel):
    command: str                   # Start command
    args: List[str]                # Command args
    env: Dict[str, str]            # Environment vars
    description: str
    enabled: bool = True

class WeaveConfig(BaseModel):
    tools: Dict[str, CustomToolDef]
    mcp_servers: Dict[str, MCPServerConfig]
    agents: Dict[str, Agent]       # Agents can reference tools
```

---

## 6. LLM Integration and Tool Calling

### LLM Executor Tool Handling (llm_executor.py)

**Tool Schema Preparation** (lines 217-224):
```python
# Tools provided to LLM as JSON schemas
if agent.tools:
    parts.append(f"You have access to the following tools: {', '.join(agent.tools)}")
```

**OpenAI Integration** (lines 250-327):
```python
async def _call_openai(..., tools: Optional[List[Dict]] = None):
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    if tools:
        kwargs["tools"] = tools        # Add JSON schemas
        kwargs["tool_choice"] = "auto"
    
    response = self.openai_client.chat.completions.create(**kwargs)
    
    # Extract tool calls from response
    if hasattr(message, "tool_calls") and message.tool_calls:
        tool_calls = [
            {
                "id": tc.id,
                "name": tc.function.name,
                "arguments": tc.function.arguments,
            }
            for tc in message.tool_calls
        ]
```

**Anthropic Integration** (lines 329-422):
```python
async def _call_anthropic(..., tools: Optional[List[Dict]] = None):
    # Anthropic requires tools in separate param
    if tools:
        kwargs["tools"] = tools
    
    response = self.anthropic_client.messages.create(**kwargs)
    
    # Extract tool uses from content blocks
    for block in response.content:
        if block.type == "tool_use":
            tool_calls.append({
                "id": block.id,
                "name": block.name,
                "arguments": block.input,
            })
```

---

## 7. Tool Execution in Runtime

### Executor Flow (runtime/executor.py)

**Tool Preparation** (lines 411-420):
```python
async def _prepare_tools(self, tool_names: List[str]) -> List[Dict]:
    """Convert tool definitions to JSON schemas for LLM."""
    tools = []
    for tool_name in tool_names:
        tool_def = self.tool_executor.get_tool(tool_name)
        if tool_def:
            tools.append(tool_def.to_json_schema())
    return tools if tools else None
```

**Agent Execution with Tools** (lines 327-409):
```python
async def _execute_agent(self, agent, agent_name, dry_run):
    # Get tools for agent
    tools = None
    if agent.tools and self.tool_executor:
        tools = await self._prepare_tools(agent.tools)
    
    # Call LLM with tools
    llm_response = await self.llm_executor.execute_agent(
        agent, context, tools
    )
    
    # Handle tool calls if present
    if llm_response.tool_calls:
        final_response = await self._handle_tool_calls(
            agent, llm_response, context
        )
```

**Tool Call Execution** (lines 422-444):
```python
async def _handle_tool_calls(self, agent, llm_response, context):
    tool_results = []
    
    for tool_call in llm_response.tool_calls:
        if self.verbose:
            self.console.print(f"Calling tool: {tool_call['name']}")
        
        # Execute the tool
        result = await self.tool_executor.execute_tool(
            ToolCall(
                tool_name=tool_call["name"],
                arguments=tool_call.get("arguments", {})
            )
        )
        
        tool_results.append(result)
    
    return llm_response
```

---

## 8. MCP (Model Context Protocol) Integration

### MCPClient Class (mcp_client.py)

**MCP Server Configuration**:
```python
@dataclass
class MCPServer:
    name: str
    command: str               # Command to start server
    args: List[str]           # Command arguments
    env: Dict[str, str]       # Environment variables
    enabled: bool = True
    description: str = ""
```

**Key Methods**:
```python
class MCPClient:
    def __init__(weave_config: Optional[WeaveConfig] = None):
        # Load MCP servers from config
        self.servers: Dict[str, MCPServer]
        self.processes: Dict[str, subprocess.Popen]
    
    def list_servers() -> List[MCPServer]:
        # List all configured servers
    
    def start_server(server_name: str) -> bool:
        # Start MCP server process via stdio
        # Send initialization request
    
    def get_server_tools(server_name: str) -> List[ToolDefinition]:
        # Query available tools from server
        # Parses tools/list response
    
    async def call_tool(server_name, tool_name, arguments) -> ToolResult:
        # Execute tool on MCP server
        # Sends tools/call request via stdio
```

**MCP Protocol Flow**:
1. Server starts as subprocess with stdio communication
2. Client sends `initialize` request with client info
3. Client sends `tools/list` to discover tools
4. Client sends `tools/call` to execute tools
5. Responses parsed as JSON-RPC 2.0

**MCP Tool Integration**:
- Tools from MCP servers are loaded as ToolDefinitions
- Marked with `mcp_server` field to identify external origin
- Dynamically registered in ToolExecutor
- Executed differently than built-in tools

---

## 9. CLI Commands for Tool Management

### `weave tools` Command
```bash
weave tools                              # List all tools
weave tools --category math              # Filter by category
weave tools --tags "json,parsing"        # Filter by tags
weave tools --schema calculator          # Show JSON schema
```

**Implementation** (cli/app.py, lines 388-450):
- Loads ToolExecutor
- Lists/filters tools by category and tags
- Displays tools in formatted table
- Shows JSON schema for specific tools

### `weave mcp` Command
```bash
weave mcp                                # List MCP servers
weave mcp --init                         # Create example config
weave mcp --server-tools filesystem      # Show server's tools
weave mcp --add myserver --command "..."  # Add new server
weave mcp --remove myserver              # Remove server
```

**Implementation** (cli/app.py, lines 453-550+):
- Manages MCP server configurations
- Lists configured servers and their tools
- Enables/disables servers
- Creates example configurations

---

## 10. Test Coverage

### Test Files
- `/home/user/weave/tests/test_config_behavior.py` - Configuration loading
  - Tests tool configuration parsing (lines 34-62)
  - Tests custom tool definitions
  - Tests configuration validation

**Example Test**:
```python
def test_config_with_tools_loads_correctly(self):
    config_content = """
tools:
  custom_tool:
    description: "A custom tool"
    parameters:
      param1:
        type: "string"
        required: true

agents:
  agent1:
    model: "gpt-4"
    tools: [custom_tool, calculator]
"""
    config = load_config(config_content)
    assert "custom_tool" in config.tools
    assert "calculator" in config.agents["agent1"].tools
```

---

## 11. Recent Changes and Evolution

### Git Commit History Related to Tool Calling
```
769b326 feat: Add tool calling and MCP integration      # Original implementation
9854c76 feat: Add comprehensive plugin system           # Plugin integration
4f59088 feat: Add capabilities, testing, CI/CD          # Expanded test coverage
2ebbc6c feat: Implement V2 with real LLM execution       # LLM integration
3ee5b15 feat: Complete v1 refactoring                   # Tool system matured
7af73dd feat: Implement agent memory system              # Memory with tools
```

### Key Milestones
1. Initial tool calling and MCP integration
2. Plugin system for tool pre/post-processing
3. Real LLM API integration (OpenAI, Anthropic)
4. Comprehensive testing framework
5. Agent memory system integration
6. Memory with tool calling support

---

## 12. Documentation Files

### Key Documentation
- `/home/user/weave/docs/guides/tool-calling.md` - Complete tool calling guide
- `/home/user/weave/docs/guides/mcp.md` - MCP integration guide
- `/home/user/weave/docs/guides/plugins.md` - Plugin system guide
- `/home/user/weave/docs/reference/configuration.md` - Configuration reference

### Tool-Related Examples
- `/home/user/weave/examples/agent-creator-mcp-example/` - MCP server example
- `/home/user/weave/examples/basic.weave.yaml` - Basic tool configuration

---

## 13. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Weave Agent System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Agent Configuration (.weave.yaml)        │  │
│  │  - agents: [list of agents with tools]               │  │
│  │  - tools: [custom tool definitions]                  │  │
│  │  - mcp_servers: [MCP server configs]                 │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │         Executor (runtime/executor.py)               │  │
│  │  - Initialize ToolExecutor                           │  │
│  │  - _prepare_tools() → JSON schemas                   │  │
│  │  - _execute_agent() → Call LLM with tools            │  │
│  │  - _handle_tool_calls() → Execute called tools       │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │       LLM Executor (runtime/llm_executor.py)         │  │
│  │  - _call_openai() → OpenAI with tools                │  │
│  │  - _call_anthropic() → Anthropic with tools          │  │
│  │  - Extract tool_calls from LLM response              │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │       Tool Executor (tools/executor.py)              │  │
│  │  - register_tool()                                   │  │
│  │  - list_tools(category, tags)                        │  │
│  │  - execute_tool(ToolCall) → ToolResult              │  │
│  └────┬─────────────────────────┬──────────────────────┘  │
│       │                         │                          │
│   ┌───▼────────┐         ┌────▼────────────┐              │
│   │  Built-in  │         │  MCP Client      │              │
│   │  Tools     │         │  (tools/mcp_    │              │
│   │            │         │   client.py)     │              │
│   │ ToolResult │         │                  │              │
│   │ Models     │         │ - start_server()│              │
│   │            │         │ - get_tools()   │              │
│   │ - calc     │         │ - call_tool()   │              │
│   │ - json_val │         │                  │              │
│   │ - http_req │         │ → MCP Servers   │              │
│   └────────────┘         │   (external)     │              │
│                           └──────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 14. Known Issues and Notes

### Potential Issues Found
1. **Executor mismatch**: `executor.py` line 436 calls `execute_async()` method but `ToolExecutor` only defines `execute_tool()` as async method
   - Should be: `await self.tool_executor.execute_tool(ToolCall(...))`

2. **Tool validation timing**: Tool references in agent config are not validated at load time
   - Validation happens at execution time instead
   - This allows for dynamic tool discovery from MCP servers

3. **Async handling**: Tool handlers can be sync or async, but implementation doesn't differentiate
   - `Tool.execute()` method calls handler directly without checking if it's a coroutine
   - May need: `if asyncio.iscoroutine(result): result = await result`

---

## 15. Complete Feature Summary

### Tool Definition Features
✓ Parameter validation (required, types, enums)
✓ JSON Schema generation for LLM context
✓ Categories and tags for organization
✓ Default values and optional parameters
✓ Complex types (arrays, objects)
✓ Custom descriptions for each parameter

### Tool Execution Features
✓ Single and batch tool execution
✓ Execution timing and performance metrics
✓ Error handling and structured error responses
✓ Argument validation before execution
✓ Tool discovery by category and tags

### LLM Integration Features
✓ OpenAI function calling
✓ Anthropic tool use
✓ Automatic tool schema formatting
✓ Tool call extraction from LLM responses
✓ Temperature and token limit control

### MCP Integration Features
✓ Dynamic server startup
✓ Tool discovery from MCP servers
✓ Tool execution via MCP protocol
✓ Environment variable support
✓ Enable/disable servers per config
✓ Multiple MCP server support

### Configuration Features
✓ YAML-based tool definitions
✓ Tool assignment to agents
✓ MCP server configuration
✓ Custom tool implementation references
✓ Parameter schema in YAML
✓ Tool categories and tags

### CLI Features
✓ List available tools
✓ Filter tools by category/tags
✓ Show JSON schema for tools
✓ List MCP servers
✓ View tools from specific servers
✓ Add/remove MCP servers
✓ Create example configurations

---

## Conclusion

The Weave tool calling system is a well-architected, extensible framework that:

1. **Provides Built-in Tools** for common operations (math, text, data, web, filesystem)
2. **Supports Custom Tools** via YAML configuration with full parameter schema
3. **Integrates with LLMs** (OpenAI, Anthropic) for intelligent tool selection
4. **Leverages MCP** for external tool providers and extensibility
5. **Maintains Type Safety** through Pydantic models and parameter validation
6. **Enables Discovery** with categories, tags, and schema introspection
7. **Handles Execution** with error handling, timing, and structured results
8. **Persists Configuration** via YAML with environment variable support

The system is production-ready with comprehensive documentation, example implementations, and test coverage.
