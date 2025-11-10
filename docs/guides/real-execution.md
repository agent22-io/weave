# Real LLM Execution (V2 Features)

Weave now supports real LLM execution with actual API calls to OpenAI and Anthropic!

## Overview

By default, Weave uses **mock execution** for testing and development. With V2, you can now enable **real execution** mode to make actual LLM API calls.

### What's New in V2

1. **Real LLM Execution** - Actual API calls to OpenAI and Anthropic
2. **Plugin Execution** - Plugins run during agent execution
3. **Development Mode** - Interactive workflow development with auto-reload
4. **Run Inspection** - Detailed analysis of completed runs
5. **Better Error Messages** - Helpful suggestions and fuzzy matching
6. **Enhanced Observability** - Full execution traces with LLM prompts

---

## Installation

### Basic Installation (Mock Mode Only)

```bash
pip install weave-cli
```

### With Real LLM Support

```bash
# Install with LLM clients
pip install weave-cli[llm]

# Or install specific providers
pip install weave-cli openai anthropic
```

### With Development Tools

```bash
# Install with dev mode support (file watching)
pip install weave-cli[watch]

# Or install all optional features
pip install weave-cli[all]
```

---

## Real Execution Mode

### Setup

1. **Set up API keys:**

```bash
# For OpenAI
export OPENAI_API_KEY="sk-..."

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

2. **Run with --real flag:**

```bash
weave apply --real
```

### Example

```yaml
# example.weave.yaml
version: "1.0"

agents:
  researcher:
    model: "gpt-4"  # Will use OpenAI API
    tools:
      - web_search
    outputs: "research_findings"
    prompt: |
      Research the given topic and provide key insights.

  writer:
    model: "claude-3-opus"  # Will use Anthropic API
    inputs: "researcher"
    outputs: "article"
    prompt: |
      Write a detailed article based on the research findings.

weaves:
  content_pipeline:
    agents:
      - researcher
      - writer
```

**Run it:**

```bash
# Mock mode (default - no API calls, no costs)
weave apply

# Real mode (actual LLM API calls - costs apply!)
weave apply --real

# Dry run with real mode (validate without executing)
weave apply --real --dry-run
```

---

## Development Mode

Interactive workflow development with auto-reload on file changes.

### Usage

```bash
# Run once
weave dev

# Watch for changes and auto-reload
weave dev --watch

# With real LLM execution
weave dev --real --watch

# Specific weave
weave dev --weave my_workflow --watch
```

### Example Session

```bash
$ weave dev --watch

🔧 Development Mode

📋 Loading configuration from .weave.yaml...
[green]✅ Configuration valid[/green]

🧵 Executing Weave: content_pipeline
Run ID: a1b2c3d4
Order: researcher → writer

  ✓ researcher → research_findings
  ✓ writer → article

Summary: 2 succeeded, 0 failed
Total time: 1.23s

👀 Watching for changes... (Ctrl+C to stop)

# Edit .weave.yaml...

📝 Config changed, reloading...

# Automatically re-runs with new config
```

---

## Run Inspection

Inspect completed runs in detail.

### Usage

```bash
# List recent runs
weave state --list

# Inspect specific run
weave inspect <run-id>

# Hide output details
weave inspect <run-id> --no-outputs

# Show all details including prompts
weave inspect <run-id> --prompts
```

### Example Output

```
Run Inspection: a1b2c3d4

Weave:      content_pipeline
Status:     completed
Started:    2025-01-15 10:30:45
Ended:      2025-01-15 10:31:12
Duration:   26.84s
Agents:     2/2 completed

Agent Execution Details

✓ researcher (15.2s, 1842 tokens)
┌─ Output ────────────────────────────────────┐
│ {                                            │
│   "content": "Based on recent research...", │
│   "model": "gpt-4",                          │
│   "finish_reason": "stop"                    │
│ }                                            │
└──────────────────────────────────────────────┘

✓ writer (11.6s, 2156 tokens)
┌─ Output ────────────────────────────────────┐
│ {                                            │
│   "content": "# The Future of AI\n\n...",   │
│   "model": "claude-3-opus",                  │
│   "finish_reason": "end_turn"                │
│ }                                            │
└──────────────────────────────────────────────┘

Tip: Use --no-outputs to hide output details
```

---

## Error Messages

V2 includes significantly improved error messages with helpful suggestions.

### Example: Unknown Agent Reference

**Before:**
```
ValueError: Agent 'writer' references unknown input agent 'researcher_agent'
```

**After:**
```
📁 File: workflow.weave.yaml
Agent 'writer' references unknown input agent 'researcher_agent'

