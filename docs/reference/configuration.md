# Configuration Reference

Complete YAML schema reference for Weave configuration files.

## File Structure

```yaml
version: "1.0"           # Required
env: {...}               # Optional
agents: {...}            # Required
weaves: {...}            # Required
```

---

## Root Properties

### `version`

**Type:** String
**Required:** Yes
**Default:** `"1.0"`

Specifies the configuration schema version.

```yaml
version: "1.0"
```

### `env`

**Type:** Object
**Required:** No
**Default:** `{}`

Define environment variables for use throughout the config.

```yaml
env:
  DEFAULT_MODEL: "gpt-4"
  API_KEY: "${OPENAI_API_KEY}"    # Reference shell env
  MAX_TOKENS: "2000"
```

### `agents`

**Type:** Object (key-value pairs)
**Required:** Yes

Define all agents. Keys are agent names, values are agent configurations.

```yaml
agents:
  researcher: {...}
  writer: {...}
```

### `weaves`

**Type:** Object (key-value pairs)
**Required:** Yes (at least one)

Define workflows. Keys are weave names, values are weave configurations.

```yaml
weaves:
  content_pipeline: {...}
  data_flow: {...}
```

---

## Agent Configuration

### Agent Properties

```yaml
agents:
  agent_name:
    model: "string"              # Required
    tools: ["list"]              # Optional
    inputs: "string"             # Optional
    outputs: "string"            # Optional
    config: {...}                # Optional
```

### `model`

**Type:** String
**Required:** Yes

The AI model identifier.

```yaml
agents:
  my_agent:
    model: "gpt-4"
    # or
    model: "claude-3-opus"
    # or
    model: "${DEFAULT_MODEL}"    # From env
```

**Common Models:**
- `gpt-4`
- `gpt-3.5-turbo`
- `claude-3-opus`
- `claude-3-sonnet`

### `tools`

**Type:** Array of strings
**Required:** No
**Default:** `[]`

List of tools available to the agent.

```yaml
agents:
  researcher:
    model: "gpt-4"
    tools:
      - web_search
      - summarizer
      - pdf_reader
```

**Note:** In v0.1.0, tools are descriptive. v2.0 will implement actual tool execution.

### `inputs`

**Type:** String
**Required:** No
**Default:** `null`

Reference to another agent whose output this agent depends on.

```yaml
agents:
  writer:
    model: "gpt-4"
    inputs: "researcher"         # Depends on researcher agent
```

**Alternative forms:**
```yaml
inputs: "researcher"             # Short form
inputs: "researcher.outputs"     # Explicit form (same result)
```

**Rules:**
- Referenced agent must exist
- Referenced agent must be in the same weave
- Cannot create circular dependencies

### `outputs`

**Type:** String
**Required:** No
**Default:** `"{agent_name}_output"`

Name for this agent's output.

```yaml
agents:
  researcher:
    model: "gpt-4"
    outputs: "research_summary"   # Explicit name
```

**Default behavior:**
```yaml
agents:
  researcher:
    model: "gpt-4"
    # outputs defaults to "researcher_output"
```

### `config`

**Type:** Object
**Required:** No
**Default:** `{}`

Model-specific configuration parameters.

```yaml
agents:
  my_agent:
    model: "gpt-4"
    config:
      temperature: 0.7           # Randomness (0-1)
      max_tokens: 2000           # Max output length
      top_p: 0.9                 # Nucleus sampling
      custom_param: "value"      # Any custom field
```

**Common Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `temperature` | Number (0-1) | Controls randomness |
| `max_tokens` | Integer | Maximum output tokens |
| `top_p` | Number (0-1) | Nucleus sampling threshold |

**Note:** Configuration is flexible and accepts any key-value pairs for future extensibility.

---

## Weave Configuration

### Weave Properties

```yaml
weaves:
  weave_name:
    description: "string"        # Optional
    agents: ["list"]             # Required
```

### `description`

**Type:** String
**Required:** No
**Default:** `""`

Human-readable description of the workflow.

```yaml
weaves:
  content_pipeline:
    description: "Research, write, and edit content"
    agents: [...]
```

### `agents`

**Type:** Array of strings
**Required:** Yes (at least one)

List of agents to include in this workflow.

```yaml
weaves:
  my_workflow:
    agents:
      - researcher
      - writer
      - editor
```

**Rules:**
- All referenced agents must be defined in `agents` section
- Must contain at least one agent
- Order doesn't matter (execution order is determined by dependencies)

---

## Environment Variables

### Syntax

Use `${VARIABLE_NAME}` to reference environment variables.

```yaml
env:
  MODEL: "${DEFAULT_MODEL}"
  KEY: "${OPENAI_API_KEY}"

agents:
  my_agent:
    model: "${MODEL}"
```

### Setting Environment Variables

