# Core Concepts

Understanding the fundamental concepts of Weave will help you build powerful agent workflows.

## Agents

**Agents** are individual AI workers that perform specific tasks.

```yaml
agents:
  my_agent:
    model: "gpt-4"              # Model to use
    tools: [web_search]         # Available tools
    inputs: "other_agent"       # Dependency (optional)
    outputs: "result_key"       # Output identifier (optional)
    config:                     # Model configuration
      temperature: 0.7
      max_tokens: 1000
```

### Agent Properties

| Property | Required | Description |
|----------|----------|-------------|
| `model` | ✅ Yes | The AI model to use (e.g., gpt-4, claude-3-opus) |
| `tools` | ❌ No | List of tools available to the agent |
| `inputs` | ❌ No | Which agent's output to use as input |
| `outputs` | ❌ No | Name for this agent's output (defaults to `{agent}_output`) |
| `config` | ❌ No | Model-specific configuration parameters |

### Agent Naming

Agent names must be:
- Alphanumeric (a-z, A-Z, 0-9)
- Can include hyphens (-) and underscores (_)
- Cannot start with a number

**Valid:**
```yaml
agents:
  researcher:        # ✅
  data_processor:    # ✅
  agent-1:           # ✅
  GPT4Helper:        # ✅
```

**Invalid:**
```yaml
agents:
  my agent:          # ❌ spaces not allowed
  123agent:          # ❌ starts with number
  agent@work:        # ❌ special characters
```

## Weaves

**Weaves** orchestrate multiple agents into workflows.

```yaml
weaves:
  my_workflow:
    description: "What this workflow does"
    agents: [agent1, agent2, agent3]
```

### Weave Properties

| Property | Required | Description |
|----------|----------|-------------|
| `description` | ❌ No | Human-readable description of the workflow |
| `agents` | ✅ Yes | List of agents to execute (must exist) |

### Multiple Weaves

You can define multiple weaves in one config:

```yaml
agents:
  fetch: {...}
  process: {...}
  analyze: {...}

weaves:
  quick:
    agents: [fetch, process]

  full:
    agents: [fetch, process, analyze]
```

Execute specific weaves:
```bash
weave apply --weave quick
weave apply --weave full
```

## Dependencies

**Dependencies** define the execution order by linking agent outputs to inputs.

### Simple Dependency

```yaml
agents:
  A:
    model: "gpt-4"
    outputs: "result_a"

  B:
    model: "gpt-4"
    inputs: "A"          # B depends on A
    outputs: "result_b"

# Execution order: A → B
```

### Dependency Chain

```yaml
agents:
  fetch:
    model: "gpt-4"

  process:
    model: "gpt-4"
    inputs: "fetch"      # process depends on fetch

  analyze:
    model: "gpt-4"
    inputs: "process"    # analyze depends on process

# Execution order: fetch → process → analyze
```

### Branching Dependencies

```yaml
agents:
  source:
    model: "gpt-4"

  branch_a:
    model: "gpt-4"
    inputs: "source"     # Both depend on source

  branch_b:
    model: "gpt-4"
    inputs: "source"     # Both depend on source

# Execution order: source → branch_a (and) branch_b
# Note: v0.1.0 executes sequentially; v2.0 will support parallel
```

### Circular Dependencies (Not Allowed)

Weave detects and prevents circular dependencies:

```yaml
agents:
  A:
    inputs: "B"          # ❌ Circular!
  B:
    inputs: "A"

# Error: Circular dependency detected: A → B → A
```

## Configuration File

The `.weave.yaml` file is the main configuration:

```yaml
version: "1.0"           # Config version

env:                     # Environment variables (optional)
  API_KEY: "${OPENAI_API_KEY}"

agents:                  # Agent definitions
  agent1: {...}
  agent2: {...}

weaves:                  # Workflow definitions
  workflow1: {...}
  workflow2: {...}
```

### File Location

By default, Weave looks for `.weave.yaml` in the current directory.

Use custom locations:
```bash
weave plan --config /path/to/config.yaml
weave plan -c custom.yaml
```

## Execution Model

### v0.1.0 (Current)

- **Mock Execution**: Simulates agent execution
- **Sequential**: Agents run one after another
- **Realistic Delays**: Random 0.5-2.5 second delays
- **Mock Outputs**: Generated placeholder results

### v2.0 (Planned)

- **Real Execution**: Actual LLM API calls
- **Parallel**: Independent agents run concurrently
- **State Management**: Track execution state
- **Retry Logic**: Handle failures gracefully

## Environment Variables

Reference shell environment variables in your config:

```yaml
env:
  MODEL: "${DEFAULT_MODEL}"
  KEY: "${OPENAI_API_KEY}"

agents:
  my_agent:
    model: "${MODEL}"    # Uses env var
```

Set environment variables:
```bash
export DEFAULT_MODEL="gpt-4"
export OPENAI_API_KEY="sk-..."
weave apply
```

See [Environment Variables Guide](../guides/environment.md) for more details.

## Outputs and Inputs

### Explicit Outputs

```yaml
agents:
  researcher:
    model: "gpt-4"
    outputs: "research_data"    # Explicit name
```

### Implicit Outputs

```yaml
agents:
  researcher:
    model: "gpt-4"
    # outputs: "researcher_output" (implicit)
```

### Referencing Outputs

```yaml
agents:
  writer:
    inputs: "researcher"              # Short form
    # OR
    inputs: "researcher.outputs"      # Explicit form (same result)
```

## Tools

Tools represent capabilities available to agents:

```yaml
agents:
  researcher:
    model: "gpt-4"
    tools:
      - web_search        # Search the internet
      - summarizer        # Summarize text
      - pdf_reader        # Read PDF files
```

**Note:** In v0.1.0, tools are for documentation purposes. v2.0 will implement actual tool execution.

## Best Practices

1. **Name Descriptively**: Use clear agent names like `researcher`, `data_processor`
2. **Keep Weaves Focused**: Each weave should solve one problem
3. **Document Descriptions**: Add descriptions to weaves
4. **Test Incrementally**: Start with 2-3 agents, then expand
5. **Use `plan` First**: Always preview before applying

## Next Steps

- [Writing Configurations](../guides/writing-configs.md) - Best practices
- [Dependency Management](../guides/dependencies.md) - Advanced patterns
- [Configuration Reference](../reference/configuration.md) - Complete schema
