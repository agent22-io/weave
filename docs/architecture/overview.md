# Architecture Overview

Understanding Weave's internal architecture and design principles.

## Design Principles

### 1. Modularity

Each layer has a single responsibility:
- **CLI** - User interaction
- **Parser** - Configuration loading
- **Core** - Business logic
- **Runtime** - Execution

### 2. Extensibility

Hook points for future features:
- Executor hooks
- Custom validators
- Plugin system (planned)

### 3. Type Safety

Strong typing throughout:
- Pydantic models for validation
- Type hints in all functions
- Runtime type checking

### 4. User Experience

Clear, helpful output:
- Descriptive error messages
- Beautiful terminal formatting
- Progress indicators

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      CLI Layer                          │
│                    (Typer + Rich)                       │
│  • Command parsing                                      │
│  • User interaction                                     │
│  • Output formatting                                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Parser Layer                          │
│                 (PyYAML + Regex)                        │
│  • YAML loading                                         │
│  • Environment variable substitution                    │
│  • Raw data → Python objects                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    Core Layer                           │
│              (Pydantic + NetworkX)                      │
│  • Schema validation                                    │
│  • Dependency graph construction                        │
│  • Topological sorting                                  │
│  • Business logic                                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Runtime Layer                          │
│                (Mock Executor)                          │
│  • Agent execution (mocked in v0.1.0)                   │
│  • Output collection                                    │
│  • Hook system                                          │
│  • Execution tracking                                   │
└─────────────────────────────────────────────────────────┘
```

---

## Layer Details

### CLI Layer (`src/weave/cli/`)

**Responsibilities:**
- Parse command-line arguments
- Route to appropriate handlers
- Format output for terminal
- Handle user errors gracefully

**Key Files:**
- `app.py` - Typer application and commands
- `output.py` - Rich formatting utilities

**Technologies:**
- **Typer** - CLI framework
- **Rich** - Terminal formatting

**Entry Point:**
```python
# src/weave/cli/app.py
import typer
app = typer.Typer()

@app.command()
def init(): ...

@app.command()
def plan(): ...

@app.command()
def apply(): ...

@app.command()
def graph(): ...
```

---

### Parser Layer (`src/weave/parser/`)

**Responsibilities:**
- Load YAML files safely
- Substitute environment variables
- Handle missing files
- Provide clear parse errors

**Key Files:**
- `config.py` - YAML configuration loader
- `env.py` - Environment variable substitution

**Technologies:**
- **PyYAML** - YAML parsing
- **Regex** - Variable substitution

**Flow:**
```python
# Load file
raw_yaml = open(path).read()

# Substitute env vars
processed = substitute_env_vars(raw_yaml)

# Parse YAML
data = yaml.safe_load(processed)

# Validate with Pydantic
config = WeaveConfig(**data)
```

---

### Core Layer (`src/weave/core/`)

**Responsibilities:**
- Define data models
- Validate configurations
- Build dependency graphs
- Detect cycles
- Sort execution order

**Key Files:**
- `models.py` - Pydantic models (Agent, Weave, WeaveConfig)
- `graph.py` - Dependency graph builder
- `exceptions.py` - Custom exceptions
- `validator.py` - Additional validation logic (future)

**Technologies:**
- **Pydantic** - Data validation
- **NetworkX** - Graph algorithms

**Data Models:**
```python
class Agent(BaseModel):
    name: str
    model: str
    tools: List[str]
    inputs: Optional[str]
    outputs: Optional[str]
    config: Dict[str, Any]

class Weave(BaseModel):
    name: str
    description: str
    agents: List[str]

class WeaveConfig(BaseModel):
    version: str
    env: Dict[str, str]
    agents: Dict[str, Agent]
    weaves: Dict[str, Weave]
```

**Graph Building:**
```python
# Create directed graph
graph = nx.DiGraph()

# Add nodes (agents)
for name, agent in agents.items():
    graph.add_node(name, agent=agent)

# Add edges (dependencies)
for name, agent in agents.items():
    if agent.inputs:
        graph.add_edge(agent.inputs, name)

# Validate (no cycles)
if not nx.is_directed_acyclic_graph(graph):
    raise GraphError("Circular dependency")

# Sort topologically
order = nx.topological_sort(graph)
```

---

### Runtime Layer (`src/weave/runtime/`)

**Responsibilities:**
- Execute agents (mocked in v0.1.0)
- Manage execution flow
- Collect outputs
- Call hooks
- Track progress

**Key Files:**
- `executor.py` - Execution engine
- `hooks.py` - Extension hooks

**Technologies:**
- **Rich** - Progress output
- **Time** - Execution simulation

**Execution Flow:**
```python
# Get execution order
order = graph.get_execution_order()

# Execute each agent
for agent_name in order:
    agent = graph.get_agent(agent_name)

    # Get input from previous agent
    upstream = outputs.get(agent.inputs)

    # Execute (mocked)
    output = executor.execute_agent(agent, upstream)

    # Store output
    outputs[agent_name] = output
```

---

## Data Flow

### 1. Command Execution

```
User runs:
  $ weave apply

CLI Layer:
  ↓ Parse arguments
  ↓ Load config path

Parser Layer:
  ↓ Read .weave.yaml
  ↓ Substitute env vars
  ↓ Parse YAML

Core Layer:
  ↓ Validate schema
  ↓ Build dependency graph
  ↓ Check for cycles
  ↓ Sort execution order

Runtime Layer:
  ↓ Execute agents
  ↓ Collect outputs
  ↓ Return summary

CLI Layer:
  ↓ Format output
  ↓ Display to user
