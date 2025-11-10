# Dependency Management

Deep dive into managing agent dependencies in Weave.

## Understanding Dependencies

Dependencies define **execution order** by linking agent outputs to inputs.

```yaml
agents:
  A:
    model: "gpt-4"

  B:
    model: "gpt-4"
    inputs: "A"      # B depends on A

# Execution order: A → B
```

---

## Dependency Declaration

### Basic Syntax

```yaml
agents:
  upstream:
    model: "gpt-4"
    outputs: "data"

  downstream:
    model: "gpt-4"
    inputs: "upstream"    # References upstream agent
```

### Alternative Forms

Both forms are equivalent:

```yaml
# Short form (recommended)
inputs: "upstream"

# Explicit form
inputs: "upstream.outputs"
```

Weave normalizes both to the agent name.

---

## Dependency Patterns

### 1. Linear Chain

Simplest pattern - each agent depends on the previous one:

```yaml
agents:
  step1:
    model: "gpt-4"
    outputs: "result1"

  step2:
    model: "gpt-4"
    inputs: "step1"
    outputs: "result2"

  step3:
    model: "gpt-4"
    inputs: "step2"
    outputs: "result3"

  step4:
    model: "gpt-4"
    inputs: "step3"
    outputs: "result4"
```

**Execution:**
```
step1 → step2 → step3 → step4
```

**Use Cases:**
- Sequential processing
- Data transformations
- Multi-stage pipelines

---

### 2. Fan-Out (One-to-Many)

One agent feeds multiple independent agents:

```yaml
agents:
  source:
    model: "gpt-4"
    outputs: "raw_data"

  analyzer_a:
    model: "gpt-4"
    inputs: "source"
    outputs: "analysis_a"

  analyzer_b:
    model: "gpt-4"
    inputs: "source"
    outputs: "analysis_b"

  analyzer_c:
    model: "gpt-4"
    inputs: "source"
    outputs: "analysis_c"
```

**Execution:**
```
        ┌→ analyzer_a
source ─┼→ analyzer_b
        └→ analyzer_c
```

**Use Cases:**
- Parallel analysis
- Multiple perspectives
- A/B testing different approaches

**Note:** v0.1.0 executes sequentially. v2.0 will support true parallel execution.

---

### 3. Fan-In (Many-to-One)

Multiple agents feed into one agent:

```yaml
agents:
  source_a:
    model: "gpt-4"
    outputs: "data_a"

  source_b:
    model: "gpt-4"
    outputs: "data_b"

  source_c:
    model: "gpt-4"
    outputs: "data_c"

  # Note: v0.1.0 supports single input
  # Specify primary input, others contextual
  merger:
    model: "gpt-4"
    inputs: "source_a"      # Primary input
    outputs: "merged"
```

**Execution:**
```
source_a ─┐
source_b ─┼→ merger
source_c ─┘
```

**Use Cases:**
- Data aggregation
- Multi-source synthesis
- Consensus building

**v2.0 Enhancement:** Will support multiple inputs explicitly:
```yaml
# Future syntax
merger:
  inputs: [source_a, source_b, source_c]
```

---

### 4. Diamond Pattern

Parallel processing that converges:

```yaml
agents:
  start:
    model: "gpt-4"

  branch_a:
    model: "gpt-4"
    inputs: "start"

  branch_b:
    model: "gpt-4"
    inputs: "start"

  merge:
    model: "gpt-4"
    inputs: "branch_a"    # Primary, but aware of branch_b
```

**Execution:**
```
        ┌→ branch_a ─┐
start ──┤            ├→ merge
        └→ branch_b ─┘
```

**Use Cases:**
- Compare different approaches
- Validation from multiple angles
- Ensemble methods

---

### 5. Layered Pipeline

Multiple stages with fan-out/fan-in:

```yaml
agents:
  # Stage 1: Data collection
  collector:
    model: "gpt-4"

  # Stage 2: Parallel processing
  processor_a:
    model: "gpt-4"
    inputs: "collector"

  processor_b:
    model: "gpt-4"
    inputs: "collector"

  # Stage 3: Synthesis
  synthesizer:
    model: "claude-3-opus"
    inputs: "processor_a"    # Primary

  # Stage 4: Final output
  reporter:
    model: "gpt-4"
    inputs: "synthesizer"
```

**Execution:**
```
                ┌→ processor_a ─┐
collector ──────┤               ├→ synthesizer ──→ reporter
                └→ processor_b ─┘
```

---

## Dependency Graph Visualization

### View Dependencies

```bash
# ASCII visualization
weave graph

# Mermaid diagram
weave graph --format mermaid
```

### Example Output

```
       ┌──────────────┐
       │   collector  │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │  processor   │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │   reporter   │
       └──────────────┘
```

---

## Dependency Rules

### 1. No Circular Dependencies

❌ **Invalid - creates cycle:**
```yaml
agents:
  A:
    inputs: "B"

  B:
    inputs: "A"    # Error: A → B → A
```

**Error:**
```
Circular dependency detected: A → B → A
Agents cannot have circular input dependencies.
```

---

### 2. Referenced Agents Must Exist

❌ **Invalid - agent doesn't exist:**
```yaml
agents:
  writer:
    inputs: "researcher"    # Error: researcher not defined
```

**Error:**
```
Agent 'writer' references unknown input agent 'researcher'
```