**Bash/Linux/macOS:**
```bash
export DEFAULT_MODEL="gpt-4"
export OPENAI_API_KEY="sk-..."
weave apply
```

**Windows (PowerShell):**
```powershell
$env:DEFAULT_MODEL="gpt-4"
$env:OPENAI_API_KEY="sk-..."
weave apply
```

**Inline:**
```bash
DEFAULT_MODEL=gpt-4 weave apply
```

### Missing Variables

If a referenced environment variable is not set:

```
Error: Environment variable 'OPENAI_API_KEY' not set
Please set these variables or remove them from your config.
```

---

## Complete Example

```yaml
version: "1.0"

# Environment configuration
env:
  DEFAULT_MODEL: "${DEFAULT_MODEL:-gpt-4}"
  API_KEY: "${OPENAI_API_KEY}"

# Agent definitions
agents:
  # Data collection agent
  fetcher:
    model: "${DEFAULT_MODEL}"
    tools:
      - api_client
      - web_scraper
    config:
      temperature: 0.3
      max_tokens: 1000
    outputs: "raw_data"

  # Data processing agent
  processor:
    model: "gpt-4"
    tools:
      - data_cleaner
      - validator
    inputs: "fetcher"          # Depends on fetcher
    config:
      temperature: 0.2
      max_tokens: 1500
    outputs: "clean_data"

  # Analysis agent
  analyzer:
    model: "claude-3-opus"
    tools:
      - statistical_analyzer
      - pattern_detector
    inputs: "processor"        # Depends on processor
    config:
      temperature: 0.5
      max_tokens: 2000
    outputs: "insights"

  # Report generator
  reporter:
    model: "gpt-4"
    tools:
      - report_formatter
      - chart_generator
    inputs: "analyzer"         # Depends on analyzer
    config:
      temperature: 0.7
      max_tokens: 3000
    outputs: "final_report"

# Workflow definitions
weaves:
  # Full pipeline
  full_analysis:
    description: "Complete data analysis workflow"
    agents:
      - fetcher
      - processor
      - analyzer
      - reporter

  # Quick analysis (skip reporting)
  quick_analysis:
    description: "Fast analysis without full report"
    agents:
      - fetcher
      - processor
      - analyzer
```

---

## Validation Rules

### Required Fields

❌ **Missing required field:**
```yaml
agents:
  my_agent:
    # Error: 'model' is required
    tools: [web_search]
```

✅ **Correct:**
```yaml
agents:
  my_agent:
    model: "gpt-4"
    tools: [web_search]
```

### Agent References

❌ **Invalid reference:**
```yaml
agents:
  writer:
    model: "gpt-4"
    inputs: "researcher"    # Error: researcher doesn't exist

weaves:
  pipeline:
    agents: [writer]
```

✅ **Correct:**
```yaml
agents:
  researcher:
    model: "gpt-4"

  writer:
    model: "gpt-4"
    inputs: "researcher"

weaves:
  pipeline:
    agents: [researcher, writer]
```

### Circular Dependencies

❌ **Circular dependency:**
```yaml
agents:
  A:
    model: "gpt-4"
    inputs: "B"

  B:
    model: "gpt-4"
    inputs: "A"         # Error: A → B → A

weaves:
  pipeline:
    agents: [A, B]
```

✅ **Linear dependency:**
```yaml
agents:
  A:
    model: "gpt-4"

  B:
    model: "gpt-4"
    inputs: "A"         # ✓ A → B

weaves:
  pipeline:
    agents: [A, B]
```

---

## Best Practices

### 1. Use Environment Variables for Secrets

✅ **Good:**
```yaml
env:
  API_KEY: "${OPENAI_API_KEY}"

agents:
  my_agent:
    config:
      api_key: "${API_KEY}"
```

❌ **Bad:**
```yaml
agents:
  my_agent:
    config:
      api_key: "sk-1234567890..."    # Don't hardcode secrets!
```

### 2. Name Agents Descriptively

✅ **Good:**
```yaml
agents:
  web_scraper: {...}
  data_cleaner: {...}
  report_generator: {...}
```

❌ **Bad:**
```yaml
agents:
  agent1: {...}
  agent2: {...}
  agent3: {...}
```

### 3. Add Descriptions to Weaves

✅ **Good:**
```yaml
weaves:
  etl_pipeline:
    description: "Extract, transform, and load customer data"
    agents: [...]
```

❌ **Bad:**
```yaml
weaves:
  pipeline1:
    agents: [...]
```

### 4. Keep Config Modular

For large projects, consider multiple config files:

```bash
# Development
weave apply --config configs/dev.yaml

# Production
weave apply --config configs/prod.yaml
```

---

## Next Steps

- [CLI Commands](cli-commands.md) - Command reference
- [Writing Configurations](../guides/writing-configs.md) - Best practices
- [Error Messages](errors.md) - Troubleshooting
