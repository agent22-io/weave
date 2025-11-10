# 🧵 Weave

**Declarative agent orchestration framework**

Weave allows you to define and compose AI agents using YAML configuration files and execute them with a simple, elegant CLI. Think of it as convention over config for composing AI agents.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎯 **Declarative Configuration** - Define agents and workflows in clean YAML
- 🔗 **Dependency Management** - Automatic dependency resolution and execution ordering
- 📊 **Beautiful CLI** - Professional UX with rich terminal output
- 🔍 **Validation** - Schema validation with clear error messages
- 🎨 **Visualization** - ASCII and Mermaid graph generation
- 🪝 **Extensible** - Hook system for custom execution (v2: real LLM calls)
- 🧪 **Mock Execution** - Test workflows without API calls (v1)
- 🔧 **Tool Calling** - Built-in and custom tools with JSON schema validation
- 🌐 **MCP Integration** - Connect to Model Context Protocol servers for external tools
- 🔌 **Plugin System** - Built-in and custom plugins for extending agent capabilities
- 📁 **Resource Management** - Organize prompts, skills, and knowledge bases in files

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/weave/weave-cli.git
cd weave-cli

# Install dependencies
pip install -e .

# Verify installation
weave --version
```

### Using pip (coming soon)

```bash
pip install weave-cli
```

## 🚀 Quick Start

### 1. Initialize a Project

```bash
weave init
```

This creates a `.weave.yaml` file with example agents:

```yaml
version: "1.0"

agents:
  researcher:
    model: "gpt-4"
    tools: [web_search, summarizer]
    outputs: "research_summary"

  writer:
    model: "claude-3-opus"
    tools: [text_generator]
    inputs: "researcher"  # Depends on researcher
    outputs: "draft_article"

  editor:
    model: "gpt-4"
    tools: [grammar_checker]
    inputs: "writer"
    outputs: "final_article"

weaves:
  content_pipeline:
    description: "Research, write, and edit content"
    agents: [researcher, writer, editor]
```

### 2. Preview the Execution Plan

```bash
weave plan
```

Output:
```
📊 Execution Plan: content_pipeline

┏━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Order ┃ Agent      ┃ Model         ┃ Tools      ┃ Inputs     ┃
┡━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ researcher │ gpt-4         │ web_search │ -          │
│ 2     │ writer     │ claude-3-opus │ text_gen.. │ researcher │
│ 3     │ editor     │ gpt-4         │ grammar_.. │ writer     │
└───────┴────────────┴───────────────┴────────────┴────────────┘

Execution graph:
  researcher → writer → editor

3 agents will be executed.
```

### 3. Execute the Workflow

```bash
weave apply
```

Output:
```
🚀 Applying weave: content_pipeline

Executing agents in order:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/3] researcher (gpt-4)
  ⚙️  Running with tools: web_search, summarizer
  ⏱️  Execution time: 1.2s
  ✅ Output: research_summary

[2/3] writer (claude-3-opus)
  📥 Input from: researcher
  ⚙️  Running with tools: text_generator
  ⏱️  Execution time: 2.1s
  ✅ Output: draft_article

[3/3] editor (gpt-4)
  📥 Input from: writer
  ⚙️  Running with tools: grammar_checker
  ⏱️  Execution time: 0.9s
  ✅ Output: final_article

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Apply complete!

Summary:
  Agents executed: 3
  Total time: 4.2s
  Status: SUCCESS
```

### 4. Visualize the Dependency Graph

```bash
weave graph
```

Output:
```
       ┌─────────────┐
       │  researcher │
       │    gpt-4    │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │   writer    │
       │ claude-3-.. │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │   editor    │
       │    gpt-4    │
       └─────────────┘
