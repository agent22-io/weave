# 🧵 Weave

**Declarative AI agent orchestration framework**

Weave is a framework for building and composing interopable AI agents. Define what you want your agent to be in plain yaml and let weave worry about how to build and run the agent.

## ✨ Why Weave?

- ⚡ **Fast** - Go from idea to working agent workflow quickly
- 🔗 **Interoperable** - Agents work together through declarative composition
- 🎯 **Simple** - Clean YAML configuration
- 🔧 **Extensible** - Custom tools and plugins
- 📊 **Observable** - Track execution, outputs, and token usage

## ✨ Key Features

- **Declarative YAML** - Define agents and workflows in configuration
- **Automatic Orchestration** - Smart dependency resolution and execution ordering
- **Real LLM Integration** - OpenAI and Anthropic API support
- **Secure API Key Management** - Encrypted storage with automatic fallback to environment variables
- **Conversation Sessions** - Save and resume agent conversations with full history
- **Tool Calling** - 9 built-in tools + custom tool support
- **Plugin System** - Built-in plugins for web search, data processing, formatting
- **MCP Integration** - Connect to Model Context Protocol servers
- **Development Mode** - Interactive workflow development with auto-reload
- **Resource Management** - Organize prompts, skills, and knowledge bases

## 📦 Installation

### From Source

```bash
git clone https://github.com/swapkats/weave.git
cd weave
pip install -e .
```

### Setup API Keys

Configure your LLM provider API keys using environment variables:

```bash
# Set API keys via environment
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Optional: OpenRouter for multi-model access
export OPENROUTER_API_KEY="your-key-here"
```

Alternatively, API keys can be stored encrypted in `~/.agent/api_keys.yaml` using the APIKeyManager.

## 🚀 Quick Start

### 1. Initialize a Project

```bash
weave init
```

This creates a `.agent.yaml` file:

```yaml
version: "1.0"

agents:
  researcher:
    model: "gpt-4"
    tools: [web_search]
    outputs: "research_summary"

  writer:
    model: "claude-3-opus"
    inputs: "researcher"
    outputs: "draft_article"

weaves:
  content_pipeline:
    description: "Research and write content"
    agents: [researcher, writer]
```
### 2. Run Interactive Chat

```bash
# Chat with default model
weave run

# Chat with specific agent from config
weave run --agent researcher
```

### 3. Review Execution Plan

```bash
weave plan
```

Output:
```
📊 Execution Plan: content_pipeline

Order  Agent       Model         Inputs      
1      researcher  gpt-4         -           
2      writer      claude-3-opus researcher  

Execution graph:
  researcher → writer

2 agents will be created
```

### 4. Apply Your Workflow

```bash
weave apply
```

## 🛠️ Built-in Tools

Weave includes 9 production-ready tools:

**Math & Text:**
- `calculator` - Evaluate mathematical expressions
- `text_length` - Count characters, words, lines
- `string_formatter` - Template-based string formatting

**Data Processing:**
- `json_validator` - Validate and parse JSON
- `list_operations` - List operations (sort, filter, etc.)

**Web & HTTP:**
- `http_request` - Make HTTP requests (GET, POST, PUT, DELETE)
- `web_search` - Search the web (DuckDuckGo)

**File Operations:**
- `file_read` - Read file contents
- `file_write` - Write content to files
- `file_list` - List directory contents

### Using Tools

```yaml
agents:
  data_agent:
    model: "gpt-4"
    tools:
      - http_request
      - file_read
      - file_write
```

## 🔌 Plugins

Built-in plugins for extended functionality:

- **web_search** - Real web search via DuckDuckGo API
- **openrouter** - Unified LLM access (100+ models)
- **data_cleaner** - Clean and normalize data
- **json_parser** - Parse and validate JSON
- **markdown_formatter** - Format markdown content

### Using Plugins

Plugins are automatically loaded and available to agents:

```yaml
agents:
  agent1:
    model: "gpt-4"
    plugins:
      - web_search
      - markdown_formatter
```

## 🔗 MCP Integration

Connect to Model Context Protocol servers for extended tool access:

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    enabled: true
    
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    enabled: true
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

List MCP servers and tools:

