# CLI Commands

Complete reference for all Weave CLI commands.

## Global Options

```bash
weave --version, -v    # Show version and exit
weave --help           # Show help message
```

---

## `weave init`

Initialize a new Weave project with example configuration.

### Usage

```bash
weave init [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--force` | `-f` | Overwrite existing config | `false` |
| `--template` | `-t` | Template to use | `basic` |

### Examples

```bash
# Create new project
weave init

# Overwrite existing config
weave init --force

# Use specific template
weave init --template research
```

### Output

```
✨ Initialized Weave project!

Created .weave.yaml with example configuration

Next steps:
  1. Edit .weave.yaml to define your agents
  2. Run weave plan to preview execution
  3. Run weave apply to execute the flow
```

---

## `weave plan`

Preview execution plan without running agents.

### Usage

```bash
weave plan [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to config file | `.weave.yaml` |
| `--weave` | `-w` | Specific weave to plan | First weave |

### Examples

```bash
# Plan default weave
weave plan

# Plan with custom config
weave plan --config custom.yaml

# Plan specific weave
weave plan --weave content_pipeline

# Both options
weave plan -c custom.yaml -w my_flow
```

### Output

```
📊 Execution Plan: content_pipeline

                    Agents to Execute
┏━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Order ┃ Agent      ┃ Model         ┃ Inputs     ┃
┡━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ researcher │ gpt-4         │ -          │
│ 2     │ writer     │ claude-3-opus │ researcher │
└───────┴────────────┴───────────────┴────────────┘

Execution graph:
  researcher → writer

2 agents will be executed.
```

---

## `weave apply`

Execute the agent workflow.

### Usage

```bash
weave apply [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to config file | `.weave.yaml` |
| `--weave` | `-w` | Specific weave to apply | First weave |
| `--dry-run` | | Show what would execute | `false` |
| `--verbose` | `-v` | Verbose output | `false` |

### Examples

```bash
# Execute default weave
weave apply

# Dry run (preview only)
weave apply --dry-run

# Verbose output
weave apply --verbose

# Execute specific weave
weave apply --weave my_pipeline

# All options
weave apply -c custom.yaml -w pipeline --verbose
```

### Output

```
🚀 Applying weave: content_pipeline

Executing agents in order:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/2] researcher (gpt-4)
  ⚙️  Running with tools: web_search
  ⏱️  Execution time: 1.2s
  ✅ Output: research_summary (430 tokens)

[2/2] writer (claude-3-opus)
  📥 Input from: researcher
  ⚙️  Running with tools: text_generator
  ⏱️  Execution time: 2.1s
  ✅ Output: draft_article (1058 tokens)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Apply complete!

Summary:
  Agents executed: 2/2
  Total time: 3.3s
  Status: SUCCESS

Final output: draft_article
```

### Dry Run Output

```bash
weave apply --dry-run
```

```
🚀 [DRY RUN] Applying weave: content_pipeline

[1/2] researcher (gpt-4)
  [DRY RUN] Would execute this agent

[2/2] writer (claude-3-opus)
  [DRY RUN] Would execute this agent
  [DRY RUN] Would use input from: researcher
```

---

## `weave graph`

Visualize the dependency graph.

### Usage

```bash
weave graph [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to config file | `.weave.yaml` |
| `--weave` | `-w` | Specific weave to visualize | First weave |
| `--format` | `-f` | Output format (`ascii`, `mermaid`) | `ascii` |
| `--output` | `-o` | Save to file | stdout |

### Examples

```bash
# Display ASCII graph
weave graph

# Display Mermaid diagram
weave graph --format mermaid

# Save to file
weave graph --format mermaid --output diagram.mmd

# Specific weave
weave graph --weave my_pipeline

# All options
weave graph -c custom.yaml -w flow -f mermaid -o graph.mmd
```

### ASCII Output

```
📊 Dependency Graph: content_pipeline

       ┌──────────────┐
       │  researcher  │
       │    gpt-4     │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │   writer     │
       │ claude-3-..  │
       └──────────────┘

Execution order: researcher → writer
```

### Mermaid Output

```
📊 Dependency Graph: content_pipeline

graph TD
    researcher["researcher<br/>gpt-4"]
    writer["writer<br/>claude-3-opus"]
    researcher --> writer

Execution order: researcher → writer
```

You can paste Mermaid output into tools like:
- [Mermaid Live Editor](https://mermaid.live)
- GitHub Markdown (renders automatically)
- VS Code with Mermaid extension

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (config, validation, execution) |

### Examples

```bash
# Check if command succeeded
weave plan && echo "Valid config"

# Chain commands
weave plan && weave apply

# Handle errors
weave apply || echo "Execution failed"
```

---

## Common Patterns

### Validate Before Applying

```bash
# Always plan first
weave plan
# Review the output
weave apply
```

### Multiple Configs

```bash
# Manage multiple environments
weave plan -c dev.yaml
weave plan -c staging.yaml
weave plan -c prod.yaml
```

### Export Documentation

```bash
# Generate graph for documentation
weave graph --format mermaid --output docs/architecture.mmd
```

### Scripting

```bash
#!/bin/bash
# Automated workflow

# Validate config
if weave plan --config prod.yaml; then
    echo "✅ Config valid"

    # Execute with verbose logging
    weave apply --config prod.yaml --verbose
else
    echo "❌ Config invalid"
    exit 1
fi
```

---

## Troubleshooting

### Command Not Found

```bash
# If weave command not found, use module form
python -m weave init
python -m weave plan
```

### Config Not Found

```bash
# Specify full path
weave plan --config /absolute/path/to/.weave.yaml

# Or relative path
weave plan --config ../configs/prod.yaml
```

### Permission Errors

```bash
# If you get permission errors with output
weave graph -o ~/graphs/diagram.mmd
# Ensure the directory exists
mkdir -p ~/graphs
```

---

## Next Steps

- [Configuration Reference](configuration.md) - Learn YAML schema
- [Error Messages](errors.md) - Common errors and solutions
- [Writing Configurations](../guides/writing-configs.md) - Best practices
