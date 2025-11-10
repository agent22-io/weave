---
layout: default
title: Weave - Create and deploy AI agents in minutes, not months
---

# 🧵 Weave

**Create and deploy AI agents in minutes, not months**

Weave is a declarative framework for building and composing interoperable AI agents. Define workflows in simple YAML, compose agents that work together seamlessly, and deploy to production with a single command.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Why Weave?

- ⚡ **Fast** - Go from idea to deployed agent in minutes, not months
- 🔗 **Interoperable** - Agents work together seamlessly through declarative composition
- 🎯 **Simple** - Clean YAML configuration, no complex code required
- 🚀 **Production-Ready** - Deploy to AWS, GCP, or Docker with one command
- 🔧 **Extensible** - Custom tools, plugins, and MCP integration
- 📊 **Observable** - Track execution, prompts, outputs, and token usage

---

## 🚀 Quick Start

### 1. Install Weave

```bash
# One-command installation with interactive setup
curl -fsSL https://weave.dev/install.sh | bash

# Then run the setup wizard
weave setup
```

### 2. Initialize a Project

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

### 3. Execute Your Workflow

```bash
# Preview the execution plan
weave plan

# Execute the workflow
weave apply

# Run with real LLMs
weave apply --real

# Development mode with auto-reload
weave dev --watch
```

---

## ✨ Key Features

### Declarative YAML Configuration
Define agents and workflows in clean, readable configuration files.

### Automatic Orchestration
Smart dependency resolution and execution ordering - just define what you need, Weave handles the rest.

### Multiple LLM Providers
Support for OpenAI, Anthropic, and more. Mix and match models in a single workflow.

### Tool Calling & MCP Integration
Built-in tools with JSON schema validation, plus integration with Model Context Protocol servers.

### Cloud Deployment
Deploy to AWS Lambda, GCP Cloud Functions, or Docker with a single command.

### Resource Management
Organize prompts, skills, and knowledge bases in a structured `.weave/` directory.

---

## 📖 Documentation

<div class="docs-grid">

### [Getting Started](docs/getting-started/installation.md)
Installation, quick start, and core concepts

### [CLI Commands](docs/reference/cli-commands.md)
Complete command reference

### [Configuration](docs/reference/configuration.md)
YAML configuration schema and options

### [Guides](docs/guides/writing-configs.md)
Best practices, tutorials, and how-tos

### [Tool Calling](docs/guides/tool-calling.md)
Using built-in and custom tools

### [MCP Integration](docs/guides/mcp.md)
Model Context Protocol servers

### [Plugins](docs/guides/plugins.md)
Extending Weave with custom functionality

### [Resources](docs/guides/resources.md)
Managing prompts, skills, and knowledge bases

</div>

---

## 📂 Examples

The repository includes production-ready examples for common use cases:

- **[Coding Agent](examples/coding-agent-example/)** - AI-powered software development workflow
- **[Content Creation](examples/content-creation-example/)** - Blog posts and marketing content
- **[Research Assistant](examples/research-assistant-example/)** - Research and analysis
- **[Customer Support](examples/customer-support-example/)** - Automated support
- **[Data Processing](examples/data-processing-example/)** - ETL pipelines

Each example includes a README with usage instructions and customization options.

---

## 🏗️ Architecture

Weave is built with a clean, layered architecture:

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

---

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

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📬 Contact

- **GitHub Issues:** [github.com/weave/weave-cli/issues](https://github.com/weave/weave-cli/issues)
- **Documentation:** [Full Documentation](docs/)

---

<div style="text-align: center; margin-top: 2rem;">
Made with ❤️ by the Weave team
</div>