```

Or generate Mermaid diagrams:

```bash
weave graph --format mermaid --output graph.mmd
```

## 📖 Documentation

### Commands

#### `weave init`

Initialize a new project with example configuration.

**Options:**
- `--force, -f` - Overwrite existing config
- `--template, -t` - Template to use (default: basic)

```bash
weave init
weave init --force --template research
```

#### `weave plan`

Preview execution plan without running agents.

**Options:**
- `--config, -c` - Config file path (default: .weave.yaml)
- `--weave, -w` - Specific weave to plan

```bash
weave plan
weave plan --config custom.yaml
weave plan --weave research_only
```

#### `weave apply`

Execute the agent workflow.

**Options:**
- `--config, -c` - Config file path
- `--weave, -w` - Specific weave to execute
- `--dry-run` - Show what would execute without running
- `--verbose, -v` - Verbose output

```bash
weave apply
weave apply --dry-run
weave apply --weave content_pipeline --verbose
```

#### `weave graph`

Visualize dependency graph.

**Options:**
- `--config, -c` - Config file path
- `--weave, -w` - Specific weave to visualize
- `--format, -f` - Output format (ascii, mermaid)
- `--output, -o` - Save to file

```bash
weave graph
weave graph --format mermaid
weave graph --format mermaid --output pipeline.mmd
```

#### `weave tools`

List and inspect available tools for agents.

**Options:**
- `--category, -c` - Filter by category (math, text, data, web, etc.)
- `--tags, -t` - Filter by tags (comma-separated)
- `--schema, -s` - Show JSON schema for a specific tool

```bash
# List all tools
weave tools

# Filter by category
weave tools --category math

# View tool schema
weave tools --schema calculator
```

Built-in tools include:
- **calculator** - Evaluate mathematical expressions
- **text_length** - Count characters, words, and lines
- **json_validator** - Validate and parse JSON
- **string_formatter** - Format strings with templates
- **list_operations** - Perform list operations

See [Tool Calling Guide](docs/guides/tool-calling.md) for details.

#### `weave mcp`

Manage MCP (Model Context Protocol) servers.

**Options:**
- `--list, -l` - List configured MCP servers
- `--init` - Create example MCP configuration
- `--add <name>` - Add a new MCP server
- `--command <cmd>` - Command to start server (used with --add)
- `--remove <name>` - Remove an MCP server
- `--server-tools <name>` - List tools from specific server

```bash
# Initialize MCP configuration
weave mcp --init

# List servers
weave mcp

# View tools from server
weave mcp --server-tools filesystem

# Add custom server
weave mcp --add myserver --command "python server.py"
```

See [MCP Integration Guide](docs/guides/mcp.md) for details.

#### `weave plugins`

List and manage plugins for extending agent capabilities.

**Options:**
- `--category, -c` - Filter by category (data_collection, web, nlp, etc.)

```bash
weave plugins
weave plugins --category web
```

Built-in plugins include:
- **web_search** - Search the web for information
- **summarizer** - Summarize text content
- **data_cleaner** - Clean and normalize data
- **json_parser** - Parse and validate JSON
- **markdown_formatter** - Format content as Markdown

See [Plugins Guide](docs/guides/plugins.md) for creating custom plugins.

#### `weave resources`

List and manage agent resources (prompts, skills, knowledge bases).

**Options:**
- `--type, -t` - Filter by type (prompt, skill, recipe, knowledge, rule, behavior, sub_agent)
- `--path, -p` - Resource directory path (default: .weave)
- `--create` - Create example resource structure

```bash
# List all resources
weave resources

# Filter by type
weave resources --type skill

# Create example structure
weave resources --create
```

Resources are organized in `.weave/` directory:
```
.weave/
├── prompts/         # System prompts with YAML frontmatter
├── skills/          # Agent skills (YAML)
├── recipes/         # Workflow templates
├── knowledge/       # Knowledge bases (Markdown, text)
├── rules/           # Agent constraints
├── behaviors/       # Behavioral guidelines
└── sub_agents/      # Nested agent configurations
```

See [Resources Guide](docs/guides/resources.md) for details.

### Configuration

#### Agent Definition

```yaml
agents:
  agent_name:
    model: "model-name"              # Required: Model to use
    tools: [tool1, tool2]            # Optional: Tools available
    inputs: "other_agent"            # Optional: Input dependency
    outputs: "output_key"            # Optional: Output key name
    config:                          # Optional: Model config
      temperature: 0.7
      max_tokens: 1000
      custom_param: "value"
```

#### Weave Definition

```yaml
weaves:
  weave_name:
    description: "What this weave does"  # Optional
    agents: [agent1, agent2, agent3]     # Required: Agent list
```

#### Environment Variables

Use `${VAR}` syntax to reference environment variables:

```yaml
env:
  API_KEY: "${OPENAI_API_KEY}"
  DEFAULT_MODEL: "${MODEL:-gpt-4}"  # With default value

