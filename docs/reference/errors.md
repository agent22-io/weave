# Error Messages

Common error messages and how to resolve them.

## Configuration Errors

### Config File Not Found

**Error:**
```
Configuration file not found: .weave.yaml
Run 'weave init' to create a new configuration.
```

**Cause:** No `.weave.yaml` file in current directory.

**Solution:**
```bash
# Create new config
weave init

# Or specify config location
weave plan --config /path/to/config.yaml
```

---

### Invalid YAML Syntax

**Error:**
```
Invalid YAML in .weave.yaml:
  line 5, column 3: expected <block end>, but found ':'
```

**Cause:** YAML syntax error (indentation, colons, etc.).

**Solution:**
- Check YAML indentation (use spaces, not tabs)
- Validate YAML with online tools
- Common issues: missing spaces after colons, incorrect nesting

**Example Fix:**

❌ **Before:**
```yaml
agents:
  my_agent:
    model:"gpt-4"        # Missing space after colon
```

✅ **After:**
```yaml
agents:
  my_agent:
    model: "gpt-4"       # Space after colon
```

---

### Missing Required Field

**Error:**
```
Configuration validation failed:
  • agents -> researcher -> model: Field required
```

**Cause:** Required field is missing.

**Solution:** Add the required field:

❌ **Before:**
```yaml
agents:
  researcher:
    tools: [web_search]
    # model missing!
```

✅ **After:**
```yaml
agents:
  researcher:
    model: "gpt-4"
    tools: [web_search]
```

---

### Invalid Agent Reference

**Error:**
```
Agent 'writer' references unknown input agent 'researcher'
```

**Cause:** Agent references another agent that doesn't exist.

**Solution:** Ensure referenced agent is defined:

❌ **Before:**
```yaml
agents:
  writer:
    model: "gpt-4"
    inputs: "researcher"    # researcher not defined!
```

✅ **After:**
```yaml
agents:
  researcher:               # Define researcher
    model: "gpt-4"

  writer:
    model: "gpt-4"
    inputs: "researcher"
```

---

### Weave References Unknown Agent

**Error:**
```
Weave 'pipeline' references unknown agent 'analyzer'
```

**Cause:** Weave includes an agent that isn't defined.

**Solution:** Remove the agent from weave or define it:

❌ **Before:**
```yaml
agents:
  fetcher: {...}

weaves:
  pipeline:
    agents: [fetcher, analyzer]    # analyzer not defined!
```

✅ **After:**
```yaml
agents:
  fetcher: {...}
  analyzer: {...}                  # Define analyzer

weaves:
  pipeline:
    agents: [fetcher, analyzer]
```

---

### Empty Weave

**Error:**
```
Weave must contain at least one agent
```

**Cause:** Weave has an empty agents list.

**Solution:** Add at least one agent:

❌ **Before:**
```yaml
weaves:
  pipeline:
    agents: []            # Empty!
```

✅ **After:**
```yaml
weaves:
  pipeline:
    agents: [my_agent]
```

---

### No Weaves Defined

**Error:**
```
Configuration must define at least one weave
```

**Cause:** Config has no weaves section or it's empty.

**Solution:** Add at least one weave:

❌ **Before:**
```yaml
version: "1.0"
agents:
  my_agent: {...}
# No weaves!
```

✅ **After:**
```yaml
version: "1.0"
agents:
  my_agent: {...}

weaves:
  my_pipeline:
    agents: [my_agent]
```

---

## Graph Errors

### Circular Dependency

**Error:**
```
Circular dependency detected: researcher → writer → researcher
Agents cannot have circular input dependencies.
```

**Cause:** Two or more agents depend on each other, creating a cycle.

**Solution:** Break the circular dependency:

❌ **Before:**
```yaml
agents:
  researcher:
    model: "gpt-4"
    inputs: "writer"      # Circular!

  writer:
    model: "gpt-4"
    inputs: "researcher"  # Circular!
```

✅ **After:**
```yaml
agents:
  researcher:
    model: "gpt-4"
    # No inputs - starts the chain

  writer:
    model: "gpt-4"
    inputs: "researcher"  # Linear: researcher → writer
```

---

### Agent Not in Weave

