# Configuration Reference

Complete reference for all Weave configuration options.

## Table of Contents

- [Overview](#overview)
- [Root Level](#root-level)
- [Storage Configuration](#storage-configuration)
- [Tool Definitions](#tool-definitions)
- [Agent Configuration](#agent-configuration)
  - [Agent Capabilities](#agent-capabilities)
  - [Model Configuration](#model-configuration)
  - [Memory Configuration](#memory-configuration)
  - [Storage Configuration (Agent)](#storage-configuration-agent)
- [Weave Definition](#weave-definition)
- [Complete Example](#complete-example)

## Overview

Weave configurations are defined in YAML files with the `.weave.yaml` extension. All functionality is accessible through configuration - no code required.

## Root Level

The top-level structure of a Weave configuration file.

```yaml
version: "1.0"
env: {}
storage: {}
tools: {}
agents: {}
weaves: {}
```

### `version` (required)

**Type**: `string`
**Default**: `"1.0"`
**Description**: Configuration format version.

```yaml
version: "1.0"
```

### `env` (optional)

**Type**: `object`
**Default**: `{}`
**Description**: Environment variables to set for the execution. Can be referenced using `${VAR_NAME}` syntax throughout the configuration.

```yaml
env:
  MODEL_NAME: "gpt-4"
  API_ENDPOINT: "https://api.openai.com/v1"
```

### `storage` (optional)

**Type**: [`GlobalStorageConfig`](#storage-configuration)
**Default**: `null`
**Description**: Global storage configuration for the entire weave. See [Storage Configuration](#storage-configuration) for details.

### `tools` (optional)

**Type**: `object`
**Default**: `{}`
**Description**: Custom tool definitions. See [Tool Definitions](#tool-definitions) for details.

### `agents` (required)

**Type**: `object`
**Default**: N/A
**Description**: Dictionary of agent definitions. At least one agent is required. See [Agent Configuration](#agent-configuration) for details.

### `weaves` (required)

**Type**: `object`
**Default**: N/A
**Description**: Dictionary of weave (workflow) definitions. At least one weave is required. See [Weave Definition](#weave-definition) for details.

---

## Storage Configuration

Global storage settings for execution state, lock files, and agent outputs.

```yaml
storage:
  enabled: true
  base_path: ".weave/storage"
  state_file: ".weave/state.yaml"
  lock_file: ".weave/weave.lock"
  format: "json"
  auto_cleanup: false
  retention_days: 30
```

### `enabled`

**Type**: `boolean`
**Default**: `true`
**Description**: Enable or disable storage functionality.

### `base_path`

**Type**: `string`
**Default**: `".weave/storage"`
**Description**: Base directory for storing agent outputs, memory, and logs.

### `state_file`

**Type**: `string`
**Default**: `".weave/state.yaml"`
**Description**: Path to execution state file that tracks all runs.

### `lock_file`

**Type**: `string`
**Default**: `".weave/weave.lock"`
**Description**: Path to lock file used to prevent concurrent executions.

### `format`

**Type**: `string`
**Options**: `"json"`, `"yaml"`, `"pickle"`
**Default**: `"json"`
**Description**: Storage format for saved data.

### `auto_cleanup`

**Type**: `boolean`
**Default**: `false`
**Description**: Automatically clean up old execution state on startup.

### `retention_days`

**Type**: `integer`
**Default**: `30`
**Description**: Number of days to retain execution state when auto_cleanup is enabled.

---

## Tool Definitions

Define custom tools that agents can use.

```yaml
tools:
  tool_name:
    description: "Tool description"
    category: "category_name"
    tags: ["tag1", "tag2"]
    handler: "module.path.to.function"
    parameters:
      param_name:
        type: "string"
        description: "Parameter description"
        required: true
        default: "default_value"
        enum: ["option1", "option2"]
```

### Tool Structure

#### `description` (required)

**Type**: `string`
**Description**: Human-readable description of what the tool does.

#### `category`

**Type**: `string`
**Default**: `"general"`
**Description**: Category for organizing tools (e.g., "research", "communication", "analysis").

#### `tags`

**Type**: `array[string]`
**Default**: `[]`
**Description**: Tags for filtering and searching tools.

#### `handler`

**Type**: `string`
**Default**: `null`
**Description**: Python module path to the function that implements the tool (e.g., `"mymodule.tools.my_function"`).

#### `parameters`

**Type**: `object`
**Default**: `{}`
**Description**: Dictionary of parameter definitions. Each parameter has:

##### Parameter Definition

- **`type`** (required): `"string"`, `"number"`, `"integer"`, `"boolean"`, `"array"`, or `"object"`
- **`description`** (required): Parameter description
- **`required`**: Whether parameter is required (default: `true`)
- **`default`**: Default value if not provided
- **`enum`**: Array of allowed values

### Built-in Tools

Weave includes built-in tools:

- `calculator`: Basic arithmetic operations
- `text_length`: Count characters and words
- `json_validator`: Validate JSON data
- `string_formatter`: Format and manipulate strings
- `list_operations`: List manipulation operations
- `web_search`: Web search (via MCP)

### Example

```yaml
tools:
  email_sender:
    description: "Send emails via SMTP"
    category: "communication"
    tags: ["email", "messaging"]
    parameters:
      to:
        type: "string"
        description: "Recipient email address"
        required: true
      subject:
        type: "string"
        description: "Email subject"
        required: true
      body:
        type: "string"
        description: "Email body content"
        required: true
      priority:
        type: "string"
        description: "Email priority"
        required: false
        enum: ["low", "normal", "high"]
        default: "normal"
```

---

## Agent Configuration

Agents are the core building blocks of Weave workflows.

```yaml
agents:
  agent_name:
    model: "gpt-4"
    capabilities: [coding, text-analysis]
    model_config: {}
    memory: {}
    storage: {}
    tools: []
    inputs: "other_agent"
    outputs: "output_key"
    prompt: "Custom instructions"
```

### `model` (required)

**Type**: `string`
**Description**: Model identifier (e.g., `"gpt-4"`, `"claude-3-opus"`, `"gpt-3.5-turbo"`).

**Examples**:
- OpenAI: `"gpt-4"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
- Anthropic: `"claude-3-opus"`, `"claude-3-sonnet"`, `"claude-3-haiku"`
- Local: `"local/llama-2"`, `"ollama/mistral"`

### `capabilities`

**Type**: `array[string]`
**Default**: `[]`
**Description**: List of agent capabilities that describe what the agent can do.

**Available Capabilities**:

#### Core Capabilities
- `coding`: Code generation, analysis, review
- `image-gen`: Image generation and manipulation
- `image-analysis`: Image understanding and analysis
- `audio-gen`: Audio/music generation
- `audio-analysis`: Audio transcription and analysis
- `video-gen`: Video generation
- `video-analysis`: Video understanding

#### Content Capabilities
- `text-generation`: Creative writing, content creation
- `text-analysis`: NLP, sentiment analysis, summarization
- `translation`: Language translation
- `search`: Web/knowledge search
- `research`: Information gathering and synthesis

#### Technical Capabilities
- `data-processing`: Data transformation and analysis
- `data-visualization`: Chart and graph creation
- `sql`: Database queries and analysis
- `api-integration`: External API interaction
- `web-scraping`: Web data extraction

#### Business Capabilities
- `analytics`: Business intelligence and reporting
- `planning`: Strategic planning and organization
- `decision-making`: Analysis and recommendations
- `classification`: Categorization and tagging
- `extraction`: Information extraction from text

#### Communication Capabilities
- `email`: Email composition and processing
- `chat`: Conversational interaction
- `documentation`: Technical documentation
- `reporting`: Report generation

#### Specialized Capabilities
- `security`: Security analysis and review
- `compliance`: Regulatory compliance checking
- `qa`: Quality assurance and testing
- `monitoring`: System monitoring and alerting
- `optimization`: Performance and efficiency optimization

**Example**:
```yaml
capabilities: [coding, security, qa]
```

### `model_config`

**Type**: [`ModelConfig`](#model-configuration)
**Default**: `null`
**Description**: Model-specific configuration settings.

### `memory`

**Type**: [`MemoryConfig`](#memory-configuration)
**Default**: `null`
**Description**: Memory management configuration.

### `storage`

**Type**: [`StorageConfig`](#storage-configuration-agent)
**Default**: `null`
**Description**: Agent-specific storage settings.

### `tools`

**Type**: `array[string]`
**Default**: `[]`
**Description**: List of tool names available to this agent. Can reference built-in tools, custom tools, or MCP tools.

**Example**:
```yaml
tools: [calculator, web_search, custom_tool, string_formatter]
```

### `inputs`

**Type**: `string`
**Default**: `null`
**Description**: Reference to another agent whose output becomes this agent's input. Creates a dependency relationship.

**Example**:
```yaml
# Agent B receives output from Agent A
agents:
  agent_a:
    model: "gpt-4"
    outputs: "research_data"

  agent_b:
    model: "gpt-4"
    inputs: "agent_a"  # Gets research_data from agent_a
```

### `outputs`

**Type**: `string`
**Default**: `null`
**Description**: Key name for this agent's output. Other agents can reference this using `inputs`.

### `prompt`

**Type**: `string`
**Default**: `null`
**Description**: Agent-specific instructions or system prompt. Provides context and guidance for the agent's behavior.

**Example**:
```yaml
prompt: |
  You are a code review expert. Analyze the provided code for:
  - Security vulnerabilities
  - Performance issues
  - Best practice violations
  Provide specific, actionable feedback.
```

---

## Model Configuration

Fine-tune model behavior and API settings.

```yaml
model_config:
  provider: "openai"
  temperature: 0.7
  max_tokens: 1000
  top_p: 1.0
  frequency_penalty: 0.0
  presence_penalty: 0.0
  stop_sequences: []
  api_base: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
```

### `provider`

**Type**: `string`
**Default**: `"openai"`
**Options**: `"openai"`, `"anthropic"`, `"local"`, or custom
**Description**: LLM provider identifier.

### `temperature`

**Type**: `float`
**Range**: `0.0` to `2.0`
**Default**: `0.7`
**Description**: Controls randomness. Lower = more deterministic, higher = more creative.

- `0.0-0.3`: Deterministic, factual
- `0.4-0.7`: Balanced
- `0.8-1.0`: Creative, varied
- `1.0-2.0`: Very creative (use sparingly)

### `max_tokens`

**Type**: `integer`
**Default**: `1000`
**Description**: Maximum number of tokens in the response.

### `top_p`

**Type**: `float`
**Range**: `0.0` to `1.0`
**Default**: `1.0`
**Description**: Nucleus sampling parameter. Alternative to temperature.

### `frequency_penalty`

**Type**: `float`
**Range**: `-2.0` to `2.0`
**Default**: `0.0`
**Description**: Penalize repeated tokens based on frequency. Positive values reduce repetition.

### `presence_penalty`

**Type**: `float`
**Range**: `-2.0` to `2.0`
**Default**: `0.0`
**Description**: Penalize repeated tokens based on presence. Positive values encourage topic diversity.

### `stop_sequences`

**Type**: `array[string]`
**Default**: `[]`
**Description**: Sequences that trigger response completion.

### `api_base`

**Type**: `string`
**Default**: `null`
**Description**: Custom API endpoint URL.

### `api_key_env`

**Type**: `string`
**Default**: `"API_KEY"`
**Description**: Environment variable name containing the API key.

---

## Memory Configuration

Configure how agents retain and manage conversation history.

```yaml
memory:
  type: "buffer"
  max_messages: 100
  summarize_after: 50
  context_window: 4000
  persist: true
  storage_key: "agent_memory"
```

### `type`

**Type**: `string`
**Options**: `"buffer"`, `"summary"`, `"sliding_window"`, `"vector"`
**Default**: `"buffer"`
**Description**: Memory management strategy.

**Types**:
- **`buffer`**: Keep recent N messages
- **`summary`**: Periodically summarize old messages
- **`sliding_window`**: Keep last N tokens of context
- **`vector`**: Use vector database for semantic search (future)

### `max_messages`

**Type**: `integer`
**Default**: `100`
**Description**: Maximum number of messages to keep in memory.

### `summarize_after`

**Type**: `integer`
**Default**: `null`
**Description**: Summarize messages after N messages (for `summary` type).

### `context_window`

**Type**: `integer`
**Default**: `4000`
**Description**: Context window size in tokens.

### `persist`

**Type**: `boolean`
**Default**: `false`
**Description**: Save memory to storage for persistence across runs.

### `storage_key`

**Type**: `string`
**Default**: `null`
**Description**: Custom key for storing memory. If not provided, uses agent name.

---

## Storage Configuration (Agent)

Agent-specific storage settings that override global storage.

```yaml
storage:
  enabled: true
  base_path: ".weave/agent_storage"
  save_outputs: true
  save_memory: false
  save_logs: true
  retention_days: 7
  format: "json"
```

### `enabled`

**Type**: `boolean`
**Default**: `true`
**Description**: Enable storage for this agent.

### `base_path`

**Type**: `string`
**Default**: `".weave/storage"`
**Description**: Base directory for this agent's storage (overrides global).

### `save_outputs`

**Type**: `boolean`
**Default**: `true`
**Description**: Save agent outputs to storage.

### `save_memory`

**Type**: `boolean`
**Default**: `false`
**Description**: Save agent memory state to storage.

### `save_logs`

**Type**: `boolean`
**Default**: `true`
**Description**: Save execution logs for this agent.

### `retention_days`

**Type**: `integer`
**Default**: `null`
**Description**: Auto-delete files older than N days.

### `format`

**Type**: `string`
**Options**: `"json"`, `"yaml"`, `"pickle"`
**Default**: `"json"`
**Description**: Format for stored data.

---

## Weave Definition

Weaves define the workflow execution order and agent composition.

```yaml
weaves:
  workflow_name:
    description: "Workflow description"
    agents: [agent1, agent2, agent3]
```

### `description`

**Type**: `string`
**Default**: `""`
**Description**: Human-readable description of the workflow.

### `agents` (required)

**Type**: `array[string]`
**Description**: Ordered list of agent names to execute. Agents with dependencies (via `inputs`) are automatically ordered correctly.

**Example**:
```yaml
weaves:
  data_pipeline:
    description: "Extract, transform, and analyze data"
    agents:
      - extractor
      - transformer
      - analyzer
      - reporter
```

---

## Complete Example

A comprehensive example showing all configuration options:

```yaml
version: "1.0"

# Environment variables
env:
  PRIMARY_MODEL: "gpt-4"
  BACKUP_MODEL: "claude-3-opus"

# Global storage configuration
storage:
  enabled: true
  base_path: ".weave/storage"
  state_file: ".weave/state.yaml"
  lock_file: ".weave/weave.lock"
  format: "json"
  auto_cleanup: true
  retention_days: 30

# Custom tool definitions
tools:
  database_query:
    description: "Execute SQL queries on database"
    category: "data"
    tags: ["sql", "database"]
    parameters:
      query:
        type: "string"
        description: "SQL query to execute"
        required: true
      database:
        type: "string"
        description: "Database name"
        required: false
        default: "main"

  send_email:
    description: "Send email notifications"
    category: "communication"
    parameters:
      to:
        type: "string"
        required: true
      subject:
        type: "string"
        required: true
      body:
        type: "string"
        required: true

# Agent definitions
agents:
  researcher:
    model: "${PRIMARY_MODEL}"
    capabilities: [research, search, text-analysis]
    model_config:
      provider: "openai"
      temperature: 0.7
      max_tokens: 2000
      api_key_env: "OPENAI_API_KEY"
    tools: [web_search, calculator]
    outputs: "research_findings"
    storage:
      save_outputs: true
      save_logs: true
    prompt: |
      Research the given topic thoroughly and provide:
      - Key insights and findings
      - Relevant statistics and data
      - Credible sources
      Format results in structured JSON.

  analyst:
    model: "${PRIMARY_MODEL}"
    capabilities: [data-processing, analytics, sql]
    model_config:
      provider: "openai"
      temperature: 0.3
      max_tokens: 1500
    inputs: "researcher"
    tools: [calculator, database_query, list_operations]
    memory:
      type: "buffer"
      max_messages: 100
      persist: true
    outputs: "analysis_results"
    storage:
      save_outputs: true
      save_memory: true
    prompt: |
      Analyze the research data:
      - Extract key metrics
      - Identify trends and patterns
      - Perform statistical analysis
      - Generate insights

  writer:
    model: "${BACKUP_MODEL}"
    capabilities: [text-generation, documentation, reporting]
    model_config:
      provider: "anthropic"
      temperature: 0.8
      max_tokens: 3000
      api_key_env: "ANTHROPIC_API_KEY"
    inputs: "analyst"
    tools: [string_formatter, text_length]
    outputs: "report"
    storage:
      save_outputs: true
      retention_days: 90
    prompt: |
      Create a comprehensive report:
      - Executive summary
      - Detailed findings
      - Visualizations and charts
      - Recommendations and next steps

  notifier:
    model: "gpt-3.5-turbo"
    capabilities: [email, chat]
    model_config:
      temperature: 0.5
      max_tokens: 500
    inputs: "writer"
    tools: [send_email]
    storage:
      save_logs: true
    prompt: |
      Send notification email with report summary.
      Keep it concise and professional.

# Workflow definitions
weaves:
  full_analysis:
    description: "Complete research, analysis, and reporting pipeline"
    agents:
      - researcher
      - analyst
      - writer
      - notifier

  quick_research:
    description: "Quick research without full analysis"
    agents:
      - researcher
      - writer
```

## Configuration Validation

Validate your configuration before execution:

```bash
weave validate config.weave.yaml
```

## Environment Variable Substitution

Reference environment variables in your configuration:

```yaml
model: "${MODEL_NAME}"
api_key_env: "${API_KEY_VAR}"
```

Set environment variables:

```bash
export MODEL_NAME="gpt-4"
export API_KEY_VAR="OPENAI_API_KEY"
weave run config.weave.yaml
```

## Best Practices

1. **Use descriptive agent names**: `code_reviewer` instead of `agent1`
2. **Specify capabilities**: Helps with documentation and tool selection
3. **Set appropriate temperatures**:
   - `0.0-0.3` for factual, deterministic tasks
   - `0.7-0.9` for creative tasks
4. **Enable storage for important agents**: Helps with debugging and audit trails
5. **Use memory for stateful agents**: Especially for conversational or iterative tasks
6. **Provide clear prompts**: Specific instructions lead to better results
7. **Validate configurations**: Always validate before executing in production
8. **Use environment variables**: For sensitive data and environment-specific configs

## Next Steps

- [Tool Calling Guide](../guides/tool-calling.md)
- [MCP Integration Guide](../guides/mcp.md)
- [Testing Guide](../guides/testing.md)
- [Examples](../../examples/)
