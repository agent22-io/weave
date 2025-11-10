# Environment Variables

Using environment variables in Weave configurations for flexibility and security.

## Why Use Environment Variables?

1. **Security** - Keep secrets out of config files
2. **Flexibility** - Same config, different environments
3. **Portability** - Easy to share configs without exposing secrets

---

## Basic Syntax

Use `${VARIABLE_NAME}` to reference environment variables:

```yaml
env:
  MY_VAR: "${SHELL_VAR}"

agents:
  my_agent:
    model: "${MY_VAR}"
```

---

## Setting Environment Variables

### Linux / macOS

```bash
# Set for current session
export MODEL="gpt-4"
export API_KEY="sk-..."

# Run weave
weave apply

# Or inline
MODEL=gpt-4 weave apply
```

### Windows PowerShell

```powershell
# Set for current session
$env:MODEL="gpt-4"
$env:API_KEY="sk-..."

# Run weave
weave apply
```

### Windows Command Prompt

```cmd
set MODEL=gpt-4
set API_KEY=sk-...
weave apply
```

---

## Common Use Cases

### 1. API Keys

❌ **Bad - hardcoded:**
```yaml
agents:
  my_agent:
    config:
      api_key: "sk-1234567890"    # DON'T DO THIS!
```

✅ **Good - from environment:**
```yaml
env:
  API_KEY: "${OPENAI_API_KEY}"

agents:
  my_agent:
    config:
      api_key: "${API_KEY}"
```

### 2. Model Selection

```yaml
env:
  DEFAULT_MODEL: "${MODEL:-gpt-4}"    # Default to gpt-4

agents:
  agent1:
    model: "${DEFAULT_MODEL}"

  agent2:
    model: "${DEFAULT_MODEL}"
```

Usage:
```bash
# Use default (gpt-4)
weave apply

# Override with env var
MODEL=gpt-3.5-turbo weave apply

# Or export
export MODEL=claude-3-opus
weave apply
```

### 3. Environment-Specific Settings

```yaml
env:
  ENV: "${ENVIRONMENT:-dev}"
  LOG_LEVEL: "${LOG_LEVEL:-info}"
  MAX_TOKENS: "${MAX_TOKENS:-1000}"

agents:
  my_agent:
    model: "gpt-4"
    config:
      max_tokens: "${MAX_TOKENS}"
```

Usage:
```bash
# Development
ENVIRONMENT=dev LOG_LEVEL=debug weave apply

# Production
ENVIRONMENT=prod LOG_LEVEL=error MAX_TOKENS=2000 weave apply
```

---

## Default Values

### Syntax

```yaml
env:
  VAR: "${SHELL_VAR:-default_value}"
```

If `SHELL_VAR` is not set, uses `default_value`.

### Example

```yaml
env:
  MODEL: "${MODEL:-gpt-4}"
  TEMP: "${TEMPERATURE:-0.7}"
  TOKENS: "${MAX_TOKENS:-1000}"

agents:
  my_agent:
    model: "${MODEL}"
    config:
      temperature: "${TEMP}"
      max_tokens: "${TOKENS}"
```

All variables have defaults, so config works even without setting env vars.

---

## Environment Files

### .env File (Not Directly Supported)

Weave doesn't directly load `.env` files, but you can use tools like `direnv` or `dotenv`:

#### Using direnv

```bash
# Install direnv
brew install direnv  # macOS
apt install direnv   # Linux

# Create .envrc
cat > .envrc <<EOF
export OPENAI_API_KEY="sk-..."
export MODEL="gpt-4"
EOF

# Allow direnv
direnv allow

# Now weave will use these vars
weave apply
```

#### Using dotenv (Python)

```bash
# Install python-dotenv
pip install python-dotenv

# Create .env file
cat > .env <<EOF
OPENAI_API_KEY=sk-...
MODEL=gpt-4
EOF

# Load and run
python -c "from dotenv import load_dotenv; load_dotenv()" && weave apply
```

#### Using source

```bash
# Create env.sh
cat > env.sh <<EOF
export OPENAI_API_KEY="sk-..."
export MODEL="gpt-4"
export TEMPERATURE="0.7"
EOF

# Load and run
source env.sh && weave apply
```

---

## Multi-Environment Setup

### Directory Structure

```
project/
├── .weave.yaml           # Main config
├── env/
│   ├── dev.env          # Development vars
│   ├── staging.env      # Staging vars
│   └── prod.env         # Production vars
└── README.md
```

### env/dev.env

```bash
export MODEL="gpt-3.5-turbo"
export TEMPERATURE="1.0"
export MAX_TOKENS="500"
export LOG_LEVEL="debug"
```

### env/staging.env

```bash
export MODEL="gpt-4"
export TEMPERATURE="0.7"
export MAX_TOKENS="1000"
export LOG_LEVEL="info"
```

### env/prod.env

```bash
export MODEL="gpt-4"
export TEMPERATURE="0.3"
export MAX_TOKENS="2000"
export LOG_LEVEL="error"
```

### Usage

```bash
# Development
source env/dev.env && weave apply

# Staging
source env/staging.env && weave apply

# Production
source env/prod.env && weave apply
```

---

## Security Best Practices

### 1. Never Commit Secrets

```bash
# Add to .gitignore
echo "*.env" >> .gitignore
echo ".envrc" >> .gitignore
echo "env/" >> .gitignore
```

### 2. Use Secret Management

**AWS Secrets Manager:**
```bash
export API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id openai-api-key \
  --query SecretString \
  --output text)

weave apply
```