**Error:**
```
Agent 'writer' depends on 'researcher' which is not part of weave 'quick_flow'
```

**Cause:** Agent depends on another agent not included in the weave.

**Solution:** Add the dependency to the weave:

❌ **Before:**
```yaml
agents:
  researcher: {...}
  writer:
    inputs: "researcher"

weaves:
  quick_flow:
    agents: [writer]      # Missing researcher!
```

✅ **After:**
```yaml
agents:
  researcher: {...}
  writer:
    inputs: "researcher"

weaves:
  quick_flow:
    agents: [researcher, writer]    # Include both
```

---

### Weave Not Found

**Error:**
```
Weave 'production' not found. Available weaves: dev, staging
```

**Cause:** Specified weave doesn't exist in config.

**Solution:** Use an existing weave or add the missing one:

```bash
# List available weaves
weave plan    # Shows available weaves if multiple exist

# Or specify correct weave
weave plan --weave dev
```

---

## Environment Variable Errors

### Environment Variable Not Set

**Error:**
```
Environment variable 'OPENAI_API_KEY' not set
Please set these variables or remove them from your config.
```

**Cause:** Config references an environment variable that isn't set.

**Solution:** Set the environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."

# Or inline
OPENAI_API_KEY="sk-..." weave apply
```

**Alternative:** Remove the variable reference from config:

❌ **Before:**
```yaml
env:
  KEY: "${OPENAI_API_KEY}"    # Not set!
```

✅ **After:**
```yaml
env:
  KEY: "fallback-value"        # Hardcoded (not recommended for secrets)
```

---

## Validation Errors

### Invalid Agent Name

**Error:**
```
Agent name must be alphanumeric with - or _: my agent
```

**Cause:** Agent name contains invalid characters.

**Solution:** Use only alphanumeric characters, hyphens, and underscores:

❌ **Before:**
```yaml
agents:
  my agent: {...}           # Spaces not allowed
  agent@work: {...}         # Special chars not allowed
```

✅ **After:**
```yaml
agents:
  my_agent: {...}           # Underscore OK
  agent-work: {...}         # Hyphen OK
  myAgent: {...}            # CamelCase OK
```

---

## Command Errors

### Command Not Found

**Error:**
```bash
bash: weave: command not found
```

**Cause:** Weave not installed or not in PATH.

**Solution:**

```bash
# Option 1: Use module form
python -m weave plan

# Option 2: Reinstall
pip install -e .

# Option 3: Check PATH
which weave
```

---

### Permission Denied

**Error:**
```
Permission denied: /path/to/output.mmd
```

**Cause:** No write permission for output file/directory.

**Solution:**

```bash
# Ensure directory exists
mkdir -p output/

# Check permissions
ls -la output/

# Use writable location
weave graph --output ~/graphs/diagram.mmd
```

---

## Runtime Errors

### Execution Failed

**Error:**
```
❌ Execution failed: [error details]
```

**Cause:** Error during agent execution (v2.0 with real execution).

**Solution:** Check error details and:
- Verify API keys are set
- Check network connectivity
- Review agent configuration
- Check rate limits

---

## Debugging Tips

### Enable Verbose Output

```bash
weave apply --verbose
```

Shows detailed execution information.

### Validate First

```bash
# Always validate before applying
weave plan

# If plan succeeds, config is valid
```

### Check YAML Syntax

Use online validators:
- [YAML Lint](http://www.yamllint.com/)
- VS Code with YAML extension

### Inspect Graph

```bash
# Visualize dependencies
weave graph

# Check for unexpected relationships
```

### Dry Run

```bash
# Preview execution without running
weave apply --dry-run
```

---

## Getting Help

### Show Help

```bash
weave --help
weave init --help
weave plan --help
weave apply --help
weave graph --help
```

### Report Bugs

Found a bug? Report it at:
- GitHub Issues: [github.com/weave/weave-cli/issues](https://github.com/weave/weave-cli/issues)

Include:
- Weave version (`weave --version`)
- Config file (sanitized, no secrets)
- Full error message
- Steps to reproduce

---

## Next Steps

- [Configuration Reference](configuration.md) - Complete schema
- [CLI Commands](cli-commands.md) - Command documentation
- [Writing Configurations](../guides/writing-configs.md) - Best practices