```

### 2. Error Handling

```
Error occurs at any layer:
  ↓
Custom exception raised:
  - ConfigError
  - GraphError
  - ExecutionError
  ↓
CLI catches exception:
  ↓
Pretty error message displayed:
  ╭─ Error ─╮
  │ Message │
  ╰─────────╯
  ↓
Exit with code 1
```

---

## Key Classes

### WeaveConfig

**Purpose:** Root configuration model

**Validation:**
- All agents defined
- All weaves reference valid agents
- Dependencies exist
- No circular references

**Usage:**
```python
config = WeaveConfig(**yaml_data)
# Fully validated and ready to use
```

### DependencyGraph

**Purpose:** Build and analyze agent dependencies

**Methods:**
- `build(weave_name)` - Construct graph
- `validate()` - Check for cycles
- `get_execution_order()` - Topological sort
- `to_ascii()` - ASCII visualization
- `to_mermaid()` - Mermaid diagram

**Usage:**
```python
graph = DependencyGraph(config)
graph.build("my_weave")
graph.validate()
order = graph.get_execution_order()
```

### MockExecutor

**Purpose:** Execute agent flow (mocked in v0.1.0)

**Methods:**
- `execute_agent(agent, inputs)` - Execute single agent
- `execute_flow(graph, weave_name)` - Execute entire flow
- `register_hook(hook)` - Add execution hook

**Usage:**
```python
executor = MockExecutor()
executor.register_hook(LoggingHook("weave.log"))
summary = executor.execute_flow(graph, "my_weave")
```

---

## Extension Points

### 1. Executor Hooks

```python
class CustomHook(ExecutorHook):
    def before_agent(self, agent: Agent):
        # Called before execution
        pass

    def after_agent(self, agent: Agent, output: Any):
        # Called after execution
        pass

# Register
executor.register_hook(CustomHook())
```

### 2. Custom Validators (Future)

```python
class CustomValidator:
    def validate_agent(self, agent: Agent):
        # Custom validation logic
        pass

# Register
config.add_validator(CustomValidator())
```

### 3. Plugin System (Future v2.0)

```python
class ToolPlugin:
    name = "custom_tool"

    def execute(self, input_data):
        # Tool implementation
        return result

# Register
weave.register_plugin(ToolPlugin())
```

---

## Technology Stack

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| typer | ≥0.9.0 | CLI framework |
| rich | ≥13.7.0 | Terminal output |
| pydantic | ≥2.5.0 | Data validation |
| pyyaml | ≥6.0.1 | YAML parsing |
| networkx | ≥3.2.0 | Graph algorithms |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ≥7.4.0 | Testing |
| black | ≥23.12.0 | Code formatting |
| ruff | ≥0.1.9 | Linting |
| mypy | ≥1.8.0 | Type checking |

---

## File Structure

```
src/weave/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point (python -m weave)
│
├── cli/                     # CLI Layer
│   ├── __init__.py
│   ├── app.py               # Typer commands
│   └── output.py            # Rich formatting
│
├── parser/                  # Parser Layer
│   ├── __init__.py
│   ├── config.py            # YAML loader
│   └── env.py               # Env substitution
│
├── core/                    # Core Layer
│   ├── __init__.py
│   ├── models.py            # Pydantic models
│   ├── graph.py             # Dependency graph
│   ├── exceptions.py        # Custom exceptions
│   └── validator.py         # Validation (future)
│
└── runtime/                 # Runtime Layer
    ├── __init__.py
    ├── executor.py          # Execution engine
    └── hooks.py             # Extension hooks
```

---

## Performance Considerations

### v0.1.0 (Current)

- **Config Parsing:** < 100ms
- **Graph Building:** < 50ms
- **Mock Execution:** 0.5-2.5s per agent (simulated)
- **Memory:** Minimal (< 50MB for typical configs)

### v2.0 (Planned)

- **Real Execution:** Depends on LLM API latency
- **Parallel Execution:** Multiple agents concurrently
- **Caching:** Response caching for repeated calls

---

## Security

### Current Implementation

- ✅ Safe YAML loading (`yaml.safe_load`)
- ✅ Environment variable validation
- ✅ No code execution in configs
- ✅ Path traversal protection
- ✅ Input sanitization

### Future Enhancements (v2.0)

- 🔄 Secret management integration
- 🔄 API key encryption at rest
- 🔄 Audit logging
- 🔄 Rate limiting
- 🔄 Access control

---

## Testing Strategy

### Unit Tests

```python
def test_dependency_graph():
    config = WeaveConfig(...)
    graph = DependencyGraph(config)
    graph.build("test_weave")
    assert graph.get_execution_order() == ["A", "B", "C"]
```

### Integration Tests

```python
def test_end_to_end():
    # Run full workflow
    result = runner.invoke(app, ["apply"])
    assert result.exit_code == 0
```

### Test Coverage

- Parser: Config loading, env substitution
- Core: Model validation, graph building
- Runtime: Execution flow, hooks
- CLI: Command handling, output formatting

---

## Roadmap

### v0.1.0 ✅ (Current)

- Mock execution
- Dependency resolution
- CLI with 4 commands
- Beautiful terminal output

### v2.0 🔄 (Next)

- Real LLM execution
- Parallel agents
- State management
- Multiple providers

### v3.0 📋 (Future)

- Web UI
- Remote modules
- Plugin marketplace
- Analytics dashboard

---

## Next Steps

- [Extensibility](extensibility.md) - Hooks and plugins
- [Writing Configurations](../guides/writing-configs.md) - Best practices
- [Contributing](../../README.md#contributing) - How to contribute