💡 Suggestion: Did you mean: researcher, analyzer?
```

### Example: Unknown Weave Agent

**Before:**
```
ValueError: Weave 'pipeline' references unknown agent 'sumamrizer'
```

**After:**
```
📁 File: workflow.weave.yaml
Weave 'pipeline' references unknown agent 'sumamrizer'

💡 Suggestion: Did you mean: summarizer?
```

### Example: LLM API Error

```
🤖 OPENAI gpt-4 error:
Rate limit exceeded

💡 Suggestion: Wait a few seconds and try again, or use a different model
🔍 Inspect run: weave inspect a1b2c3d4
```

---

## Supported LLM Providers

### OpenAI

Models: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, etc.

```yaml
agents:
  my_agent:
    model: "gpt-4"
    model_config:
      temperature: 0.7
      max_tokens: 2000
```

**Environment:**
```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic

Models: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`, etc.

```yaml
agents:
  my_agent:
    model: "claude-3-opus"
    model_config:
      temperature: 0.7
      max_tokens: 2000
```

**Environment:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Auto-Detection

Weave automatically detects the provider based on the model name:

- Contains "gpt" or "openai" → OpenAI
- Contains "claude" or "anthropic" → Anthropic

---

## Best Practices

### 1. Start with Mock Mode

Always test workflows in mock mode first:

```bash
# Develop and test
weave apply

# When ready, switch to real
weave apply --real
```

### 2. Use Dry Run

Test with real LLMs without actually executing:

```bash
weave apply --real --dry-run
```

### 3. Monitor Costs

Use `weave inspect` to track token usage:

```bash
weave state --list
weave inspect <run-id>
# Check tokens_used for each agent
```

### 4. Configure Retries

Add retry logic in runtime config:

```yaml
runtime:
  max_retries: 3
  retry_delay: 2.0
  retry_backoff: "exponential"
  retry_on_errors: ["timeout", "api_error", "rate_limit"]
```

### 5. Set Timeouts

Prevent stuck executions:

```yaml
runtime:
  default_timeout: 300.0  # 5 minutes per agent
  weave_timeout: 1800.0   # 30 minutes total
```

---

## Tool and Plugin Execution

V2 includes real tool and plugin execution during agent runs.

### Tools in Real Mode

When an agent uses tools, Weave:

1. Sends tool definitions to the LLM
2. Receives tool calls from the LLM
3. Executes the tools
4. Returns results to the LLM

```yaml
agents:
  analyst:
    model: "gpt-4"
    tools:
      - calculator
      - web_search
      - json_validator
```

### Plugin Execution

Plugins are automatically executed based on agent tool usage:

```yaml
agents:
  researcher:
    model: "claude-3-opus"
    tools:
      - web_search     # web_search plugin runs
      - summarizer     # summarizer plugin runs
```

---

## Observability

Track execution in detail with the observability system:

```yaml
observability:
  enabled: true
  log_level: "INFO"
  log_format: "json"
  collect_metrics: true
  enable_tracing: true
  log_agent_inputs: true   # Log inputs to each agent
  log_agent_outputs: true  # Log outputs from each agent
  log_tool_calls: true     # Log all tool calls
```

---

## Migration from V1

If you have existing Weave configs:

1. **No changes required** - configs work in both mock and real mode
2. **Install LLM dependencies** - `pip install weave-cli[llm]`
3. **Set API keys** - Export `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
4. **Add --real flag** - `weave apply --real`

### Gradual Migration

You can mix modes:

```bash
# Test in mock mode
weave apply

# Test with dry run + real
weave apply --real --dry-run

# Run for real
weave apply --real
```

---

## Troubleshooting

### "OpenAI not installed"

```bash
pip install openai
# or
pip install weave-cli[llm]
```

### "OPENAI_API_KEY not set"

```bash
export OPENAI_API_KEY="sk-..."
```

### "Rate limit exceeded"

Add retry configuration or use exponential backoff:

```yaml
runtime:
  max_retries: 3
  retry_backoff: "exponential"
```

### "watchdog not installed" (dev mode)

```bash
pip install watchdog
# or
pip install weave-cli[watch]
```

---

## Next Steps

- [Configuration Reference](../reference/configuration.md) - All config options
- [Observability & Runtime](./observability-and-runtime.md) - Monitoring and execution
- [Tool Calling](./tool-calling.md) - Using tools with agents
- [Examples](../../examples/) - Real-world examples

---

## V3 Roadmap

Future enhancements:

- **Streaming responses** - Real-time agent output streaming
- **Local model support** - Run models locally with Ollama, etc.
- **Multi-turn conversations** - Agents with memory across runs
- **Real MCP protocol** - Full stdio/SSE communication with MCP servers
- **Cost optimization** - Automatic model selection based on budget
- **Interactive web UI** - Visual workflow builder and monitor
