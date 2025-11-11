# Environment Setup Guide

This guide explains how to configure API keys for Weave using `.env` files.

## Quick Setup

1. **Copy the example file**:
   ```bash
   cp .agent/.env.example .agent/.env
   ```

2. **Edit `.agent/.env` and add your API keys**:
   ```bash
   nano .agent/.env  # or use your preferred editor
   ```

3. **Add your actual API keys**:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

4. **Run weave** - it will automatically load the keys:
   ```bash
   source .venv/bin/activate
   weave init
   ```

## .env File Location

Weave looks for `.env` files in this order:

1. **`.agent/.env`** (in your project directory) - **Recommended**
2. **`.env`** (in your project root)

## Supported API Keys

### OpenAI (GPT Models)
```bash
OPENAI_API_KEY=sk-proj-xxxxx
```
Get your key: https://platform.openai.com/api-keys

### Anthropic (Claude Models)
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```
Get your key: https://console.anthropic.com/settings/keys

### OpenRouter (Multi-Model Access including Gemini)
```bash
OPENROUTER_API_KEY=sk-or-xxxxx
```
Get your key: https://openrouter.ai/keys

Use OpenRouter to access:
- Google Gemini (`google/gemini-pro`, `google/gemini-1.5-pro`)
- Meta Llama models
- Mistral models
- And many more

### Google (Direct Gemini Access)
```bash
GOOGLE_API_KEY=xxxxx
```
Get your key: https://makersuite.google.com/app/apikey

## Example .agent/.env File

```bash
# OpenAI API Key (for GPT models)
OPENAI_API_KEY=sk-proj-your-key-here

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenRouter API Key (for Gemini and other models)
OPENROUTER_API_KEY=sk-or-your-key-here
```

## Using in Your Agent Config

### With OpenAI:
```yaml
agents:
  my_agent:
    model: "gpt-4"
    # OPENAI_API_KEY will be loaded automatically
```

### With Anthropic:
```yaml
agents:
  my_agent:
    model: "claude-3-opus"
    # ANTHROPIC_API_KEY will be loaded automatically
```

### With Gemini (via OpenRouter):
```yaml
agents:
  my_agent:
    model: "google/gemini-pro"
    # OPENROUTER_API_KEY will be loaded automatically
```

## Security Best Practices

1. **Never commit `.env` files to git**
   - The `.gitignore` already includes `.env` and `.agent/.env`
   - Always use `.env.example` for sharing templates

2. **Keep `.env.example` updated**
   - Add new keys to `.env.example` (with dummy values)
   - Help other developers know what keys are needed

3. **Use different keys for different environments**
   ```bash
   # Development
   .agent/.env

   # Production - use environment variables directly
   export OPENAI_API_KEY="production-key"
   ```

4. **Rotate keys regularly**
   - Change API keys periodically
   - Immediately rotate if keys are exposed

## Troubleshooting

### Keys not being loaded?

1. **Check file location**:
   ```bash
   ls -la .agent/.env
   ```

2. **Check file contents**:
   ```bash
   cat .agent/.env
   ```

3. **Verify no extra spaces**:
   ```bash
   # Correct
   OPENAI_API_KEY=sk-xxxxx

   # Wrong (space before/after =)
   OPENAI_API_KEY = sk-xxxxx
   ```

4. **Test manually**:
   ```bash
   source .venv/bin/activate
   python3 -c "
   from weave.core.env_loader import load_env_file
   load_env_file()
   import os
   print('OpenAI key:', os.getenv('OPENAI_API_KEY')[:15], '...')
   "
   ```

### Still not working?

Set keys directly in your shell:
```bash
export OPENAI_API_KEY="sk-your-key"
weave init
```

## Migration from Old Setup

If you were using the encrypted key manager:

```bash
# Your old keys are still in ~/.weave/api_keys.yaml
# To migrate to .env:

# 1. Create .agent/.env
cp .agent/.env.example .agent/.env

# 2. Add your keys to .agent/.env
nano .agent/.env

# 3. Keys in .env take precedence, encrypted storage is still fallback
```

## Alternative: Environment Variables

You can also set keys as regular environment variables:

```bash
# In ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Reload shell
source ~/.bashrc
```

This is useful for:
- CI/CD environments
- Docker containers
- Production deployments