**Azure Key Vault:**
```bash
export API_KEY=$(az keyvault secret show \
  --name openai-api-key \
  --vault-name my-vault \
  --query value -o tsv)

weave apply
```

**HashiCorp Vault:**
```bash
export API_KEY=$(vault kv get -field=key secret/openai)
weave apply
```

### 3. Use Environment-Specific Configs

```bash
# Development - local config
weave apply --config dev.yaml

# Production - separate config
weave apply --config prod.yaml
```

---

## Validation

### Check Missing Variables

Weave validates env vars when loading config:

```yaml
env:
  API_KEY: "${OPENAI_API_KEY}"
```

If `OPENAI_API_KEY` is not set:

```
Error: Environment variable 'OPENAI_API_KEY' not set
Please set these variables or remove them from your config.
```

### Check Current Variables

```bash
# List all environment variables
env | grep -i model
env | grep -i api

# Check specific variable
echo $OPENAI_API_KEY
echo $MODEL
```

---

## Advanced Patterns

### Conditional Configuration

```yaml
env:
  IS_DEV: "${DEV:-false}"
  MODEL: "${DEV:+gpt-3.5-turbo}"    # If DEV set, use gpt-3.5-turbo

agents:
  my_agent:
    model: "${MODEL:-gpt-4}"
```

### Computed Values

```yaml
env:
  ENV: "${ENVIRONMENT}"
  CONFIG_PATH: "/config/${ENV}"
  LOG_FILE: "/logs/${ENV}-weave.log"
```

### Nested References

```yaml
env:
  BASE_MODEL: "${MODEL:-gpt-4}"
  FAST_MODEL: "${FAST_MODEL:-gpt-3.5-turbo}"

agents:
  slow_agent:
    model: "${BASE_MODEL}"

  fast_agent:
    model: "${FAST_MODEL}"
```

---

## Troubleshooting

### Variable Not Expanding

**Problem:**
```yaml
env:
  MODEL: ${OPENAI_MODEL}    # Missing quotes!
```

**Solution:**
```yaml
env:
  MODEL: "${OPENAI_MODEL}"   # Add quotes
```

### Empty Value

Check if variable is set:

```bash
# Check
echo "${OPENAI_API_KEY:-NOT SET}"

# Set if empty
export OPENAI_API_KEY="sk-..."
```

### Wrong Variable Name

```bash
# Typo in config
env:
  KEY: "${OPENAPI_KEY}"      # Should be OPENAI_API_KEY

# Error shows variable name
Error: Environment variable 'OPENAPI_KEY' not set
```

---

## Examples

### Example 1: Simple API Key

```yaml
version: "1.0"

env:
  API_KEY: "${OPENAI_API_KEY}"

agents:
  my_agent:
    model: "gpt-4"
    config:
      api_key: "${API_KEY}"

weaves:
  simple:
    agents: [my_agent]
```

```bash
export OPENAI_API_KEY="sk-..."
weave apply
```

### Example 2: Multi-Environment

```yaml
version: "1.0"

env:
  ENV: "${ENVIRONMENT:-dev}"
  MODEL: "${MODEL:-gpt-4}"
  TEMP: "${TEMPERATURE:-0.7}"
  TOKENS: "${MAX_TOKENS:-1000}"

agents:
  processor:
    model: "${MODEL}"
    config:
      temperature: "${TEMP}"
      max_tokens: "${TOKENS}"
      environment: "${ENV}"

weaves:
  pipeline:
    agents: [processor]
```

```bash
# Development
ENVIRONMENT=dev MODEL=gpt-3.5-turbo weave apply

# Production
ENVIRONMENT=prod MODEL=gpt-4 TEMPERATURE=0.3 weave apply
```

### Example 3: Complete Setup

```yaml
version: "1.0"

env:
  # API Configuration
  OPENAI_KEY: "${OPENAI_API_KEY}"
  ANTHROPIC_KEY: "${ANTHROPIC_API_KEY}"

  # Model Selection
  GPT_MODEL: "${GPT_MODEL:-gpt-4}"
  CLAUDE_MODEL: "${CLAUDE_MODEL:-claude-3-opus}"

  # Performance Tuning
  DEFAULT_TEMP: "${TEMPERATURE:-0.7}"
  MAX_TOKENS: "${MAX_TOKENS:-2000}"

  # Environment
  ENV_NAME: "${ENVIRONMENT:-development}"
  LOG_LEVEL: "${LOG_LEVEL:-info}"

agents:
  gpt_agent:
    model: "${GPT_MODEL}"
    config:
      api_key: "${OPENAI_KEY}"
      temperature: "${DEFAULT_TEMP}"
      max_tokens: "${MAX_TOKENS}"

  claude_agent:
    model: "${CLAUDE_MODEL}"
    inputs: "gpt_agent"
    config:
      api_key: "${ANTHROPIC_KEY}"
      temperature: "${DEFAULT_TEMP}"
      max_tokens: "${MAX_TOKENS}"

weaves:
  multi_model:
    description: "Multi-model pipeline using both OpenAI and Anthropic"
    agents: [gpt_agent, claude_agent]
```

```bash
# Set all variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export ENVIRONMENT="production"
export TEMPERATURE="0.5"
export MAX_TOKENS="3000"

# Run
weave apply
```

---

## Next Steps

- [Writing Configurations](writing-configs.md) - Best practices
- [Configuration Reference](../reference/configuration.md) - Complete schema
- [Error Messages](../reference/errors.md) - Troubleshooting
