# Quick Start Guide

Get up and running with Weave in 5 minutes!

## 1. Create a New Project

```bash
# Create a directory for your project
mkdir my-weave-project
cd my-weave-project

# Initialize Weave
weave init
```

This creates a `.weave.yaml` file with an example configuration.

## 2. Understand the Configuration

Open `.weave.yaml` to see the example:

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
    inputs: "researcher"      # ← Depends on researcher
    outputs: "draft_article"

  editor:
    model: "gpt-4"
    tools: [grammar_checker]
    inputs: "writer"          # ← Depends on writer
    outputs: "final_article"

weaves:
  content_pipeline:
    description: "Research, write, and edit content"
    agents: [researcher, writer, editor]
```

**Key Points:**
- **Agents** define individual AI workers
- **Dependencies** are declared via `inputs`
- **Weaves** orchestrate multiple agents
- Execution order is automatically determined: `researcher → writer → editor`

## 3. Preview the Execution Plan

```bash
weave plan
```

**Output:**
```
📊 Execution Plan: content_pipeline

┏━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Order ┃ Agent      ┃ Model         ┃ Inputs     ┃
┡━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ researcher │ gpt-4         │ -          │
│ 2     │ writer     │ claude-3-opus │ researcher │
│ 3     │ editor     │ gpt-4         │ writer     │
└───────┴────────────┴───────────────┴────────────┘

Execution graph:
  researcher → writer → editor

3 agents will be executed.
```

## 4. Execute the Workflow

```bash
weave apply
```

**Output:**
```
🚀 Applying weave: content_pipeline

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

✨ Apply complete!
```

**Note:** In v0.1.0, execution is mocked. v2.0 will support real LLM API calls.

## 5. Visualize the Graph

```bash
weave graph
```

**Output:**
```
       ┌──────────────┐
       │  researcher  │
       │    gpt-4     │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │   writer     │
       │ claude-3-..  │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │   editor     │
       │    gpt-4     │
       └──────────────┘
```

## Common Commands

```bash
# Initialize new project
weave init

# Preview execution
weave plan

# Execute workflow
weave apply

# Dry run (show what would execute)
weave apply --dry-run

# Verbose output
weave apply --verbose

# Visualize graph
weave graph

# Export Mermaid diagram
weave graph --format mermaid --output graph.mmd

# Use custom config file
weave plan --config custom.yaml

# Execute specific weave
weave apply --weave my_pipeline
```

## Next Steps

- [Core Concepts](concepts.md) - Understand agents, weaves, and dependencies
- [Configuration Reference](../reference/configuration.md) - Complete YAML schema
- [Writing Configurations](../guides/writing-configs.md) - Best practices
- [Examples](../../examples/) - See more complete examples

## Tips

1. **Start Simple**: Begin with 2-3 agents before building complex pipelines
2. **Use `plan` Often**: Always preview before applying
3. **Check Dependencies**: Use `graph` to visualize agent relationships
4. **Iterate Quickly**: Mock execution makes testing fast

## Troubleshooting

### Config Not Found

```bash
# Make sure you're in the project directory
pwd

# Or specify config explicitly
weave plan --config /path/to/.weave.yaml
```

### Validation Errors

If you see validation errors:
1. Check YAML syntax with a validator
2. Ensure all referenced agents exist
3. Verify required fields are present

See [Error Messages](../reference/errors.md) for more help.
