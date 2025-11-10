# Tool Calling and MCP Examples

This guide demonstrates how to use tools and MCP (Model Context Protocol) in Weave.

## Overview

Weave provides three ways to extend agent capabilities:

1. **Built-in Tools** - Ready-to-use tools for common tasks
2. **Custom Tools** - Define your own tools in YAML
3. **MCP Servers** - External tool providers via Model Context Protocol

## Examples

### 1. Tool Calling Example (`tool-calling.weave.yaml`)

Demonstrates using built-in and custom tools.

**Features:**
- Built-in tools (calculator, text_length, json_validator, etc.)
- Custom tool definitions in YAML
- Multi-agent pipeline with tool usage

**Run it:**
```bash
# Preview the workflow
weave plan --config examples/tool-calling.weave.yaml

# Execute
weave apply --config examples/tool-calling.weave.yaml

# See available tools
weave tools
```

**Custom Tools in Config:**
```yaml
tools:
  email_sender:
    description: Send emails to recipients
    category: communication
    parameters:
      to:
        type: string
        description: Email recipient address
        required: true
      subject:
        type: string
        description: Email subject line
        required: true
```

### 2. MCP Integration Example (`mcp-integration.weave.yaml`)

Demonstrates using external MCP servers.

**Prerequisites:**
```bash
# 1. Initialize MCP configuration
weave mcp --init

# 2. List available MCP servers
weave mcp

# 3. Enable servers you need in .weave/mcp.yaml
# 4. Set environment variables (e.g., export GITHUB_TOKEN=xxx)
```

**Features:**
- Filesystem operations (read_file, write_file, list_files)
- Web requests (fetch_url, extract_links)
- GitHub integration (get_repository, list_issues, search_code)
- Database queries (query_database, list_tables)

**Run it:**
```bash
# Check MCP servers status
weave mcp

# See tools from specific server
weave mcp --server-tools filesystem

# Preview workflow
weave plan --config examples/mcp-integration.weave.yaml

# Execute
weave apply --config examples/mcp-integration.weave.yaml
```

## Built-in Tools Reference

List all built-in tools:
```bash
weave tools
```

### Math Tools
- **calculator** - Evaluate mathematical expressions
  ```yaml
  tools:
    - calculator
  ```

### Text Tools
- **text_length** - Count characters, words, and lines
- **string_formatter** - Format strings with template variables
  ```yaml
  tools:
    - text_length
    - string_formatter
  ```

### Data Tools
- **json_validator** - Validate and parse JSON
- **list_operations** - Perform list operations (append, count, sum, sort, etc.)
  ```yaml
  tools:
    - json_validator
    - list_operations
  ```

View detailed tool schema:
```bash
weave tools --schema calculator
weave tools --schema json_validator
```

## Custom Tool Definitions

Define custom tools in your `.weave.yaml`:

```yaml
tools:
  my_custom_tool:
    description: What this tool does
    category: general
    tags: [tag1, tag2]
    parameters:
      param1:
        type: string
        description: First parameter
        required: true
      param2:
        type: number
        description: Second parameter
        required: false
        default: 42
```

### Parameter Types

- `string` - Text values
- `number` - Floating point numbers
- `integer` - Whole numbers
- `boolean` - true/false
- `array` - Lists
- `object` - Dictionaries

### Parameter Options

```yaml
parameters:
  level:
    type: string
    description: Log level
    required: true
    default: info
    enum: [debug, info, warning, error]  # Restrict to specific values
```

## MCP Server Configuration

### Initialize MCP

```bash
weave mcp --init
```

This creates `.weave/mcp.yaml` with example servers:

```yaml
servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem"]
    description: File system operations
    enabled: true

  web:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-fetch"]
    description: Web fetching
    enabled: true

  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
    description: GitHub API integration
    enabled: false  # Enable and set GITHUB_TOKEN to use
```

### Manage MCP Servers

```bash
# List configured servers
weave mcp

# Add a new server
weave mcp --add myserver --command "python server.py"

# Remove a server
weave mcp --remove myserver

# View tools from a server
weave mcp --server-tools filesystem
```

### Enable GitHub Server

1. Generate a GitHub token at https://github.com/settings/tokens
2. Set environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_xxxxx
   ```
3. Enable in `.weave/mcp.yaml`:
   ```yaml
   github:
     enabled: true
   ```
4. List available tools:
   ```bash
   weave mcp --server-tools github
   ```

## Agent Configuration with Tools

### Basic Tool Usage

```yaml
agents:
  my_agent:
    model: "gpt-4"
    tools:
      - calculator
      - text_length
      - json_validator