✅ **Valid:**
```yaml
agents:
  researcher:
    model: "gpt-4"

  writer:
    inputs: "researcher"
    model: "gpt-4"
```

---

### 3. Dependencies Must Be in Same Weave

❌ **Invalid - dependency outside weave:**
```yaml
agents:
  A: {...}
  B:
    inputs: "A"

weaves:
  my_flow:
    agents: [B]    # Error: B depends on A, which isn't included
```

**Error:**
```
Agent 'B' depends on 'A' which is not part of weave 'my_flow'
```

✅ **Valid:**
```yaml
weaves:
  my_flow:
    agents: [A, B]    # Include both
```

---

## Execution Order

### Topological Sorting

Weave automatically determines execution order using topological sort:

```yaml
agents:
  C:
    inputs: "B"

  A:
    # No dependencies

  B:
    inputs: "A"

  D:
    inputs: "C"
```

**Declared order:** C, A, B, D

**Execution order:** A → B → C → D

The dependency graph, not declaration order, determines execution.

---

## Independent Agents

### No Dependencies

Agents without dependencies run first:

```yaml
agents:
  independent1:
    model: "gpt-4"
    # No inputs

  independent2:
    model: "gpt-4"
    # No inputs

  dependent:
    model: "gpt-4"
    inputs: "independent1"
```

**Execution:**
```
independent1 → dependent
independent2 (runs first, no dependents)
```

---

## Practical Examples

### Example 1: Content Creation

```yaml
agents:
  # Research phase
  topic_research:
    model: "gpt-4"
    tools: [web_search]
    outputs: "research_notes"

  # Planning phase
  outline_creator:
    model: "gpt-4"
    inputs: "topic_research"
    outputs: "content_outline"

  # Writing phase
  draft_writer:
    model: "claude-3-opus"
    inputs: "outline_creator"
    outputs: "first_draft"

  # Review phase - parallel
  fact_checker:
    model: "gpt-4"
    inputs: "draft_writer"
    tools: [fact_checker]
    outputs: "fact_check_report"

  style_checker:
    model: "gpt-4"
    inputs: "draft_writer"
    tools: [style_guide]
    outputs: "style_report"

  # Revision phase
  editor:
    model: "gpt-4"
    inputs: "fact_checker"    # Primary, uses style_checker contextually
    outputs: "final_content"

weaves:
  content_pipeline:
    agents:
      - topic_research
      - outline_creator
      - draft_writer
      - fact_checker
      - style_checker
      - editor
```

**Flow:**
```
topic_research
      ↓
outline_creator
      ↓
draft_writer
      ├→ fact_checker ─┐
      └→ style_checker─┘
              ↓
          editor
```

---

### Example 2: Data Analysis

```yaml
agents:
  # Data collection
  data_fetcher:
    model: "gpt-3.5-turbo"
    tools: [api_client]

  # Parallel processing
  statistical_analyzer:
    model: "gpt-4"
    inputs: "data_fetcher"
    tools: [statistical_tools]

  pattern_detector:
    model: "gpt-4"
    inputs: "data_fetcher"
    tools: [ml_models]

  anomaly_detector:
    model: "gpt-4"
    inputs: "data_fetcher"
    tools: [anomaly_detection]

  # Synthesis
  insight_generator:
    model: "claude-3-opus"
    inputs: "statistical_analyzer"    # Primary

  # Reporting
  report_builder:
    model: "gpt-4"
    inputs: "insight_generator"
    tools: [chart_generator]

weaves:
  analysis:
    agents:
      - data_fetcher
      - statistical_analyzer
      - pattern_detector
      - anomaly_detector
      - insight_generator
      - report_builder
```

---

## Best Practices

### 1. Keep Dependencies Clear

✅ **Good - obvious flow:**
```yaml
agents:
  fetch:
    model: "gpt-4"

  clean:
    model: "gpt-4"
    inputs: "fetch"

  analyze:
    model: "gpt-4"
    inputs: "clean"
```

❌ **Bad - unclear flow:**
```yaml
agents:
  step1:
    inputs: "step3"

  step2:
    inputs: "step1"

  step3:
    model: "gpt-4"
```

### 2. Name Dependencies Meaningfully

✅ **Good:**
```yaml
agents:
  data_validator:
    inputs: "data_collector"
```

❌ **Bad:**
```yaml
agents:
  agent2:
    inputs: "agent1"
```

### 3. Visualize Complex Graphs

```bash
# Always visualize complex pipelines
weave graph --format mermaid --output pipeline.mmd
```

### 4. Test Incrementally

```bash
# Test first agent
weave apply --weave test_step1

# Add second agent
weave apply --weave test_step1_and_2

# Continue building
```

---

## Troubleshooting

### Circular Dependencies

**Detection:**
```bash
weave plan
# Error: Circular dependency detected: A → B → A
```

**Solution:** Break the cycle by removing one dependency.

### Missing Dependencies

**Detection:**
```bash
weave plan
# Error: Agent 'B' references unknown input 'A'
```

**Solution:** Add the missing agent or fix the reference.

### Wrong Execution Order

**Check order:**
```bash
weave plan
# Shows: Execution order: ...
```

**Fix:** Adjust dependencies to achieve desired order.

---

## Next Steps

- [Writing Configurations](writing-configs.md) - Best practices
- [Configuration Reference](../reference/configuration.md) - Complete schema
- [Visualization Guide](visualization.md) - Working with graphs
