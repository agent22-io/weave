# Writing Configurations

Best practices and patterns for writing effective Weave configurations.

## Start Simple

Begin with a minimal config and expand incrementally.

### Minimal Example

```yaml
version: "1.0"

agents:
  agent1:
    model: "gpt-4"

weaves:
  simple:
    agents: [agent1]
```

### Test Early

```bash
# Validate config
weave plan

# If valid, expand
```

---

## Naming Conventions

### Use Descriptive Names

✅ **Good - Clear purpose:**
```yaml
agents:
  web_scraper:
    model: "gpt-4"

  data_cleaner:
    model: "gpt-4"

  report_generator:
    model: "claude-3-opus"
```

❌ **Bad - Generic names:**
```yaml
agents:
  agent1:
    model: "gpt-4"

  agent2:
    model: "gpt-4"

  agent3:
    model: "claude-3-opus"
```

### Naming Patterns

**Action-based names:**
```yaml
agents:
  fetch_data:       # What it does
  process_data:
  analyze_results:
```

**Role-based names:**
```yaml
agents:
  researcher:       # Its role
  writer:
  editor:
```

**Domain-specific names:**
```yaml
agents:
  sql_query_generator:
  api_client:
  json_parser:
```

---

## Organizing Agents

### Group by Function

```yaml
agents:
  # Data Collection
  web_scraper: {...}
  api_fetcher: {...}

  # Data Processing
  cleaner: {...}
  validator: {...}

  # Analysis
  analyzer: {...}
  summarizer: {...}

  # Output
  formatter: {...}
  reporter: {...}
```

### Use Comments

```yaml
agents:
  # Step 1: Gather raw data from multiple sources
  data_collector:
    model: "gpt-4"
    tools: [web_search, api_client]

  # Step 2: Clean and normalize the collected data
  data_processor:
    model: "gpt-4"
    inputs: "data_collector"
    tools: [validator, normalizer]

  # Step 3: Generate insights from processed data
  insight_generator:
    model: "claude-3-opus"
    inputs: "data_processor"
    tools: [statistical_analyzer]
```

---

## Dependency Patterns

### Linear Pipeline

Simple chain of dependencies:

```yaml
agents:
  step1:
    model: "gpt-4"

  step2:
    model: "gpt-4"
    inputs: "step1"

  step3:
    model: "gpt-4"
    inputs: "step2"

  step4:
    model: "gpt-4"
    inputs: "step3"

# Execution: step1 → step2 → step3 → step4
```

### Branching Pipeline

Multiple agents depend on same source:

```yaml
agents:
  source:
    model: "gpt-4"

  branch_a:
    model: "gpt-4"
    inputs: "source"

  branch_b:
    model: "gpt-4"
    inputs: "source"

  branch_c:
    model: "gpt-4"
    inputs: "source"

# Execution: source → (branch_a, branch_b, branch_c)
```

### Converging Pipeline

Multiple sources feed into one agent:

```yaml
agents:
  source_a:
    model: "gpt-4"

  source_b:
    model: "gpt-4"

  # Note: In v0.1.0, only one input is supported
  # Use primary input, others can be added in v2.0
  merger:
    model: "gpt-4"
    inputs: "source_a"

# Execution: (source_a, source_b) → merger
```

---

## Configuration Strategies

### Environment-Specific Configs

**Development:**
```yaml
# dev.yaml
version: "1.0"

env:
  MODEL: "gpt-3.5-turbo"     # Cheaper for dev
  LOG_LEVEL: "debug"

agents:
  my_agent:
    model: "${MODEL}"
    config:
      temperature: 1.0         # Higher randomness for testing
```

**Production:**
```yaml
# prod.yaml
version: "1.0"

env:
  MODEL: "gpt-4"             # Production model
  LOG_LEVEL: "error"

agents:
  my_agent:
    model: "${MODEL}"
    config:
      temperature: 0.3       # Lower randomness for consistency
```

Usage:
```bash
weave apply --config dev.yaml
weave apply --config prod.yaml
```

---

## Model Selection

### Choose by Task Type

**Creative Tasks (high temperature):**
```yaml
agents:
  creative_writer:
    model: "claude-3-opus"
    config:
      temperature: 0.9       # High creativity
      max_tokens: 3000
```

**Analytical Tasks (low temperature):**
```yaml
agents:
  data_analyzer:
    model: "gpt-4"
    config:
      temperature: 0.2       # Low variance
      max_tokens: 1000
```

**Balanced Tasks:**
```yaml
agents:
  content_editor:
    model: "gpt-4"
    config:
      temperature: 0.5       # Balanced
      max_tokens: 2000
```

---

## Tool Organization

### Minimal Tool Sets

Only include needed tools:

✅ **Good:**
```yaml
agents:
  web_researcher:
    model: "gpt-4"
    tools:
      - web_search
      - summarizer

  code_analyzer:
    model: "gpt-4"
    tools:
      - ast_parser
      - linter
```

❌ **Bad:**
```yaml
agents:
  web_researcher:
    model: "gpt-4"
    tools:
      - web_search
      - summarizer
      - calculator
      - file_reader
      - sql_client      # Unnecessary tools!
```

### Shared Tool Patterns

Common tool combinations:

```yaml
agents:
  researcher:
    tools: [web_search, summarizer, fact_checker]

  writer:
    tools: [text_generator, grammar_checker, style_guide]

  coder:
    tools: [code_generator, syntax_checker, test_runner]

  analyst:
    tools: [statistical_analyzer, chart_generator, report_builder]
```

---

## Multiple Weaves

