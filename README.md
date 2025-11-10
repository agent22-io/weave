# 🧵 Weave

**Create and deploy AI agents in minutes, not months**

Weave is a declarative framework for building and composing interoperable AI agents. Define workflows in simple YAML, compose agents that work together seamlessly, and deploy to production with a single command.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Why Weave?

- ⚡ **Fast** - Go from idea to deployed agent in minutes, not months
- 🔗 **Interoperable** - Agents work together seamlessly through declarative composition
- 🎯 **Simple** - Clean YAML configuration, no complex code required
- 🚀 **Production-Ready** - Deploy to AWS, GCP, or Docker with one command
- 🔧 **Extensible** - Custom tools, plugins, and MCP integration
- 📊 **Observable** - Track execution, prompts, outputs, and token usage

## ✨ Key Features

- **Declarative YAML** - Define agents and workflows in clean configuration
- **Automatic Orchestration** - Smart dependency resolution and execution ordering
- **Multiple LLM Providers** - OpenAI, Anthropic, and more
- **Tool Calling** - Built-in and custom tools with JSON schema validation
- **MCP Integration** - Connect to Model Context Protocol servers
- **Cloud Deployment** - Deploy to AWS Lambda, GCP Cloud Functions, or Docker
- **Development Mode** - Interactive workflow development with auto-reload
- **Resource Management** - Organize prompts, skills, and knowledge bases

## 📦 Installation

### Quick Install (Recommended)

```bash
# One-command installation with interactive setup
curl -fsSL https://weave.dev/install.sh | bash

# Then run the setup wizard
weave setup
```


### Post-Install Setup

After installation, run the interactive setup wizard:

```bash
weave setup
```

This will:
- ✓ Configure API keys for LLM providers
- ✓ Install shell completion (bash/zsh/fish)
- ✓ Create example project
- ✓ Set up configuration directory

Or use individual setup commands:

```bash
# Check installation status
weave doctor

# Install shell completion only
weave completion bash --install

# Create example project
weave init
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

### 4. Real LLM Execution (V2)

**Set up API keys:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Run with real LLMs:**
```bash
# Run with actual API calls (costs apply!)
weave apply --real

# Or use development mode with auto-reload
weave dev --real --watch
```

**Inspect completed runs:**
```bash
# List recent runs
weave state --list

# Inspect specific run with detailed metrics
weave inspect <run-id>
```

### 5. Development Workflow (V2)

Interactive development with file watching:

```bash
$ weave dev --watch

🔧 Development Mode

🧵 Executing Weave: content_pipeline
Run ID: a1b2c3d4

  ✓ researcher → research_summary (1.2s, 450 tokens)
  ✓ writer → draft_article (2.1s, 820 tokens)
  ✓ editor → final_article (0.9s, 320 tokens)

Summary: 3 succeeded, 0 failed

👀 Watching for changes... (Ctrl+C to stop)

# Edit .weave.yaml...

📝 Config changed, reloading...
# Automatically re-runs with new config
```

### 6. Cloud Deployment (V3)

Deploy your workflows to production:

```bash
# Deploy to AWS Lambda
weave deploy --name my-weave --provider aws --region us-east-1

# Deploy to GCP Cloud Functions
weave deploy --name my-weave --provider gcp --region us-central1

# Deploy to Docker
weave deploy --name my-weave --provider docker

# List all deployments
weave deployments

# Destroy deployment
weave undeploy my-weave --provider aws
```

**What you get:**
- ☁️ Serverless execution on AWS/GCP
- 🔗 HTTP endpoint for invoking your workflow
- 🔐 Automatic credential management
- 📊 Deployment status tracking

### 7. Visualize the Dependency Graph

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

## 📂 Examples

The `examples/` directory contains production-ready examples for common use cases:

### Complete Examples (with resources)

- **[coding-agent-example/](examples/coding-agent-example/)** - AI-powered software development workflow
  - Requirements analysis, code generation, testing, review, and documentation
  - Complete with prompts, skills, and knowledge bases

- **[content-creation-example/](examples/content-creation-example/)** - Blog posts and marketing content
  - Research → Write → Edit pipeline with SEO optimization

- **[research-assistant-example/](examples/research-assistant-example/)** - Research and analysis
  - Literature review, data collection, synthesis, and peer review

- **[customer-support-example/](examples/customer-support-example/)** - Automated support
  - Ticket classification, KB search, response generation, and quality checking

- **[data-processing-example/](examples/data-processing-example/)** - ETL pipelines
  - Extract, transform, analyze, and report on data

### Getting Started

- **[basic.weave.yaml](examples/basic.weave.yaml)** - Simplest possible example
- **[resources_example/](examples/resources_example/)** - Resource system template

Each example includes a README with usage instructions and customization options.

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

## 📬 Contact

- GitHub Issues: [github.com/weave/weave-cli/issues](https://github.com/weave/weave-cli/issues)
- Documentation: [docs.weave.dev](https://docs.weave.dev)

---

Made with ❤️ by the Weave team