agents:
  my_agent:
    model: "${DEFAULT_MODEL}"
```

### Dependency Resolution

Weave automatically resolves agent dependencies based on `inputs`:

```yaml
agents:
  A:
    model: "gpt-4"
    outputs: "result_a"

  B:
    model: "gpt-4"
    inputs: "A"  # B depends on A
    outputs: "result_b"

  C:
    model: "gpt-4"
    inputs: "B"  # C depends on B

# Execution order: A → B → C
```

Weave detects circular dependencies and invalid references:

```yaml
agents:
  A:
    inputs: "B"  # ❌ Circular!
  B:
    inputs: "A"

# Error: Circular dependency detected: A → B → A
```

## 📂 Examples

See the `examples/` directory for complete examples:

- **[basic.weave.yaml](examples/basic.weave.yaml)** - Simple two-agent pipeline
- **[research-pipeline.weave.yaml](examples/research-pipeline.weave.yaml)** - Multi-stage research workflow
- **[data-processing.weave.yaml](examples/data-processing.weave.yaml)** - ETL-style data pipeline
- **[tool-calling.weave.yaml](examples/tool-calling.weave.yaml)** - Using built-in and custom tools
- **[mcp-integration.weave.yaml](examples/mcp-integration.weave.yaml)** - MCP server integration
- **[custom_plugin_example.py](examples/custom_plugin_example.py)** - Creating custom plugins
- **[resources_example/](examples/resources_example/)** - Complete resources system demo
- **[TOOLS_AND_MCP.md](examples/TOOLS_AND_MCP.md)** - Tool calling and MCP guide

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│            CLI Layer (Typer)            │
│  Commands: init, plan, apply, graph     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Parser Layer (PyYAML)           │
│  YAML loading + env substitution        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Core Layer (Pydantic + NetworkX)   │
│  Validation + dependency graph          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Runtime Layer (Executor)         │
│  Mock execution + hook system           │
└─────────────────────────────────────────┘
```

### Key Components

- **CLI** (`src/weave/cli/`) - Typer commands and Rich output
- **Parser** (`src/weave/parser/`) - YAML parsing and env substitution
- **Core** (`src/weave/core/`) - Pydantic models and dependency graph
- **Runtime** (`src/weave/runtime/`) - Execution engine with hooks
- **Tools** (`src/weave/tools/`) - Tool calling system with MCP integration
- **Plugins** (`src/weave/plugins/`) - Plugin system with built-in and custom plugins
- **Resources** (`src/weave/resources/`) - File-based resource loading for prompts, skills, etc.

## 🔮 Roadmap

### v1.0 (Current) ✅
- ✅ Declarative YAML configuration
- ✅ Dependency graph resolution
- ✅ Mock execution engine
- ✅ CLI with plan/apply/graph/tools/mcp commands
- ✅ ASCII and Mermaid visualization
- ✅ Tool calling with JSON schema validation
- ✅ Built-in tools (calculator, text processing, data validation)
- ✅ Custom tool definitions in YAML
- ✅ MCP (Model Context Protocol) server integration
- ✅ Plugin system with built-in and custom plugins
- ✅ Resource management for prompts, skills, and knowledge bases

### v2.0 (Planned)
- 🔄 Real LLM execution via APIs
- 🔄 Multiple provider support (OpenAI, Anthropic, etc.)
- 🔄 Real tool calling during LLM execution
- 🔄 MCP protocol implementation (full spec)
- 🔄 State management and drift detection
- 🔄 Parallel execution support
- 🔄 Resource loading integration (@prompts/, @skills/ syntax)
- 🔄 Agent module registry
- 🔄 Tool result caching

### v3.0 (Future)
- 📦 Remote module system
- 🌐 Web UI dashboard
- 📊 Execution analytics
- 🔐 Secret management
- 🔄 Advanced plugin marketplace

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

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

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Inspired by declarative infrastructure tools, workflow DAG managers, and agent composition patterns.

## 📬 Contact

- GitHub Issues: [github.com/weave/weave-cli/issues](https://github.com/weave/weave-cli/issues)
- Documentation: [docs.weave.dev](https://docs.weave.dev)

---

Made with ❤️ by the Weave team