```

### Mixed Built-in and Custom Tools

```yaml
tools:
  custom_tool:
    description: My custom tool
    # ...

agents:
  my_agent:
    model: "gpt-4"
    tools:
      - calculator      # Built-in
      - custom_tool     # Custom (defined above)
      - read_file       # MCP (from filesystem server)
```

### Multiple Agents with Different Tools

```yaml
agents:
  researcher:
    model: "gpt-4"
    tools:
      - fetch_url       # Web MCP
      - json_validator  # Built-in

  analyst:
    model: "claude-3-opus"
    inputs: "researcher"
    tools:
      - calculator      # Built-in
      - list_operations # Built-in
      - query_database  # Database MCP

  writer:
    model: "gpt-4"
    inputs: "analyst"
    tools:
      - string_formatter  # Built-in
      - write_file        # Filesystem MCP
```

## Tool Categories

Tools are organized by category for easy filtering:

```bash
# View tools by category
weave tools --category math
weave tools --category text
weave tools --category data
weave tools --category web
weave tools --category file
```

**Categories:**
- `math` - Mathematical operations
- `text` - Text processing and formatting
- `data` - Data manipulation and validation
- `web` - Web requests and scraping
- `file` - File system operations
- `api` - External API integrations
- `database` - Database queries
- `communication` - Email, messaging, etc.

## Best Practices

### 1. Tool Selection

Choose appropriate tools for each agent:

```yaml
# Good - Focused tool sets
data_processor:
  tools: [calculator, list_operations, json_validator]

web_scraper:
  tools: [fetch_url, extract_links, text_length]

# Avoid - Too many unrelated tools
mixed_agent:
  tools: [calculator, fetch_url, query_database, email_sender]  # Unfocused
```

### 2. Custom Tool Organization

Group related custom tools:

```yaml
tools:
  # Email tools
  send_email:
    description: Send email
    category: communication
    # ...

  parse_email:
    description: Parse email content
    category: communication
    # ...

  # Data tools
  validate_schema:
    description: Validate data schema
    category: data
    # ...
```

### 3. MCP Server Management

```yaml
# Development: Enable local/mock servers
servers:
  filesystem:
    enabled: true
  database_dev:
    enabled: true
  production_api:
    enabled: false

# Production: Enable production servers
servers:
  filesystem:
    enabled: false
  database_prod:
    enabled: true
  production_api:
    enabled: true
```

### 4. Environment Variables

Use environment variables for sensitive data:

```yaml
servers:
  github:
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"   # Read from environment
      GITHUB_ORG: "${GITHUB_ORG}"

  database:
    env:
      DB_HOST: "${DB_HOST}"
      DB_PASSWORD: "${DB_PASSWORD}"
```

```bash
# Set in shell or .env file
export GITHUB_TOKEN=ghp_xxxxx
export GITHUB_ORG=my-org
export DB_HOST=localhost
export DB_PASSWORD=secret
```

## Troubleshooting

### Tool Not Found

```bash
# Check if tool exists
weave tools

# Check specific tool schema
weave tools --schema tool_name

# For MCP tools, check server status
weave mcp
weave mcp --server-tools servername
```

### MCP Server Issues

```bash
# Verify server is enabled
weave mcp

# Check environment variables
echo $GITHUB_TOKEN
echo $DATABASE_URL

# Test server command manually
npx -y @modelcontextprotocol/server-filesystem
```

### Tool Execution Errors

Enable verbose output:

```bash
weave apply --verbose --config examples/tool-calling.weave.yaml
```

## Version Support

### v1.0 (Current)
- ✅ Built-in tools
- ✅ Custom tool definitions
- ✅ MCP server configuration
- ✅ Mock tool execution
- ✅ Tool schema validation

### v2.0 (Planned)
- 🔄 Real tool execution during LLM calls
- 🔄 Tool result integration into agent context
- 🔄 Parallel tool calls
- 🔄 Tool caching
- 🔄 Dynamic tool loading

## Additional Resources

- [Tool Calling Guide](../docs/guides/tool-calling.md) - Complete guide
- [MCP Integration Guide](../docs/guides/mcp.md) - MCP documentation
- [MCP Specification](https://modelcontextprotocol.io) - Official MCP docs
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers) - Pre-built servers

## Questions?

- Check documentation in `docs/guides/`
- Open an issue on GitHub
- View examples in `examples/`
