# MCP (Model Context Protocol) Integration

Weave integrates with MCP servers to provide agents with access to external tools and data sources. This guide covers configuring and using MCP servers in your workflows.

## What is MCP?

Model Context Protocol (MCP) is a protocol for connecting AI models to external tools and data sources. MCP servers expose tools that agents can use to:

- Access file systems
- Query databases
- Make web requests
- Interact with APIs
- And much more

## Quick Start

### Initialize MCP Configuration

```bash
weave mcp --init
```

This creates `.weave/mcp.yaml` with example server configurations:

```yaml
servers:
  filesystem:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-filesystem"
    description: File system operations (read, write, list)
    enabled: true

  web:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-fetch"
    description: Web fetching and scraping
    enabled: true

  github:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-github"
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
    description: GitHub API integration
    enabled: false
```

### List Configured Servers

```bash
weave mcp
```

Output:
```
┌────────────┬─────────────────────────────┬────────────┬────────────────────┐
│ Name       │ Command                     │ Status     │ Description        │
├────────────┼─────────────────────────────┼────────────┼────────────────────┤
│ filesystem │ npx -y @modelcontext...     │ ✓ enabled  │ File operations    │
│ web        │ npx -y @modelcontext...     │ ✓ enabled  │ Web fetching       │
│ github     │ npx -y @modelcontext...     │ ✗ disabled │ GitHub API         │
└────────────┴─────────────────────────────┴────────────┴────────────────────┘
```

### View Server Tools

```bash
weave mcp --server-tools filesystem
```

Shows tools available from the filesystem server:

```
┌──────────────┬────────────┬─────────────────────────────────┐
│ Name         │ Category   │ Description                     │
├──────────────┼────────────┼─────────────────────────────────┤
│ read_file    │ filesystem │ Read contents of a file         │
│ write_file   │ filesystem │ Write contents to a file        │
│ list_files   │ filesystem │ List files in a directory       │
└──────────────┴────────────┴─────────────────────────────────┘
```

## Managing Servers

### Add a Server

```bash
weave mcp --add myserver --command "python server.py"
```

### Remove a Server

```bash
weave mcp --remove myserver
```

### Edit Configuration

Manually edit `.weave/mcp.yaml`:

```yaml
servers:
  myserver:
    command: python
    args:
      - server.py
      - --port
      - "8080"
    env:
      API_KEY: "${MY_API_KEY}"
    description: My custom MCP server
    enabled: true
```

## Popular MCP Servers

### Filesystem Server

Access local files and directories:

```yaml
filesystem:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-filesystem"]
  description: File system operations
  enabled: true
```

Tools available:
- `read_file` - Read file contents
- `write_file` - Write to files
- `list_files` - List directory contents
- `search_files` - Search for files
- `get_file_info` - Get file metadata

### Web Fetch Server

Fetch and process web content:

```yaml
web:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-fetch"]
  description: Web fetching and scraping
  enabled: true
```

Tools available:
- `fetch_url` - Fetch URL content
- `extract_links` - Extract links from HTML
- `scrape_page` - Scrape structured data

### GitHub Server

Interact with GitHub API:

```yaml
github:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_TOKEN: "${GITHUB_TOKEN}"
  description: GitHub API integration
  enabled: true
```

Tools available:
- `get_repository` - Get repository information
- `list_issues` - List repository issues
- `create_issue` - Create a new issue
- `get_pull_request` - Get PR details
- `search_code` - Search code in repositories

### Database Server

Query databases:

```yaml
database:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-database"]
  env:
    DATABASE_URL: "${DATABASE_URL}"
  description: Database queries
  enabled: true
```

Tools available:
- `query_database` - Execute SQL queries
- `list_tables` - List database tables
- `describe_table` - Get table schema
- `execute_statement` - Run SQL statements

## Using MCP Tools in Agents

Once configured, MCP tools are automatically available to agents:

```yaml
agents:
  file_processor:
    model: "gpt-4"
    tools:
      - read_file      # From filesystem MCP server
      - write_file     # From filesystem MCP server
      - fetch_url      # From web MCP server
    outputs: "processed_files"
```

## Environment Variables

MCP servers often need credentials. Use environment variables:

### In Configuration

```yaml
servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
      GITHUB_ORG: "${GITHUB_ORG}"
```

### In Shell

```bash
export GITHUB_TOKEN="ghp_xxxxx"
export GITHUB_ORG="my-org"
weave apply
```

### In .env File

Create `.env` in your project:

```bash
GITHUB_TOKEN=ghp_xxxxx
GITHUB_ORG=my-org
DATABASE_URL=postgresql://localhost/mydb
```

## Creating Custom MCP Servers

### Python Example

```python
from mcp import MCPServer, Tool

server = MCPServer("my-custom-server")

@server.tool("greet")
def greet(name: str) -> str:
    """Greet a person."""
    return f"Hello, {name}!"

@server.tool("calculate")
def calculate(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)  # Use safe evaluation in production!

if __name__ == "__main__":
    server.run()
```

### Node.js Example

```javascript
const { MCPServer } = require('@modelcontextprotocol/sdk');

const server = new MCPServer('my-custom-server');

server.tool('greet', {
  description: 'Greet a person',
  parameters: {
    name: { type: 'string', description: 'Person name' }
  },
  handler: async ({ name }) => {
    return `Hello, ${name}!`;
  }
});

server.listen();
```

### Register in Weave

```yaml
servers:
  my_server:
    command: python
    args: ["server.py"]
    description: My custom tools
    enabled: true
```

## Advanced Configuration

### Multiple Instances

Run multiple instances of the same server:

```yaml
servers:
  github_personal:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${PERSONAL_GITHUB_TOKEN}"
    description: Personal GitHub
    enabled: true

  github_work:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${WORK_GITHUB_TOKEN}"
      GITHUB_ORG: "my-company"
    description: Work GitHub
    enabled: true
```

### Server Options

```yaml
servers:
  database:
    command: python
    args:
      - mcp_server.py
      - --host
      - localhost
      - --port
      - "5432"
    env:
      DB_HOST: "${DB_HOST}"
      DB_PORT: "${DB_PORT}"
      DB_NAME: "${DB_NAME}"
    description: PostgreSQL database
    enabled: true
```

### Conditional Enablement

Enable/disable servers for different environments:

```yaml
# Development
servers:
  database:
    enabled: true
  production_api:
    enabled: false

# Production
servers:
  database:
    enabled: false
  production_api:
    enabled: true
```

## Tool Discovery

List all tools from all enabled servers:

```bash
weave tools
```

Filter MCP tools:

```bash
# Show only filesystem tools
weave mcp --server-tools filesystem

# Show only web tools
weave mcp --server-tools web
```

## Troubleshooting

### Server Not Starting

Check the command is correct:

```bash
# Test command manually
npx -y @modelcontextprotocol/server-filesystem
```

### Missing Tools

Verify server is enabled:

```bash
weave mcp
```

Enable if needed:

```yaml
servers:
  myserver:
    enabled: true  # Set to true
```

### Authentication Errors

Check environment variables are set:

```bash
echo $GITHUB_TOKEN
echo $DATABASE_URL
```

### Tool Not Available

List server tools:

```bash
weave mcp --server-tools servername
```

## Best Practices

### 1. Security

```yaml
# Good - Use environment variables
env:
  API_KEY: "${API_KEY}"

# Bad - Hardcode secrets
env:
  API_KEY: "sk-1234567890"
```

### 2. Organization

```yaml
# Group related servers
servers:
  # Data sources
  database:
    ...
  redis:
    ...

  # External APIs
  github:
    ...
  slack:
    ...

  # File operations
  filesystem:
    ...
  s3:
    ...
```

### 3. Descriptions

```yaml
# Good - Clear description
description: GitHub API for repository management and issue tracking

# Bad - Vague description
description: GitHub stuff
```

### 4. Naming

```yaml
# Good - Descriptive names
github_personal:
  ...
github_work:
  ...

# Bad - Generic names
server1:
  ...
server2:
  ...
```

### 5. Testing

Test servers individually:

```bash
# Test server starts
npx -y @modelcontextprotocol/server-filesystem

# Test server tools
weave mcp --server-tools filesystem

# Test in agent
weave tools --schema read_file
```

## Version 2.0 Features (Coming Soon)

The v2.0 release will include:

- **Real MCP Protocol** - Full MCP protocol implementation
- **Server Health Checks** - Monitor server availability
- **Tool Caching** - Cache tool results for performance
- **Batch Tool Calls** - Execute multiple tools in parallel
- **Server Discovery** - Auto-discover available MCP servers
- **Tool Versioning** - Manage multiple versions of tools

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Building MCP Servers](https://docs.modelcontextprotocol.io)
- [Weave Tool Calling Guide](tool-calling.md)

## Examples

See `examples/mcp_example/` for complete examples:

- Setting up MCP servers
- Using MCP tools in agents
- Creating custom MCP servers
- Multi-server workflows