```bash
weave mcp --list
weave mcp --server-tools filesystem
```

## 📖 Commands

### Core Commands

- `weave init` - Initialize new project
- `weave plan` - Preview execution plan
- `weave apply` - Execute workflow
- `weave run` - Interactive agentic chat

### Development

- `weave dev --watch` - Development mode with auto-reload
- `weave state --list` - List execution runs
- `weave inspect <run-id>` - Inspect run details

### Tools & Plugins

- `weave tools` - List available tools
- `weave tools --schema <tool-name>` - View tool schema
- `weave plugins` - List plugins
- `weave mcp` - Manage MCP servers

## 📂 Configuration

### Agent Definition

```yaml
agents:
  agent_name:
    model: "model-name"              # Required
    tools: [tool1, tool2]            # Optional
    plugins: [plugin1]               # Optional
    inputs: "other_agent"            # Optional: dependency
    outputs: "output_key"            # Optional: output name
    model_config:                    # Optional: LLM config
      temperature: 0.7
      max_tokens: 1000
    memory:                          # Optional: conversation memory
      type: "buffer"
      max_messages: 100
    storage:                         # Optional: output storage
      save_outputs: true
```

### Custom Tools

```yaml
tools:
  custom_tool:
    description: "My custom tool"
    category: "custom"
    parameters:
      param1:
        type: "string"
        description: "Parameter description"
        required: true
```

## 📊 Resource Management

Organize agent resources in `.agent/` directory:

```
.agent/
├── prompts/         # System prompts (YAML + markdown)
├── skills/          # Agent skills (YAML)
├── recipes/         # Workflow templates
├── knowledge/       # Knowledge bases
├── rules/           # Agent constraints
├── behaviors/       # Behavioral guidelines
└── sub_agents/      # Nested agents
```

Create resource structure:

```bash
weave resources --create
```

## 📂 Examples

Complete examples with resources:

- **[basic.agent.yaml](examples/basic.agent.yaml)** - Simple pipeline
- **[coding-agent-example/](examples/coding-agent-example/)** - Software development
- **[content-creation-example/](examples/content-creation-example/)** - Blog posts
- **[research-assistant-example/](examples/research-assistant-example/)** - Research & analysis
- **[customer-support-example/](examples/customer-support-example/)** - Support automation
- **[data-processing-example/](examples/data-processing-example/)** - ETL pipelines

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│       CLI Layer (Typer)         │
│  Commands: init, plan, apply    │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│    Parser Layer (PyYAML)        │
│  YAML loading + env substitution│
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Core Layer (Pydantic+NetworkX) │
│  Validation + dependency graph  │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│     Executor (Real LLMs)        │
│  OpenAI + Anthropic + Tools     │
└─────────────────────────────────┘
```

### Key Components

- **CLI** (`src/weave/cli/`) - Typer commands with Rich output
- **Parser** (`src/weave/parser/`) - YAML parsing and env substitution
- **Core** (`src/weave/core/`) - Pydantic models and dependency graph
- **Executor** (`src/weave/runtime/`) - Real LLM execution
- **Tools** (`src/weave/tools/`) - Tool calling system + MCP
- **Plugins** (`src/weave/plugins/`) - Plugin system

## 🤝 Contributing

Contributions welcome! See development setup:

```bash
# Clone and install dev dependencies
git clone https://github.com/weave/weave-cli.git
cd weave-cli
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## 🛣️ Roadmap

### Current: v0.1.0
- ✅ Real LLM execution (OpenAI, Anthropic)
- ✅ 9 built-in tools
- ✅ MCP protocol integration
- ✅ Plugin system
- ✅ Dependency graphs
- ✅ Development mode

### Planned: v0.2.0
- [ ] More LLM providers (Google, Cohere)
- [ ] Advanced memory systems
- [ ] Parallel agent execution
- [ ] Web UI for monitoring
- [ ] Cloud deployment (AWS, GCP)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 📬 Contact

- GitHub Issues: [github.com/weave/weave-cli/issues](https://github.com/weave/weave-cli/issues)
- Documentation: [docs.weave.dev](https://docs.weave.dev)

---

Made with ❤️ by the Weave team