### Organize by Use Case

```yaml
agents:
  fetch: {...}
  clean: {...}
  analyze: {...}
  report: {...}

weaves:
  # Quick check - minimal processing
  quick:
    description: "Fast data validation"
    agents: [fetch, clean]

  # Standard flow - full processing
  standard:
    description: "Complete analysis pipeline"
    agents: [fetch, clean, analyze]

  # Full report - everything
  full:
    description: "Comprehensive analysis with reporting"
    agents: [fetch, clean, analyze, report]
```

Usage:
```bash
weave apply --weave quick      # Fast
weave apply --weave standard   # Normal
weave apply --weave full       # Complete
```

---

## Output Naming

### Explicit Output Names

```yaml
agents:
  researcher:
    model: "gpt-4"
    outputs: "market_research"     # Clear name

  analyzer:
    model: "gpt-4"
    inputs: "researcher"
    outputs: "trend_analysis"      # Descriptive

  reporter:
    model: "gpt-4"
    inputs: "analyzer"
    outputs: "executive_summary"   # Purpose-based
```

### Default Naming

Let Weave generate names:

```yaml
agents:
  researcher:
    model: "gpt-4"
    # outputs: "researcher_output" (default)

  analyzer:
    model: "gpt-4"
    inputs: "researcher"
    # outputs: "analyzer_output" (default)
```

---

## Documentation

### Add Descriptions

```yaml
weaves:
  etl_pipeline:
    description: |
      Extract data from API endpoints, transform using GPT-4,
      load results into database, and generate analytics report.
      Expected runtime: ~5 minutes.
    agents: [...]
```

### Inline Comments

```yaml
agents:
  processor:
    model: "gpt-4"
    tools:
      - data_cleaner      # Removes duplicates and null values
      - validator         # Checks data types and constraints
      - normalizer        # Converts to standard format
    config:
      temperature: 0.1    # Low variance for consistent processing
      max_tokens: 500     # Short outputs for structured data
```

---

## Security Best Practices

### Never Hardcode Secrets

❌ **Bad:**
```yaml
agents:
  my_agent:
    config:
      api_key: "sk-1234567890abcdef"    # DON'T DO THIS!
```

✅ **Good:**
```yaml
env:
  API_KEY: "${OPENAI_API_KEY}"          # From environment

agents:
  my_agent:
    config:
      api_key: "${API_KEY}"
```

### Use .gitignore

```bash
# Don't commit configs with secrets
echo ".weave.local.yaml" >> .gitignore
```

---

## Testing Strategies

### Incremental Testing

```bash
# 1. Validate syntax
weave plan

# 2. Preview execution
weave apply --dry-run

# 3. Run verbose
weave apply --verbose

# 4. Production run
weave apply
```

### Modular Testing

Test agents individually before combining:

```yaml
# test-agent1.yaml
agents:
  agent1: {...}

weaves:
  test:
    agents: [agent1]
```

```bash
# Test each agent
weave apply --config test-agent1.yaml
weave apply --config test-agent2.yaml

# Then combine
weave apply --config full-pipeline.yaml
```

---

## Performance Tips

### Optimize Agent Order

Put fast agents first:

✅ **Good:**
```yaml
# Quick validation before expensive processing
agents:
  validator:              # Fast (< 1s)
    model: "gpt-3.5-turbo"

  processor:              # Expensive (> 5s)
    model: "gpt-4"
    inputs: "validator"
```

❌ **Bad:**
```yaml
# Expensive processing before validation
agents:
  processor:              # Runs even if validation would fail
    model: "gpt-4"

  validator:
    model: "gpt-3.5-turbo"
    inputs: "processor"
```

---

## Common Patterns

### ETL Pipeline

```yaml
agents:
  extract:
    model: "gpt-3.5-turbo"
    tools: [api_client, web_scraper]

  transform:
    model: "gpt-4"
    inputs: "extract"
    tools: [data_cleaner, normalizer]

  load:
    model: "gpt-3.5-turbo"
    inputs: "transform"
    tools: [database_client]

weaves:
  etl:
    description: "Extract, transform, and load data"
    agents: [extract, transform, load]
```

### Research Pipeline

```yaml
agents:
  literature_review:
    model: "gpt-4"
    tools: [academic_search, pdf_reader]

  data_collection:
    model: "gpt-4"
    tools: [web_scraper, api_client]

  synthesis:
    model: "claude-3-opus"
    inputs: "literature_review"
    tools: [summarizer, citation_manager]

  peer_review:
    model: "gpt-4"
    inputs: "synthesis"
    tools: [fact_checker, citation_validator]

weaves:
  research:
    description: "Academic research workflow"
    agents: [literature_review, data_collection, synthesis, peer_review]
```

### Content Pipeline

```yaml
agents:
  research:
    model: "gpt-4"
    tools: [web_search, fact_checker]

  outline:
    model: "gpt-4"
    inputs: "research"

  draft:
    model: "claude-3-opus"
    inputs: "outline"
    tools: [text_generator]

  edit:
    model: "gpt-4"
    inputs: "draft"
    tools: [grammar_checker, style_guide]

  seo_optimize:
    model: "gpt-3.5-turbo"
    inputs: "edit"
    tools: [keyword_analyzer, meta_generator]

weaves:
  content:
    description: "Content creation workflow"
    agents: [research, outline, draft, edit, seo_optimize]
```

---

## Next Steps

- [Dependency Management](dependencies.md) - Advanced dependency patterns
- [Environment Variables](environment.md) - Managing environments
- [Configuration Reference](../reference/configuration.md) - Complete schema
