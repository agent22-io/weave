# Extensibility

How to extend Weave with custom functionality using hooks and plugins.

## Extension Points

Weave provides multiple extension points:

1. **Executor Hooks** - Intercept agent execution
2. **Custom Validators** - Add validation logic (planned)
3. **Plugin System** - Add tools and capabilities (planned v2.0)

---

## Executor Hooks

### Overview

Hooks allow you to run custom code before and after agent execution.

**Use Cases:**
- Logging
- Metrics collection
- State management
- Custom output processing
- Integration with external systems

### Hook Protocol

```python
from weave.runtime.hooks import ExecutorHook
from weave.core.models import Agent

class MyHook(ExecutorHook):
    def before_agent(self, agent: Agent) -> None:
        """Called before agent starts executing."""
        # Your code here
        pass

    def after_agent(self, agent: Agent, output: Any) -> None:
        """Called after agent completes execution."""
        # Your code here
        pass
```

### Built-in Hooks

#### LoggingHook

Logs agent execution to a file:

```python
from weave.runtime.hooks import LoggingHook

# Create hook
logger = LoggingHook("weave.log")

# Register with executor
executor.register_hook(logger)
```

**Output in `weave.log`:**
```
[START] researcher (gpt-4)
[DONE] researcher completed in 1.2s
[START] writer (claude-3-opus)
[DONE] writer completed in 2.3s
```

### Custom Hook Examples

#### Metrics Collection Hook

```python
import time
from typing import Dict, Any
from weave.runtime.hooks import ExecutorHook

class MetricsHook(ExecutorHook):
    def __init__(self):
        self.metrics: Dict[str, Any] = {}

    def before_agent(self, agent: Agent) -> None:
        self.metrics[agent.name] = {
            "start_time": time.time(),
            "model": agent.model,
        }

    def after_agent(self, agent: Agent, output: Any) -> None:
        metrics = self.metrics[agent.name]
        metrics["end_time"] = time.time()
        metrics["duration"] = metrics["end_time"] - metrics["start_time"]
        metrics["status"] = output.status
        metrics["tokens"] = output.tokens_used

    def report(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return self.metrics

# Usage
metrics = MetricsHook()
executor.register_hook(metrics)
executor.execute_flow(graph, "my_weave")

# Print report
import json
print(json.dumps(metrics.report(), indent=2))
```

#### Database Logging Hook

```python
import sqlite3
from datetime import datetime
from weave.runtime.hooks import ExecutorHook

class DatabaseHook(ExecutorHook):
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY,
                agent_name TEXT,
                model TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                duration REAL
            )
        """)

    def before_agent(self, agent: Agent) -> None:
        self.start_time = datetime.now()

    def after_agent(self, agent: Agent, output: Any) -> None:
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.conn.execute("""
            INSERT INTO agent_runs
            (agent_name, model, status, start_time, end_time, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            agent.name,
            agent.model,
            output.status,
            self.start_time.isoformat(),
            end_time.isoformat(),
            duration
        ))
        self.conn.commit()

# Usage
db_logger = DatabaseHook("weave_runs.db")
executor.register_hook(db_logger)
```

#### Webhook Notification Hook

```python
import requests
from weave.runtime.hooks import ExecutorHook

class WebhookHook(ExecutorHook):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def before_agent(self, agent: Agent) -> None:
        requests.post(self.webhook_url, json={
            "event": "agent_start",
            "agent": agent.name,
            "model": agent.model,
        })

    def after_agent(self, agent: Agent, output: Any) -> None:
        requests.post(self.webhook_url, json={
            "event": "agent_complete",
            "agent": agent.name,
            "status": output.status,
            "duration": output.execution_time,
        })

# Usage
webhook = WebhookHook("https://your-app.com/webhooks/weave")
executor.register_hook(webhook)
```

### Multiple Hooks

Register multiple hooks:

```python
executor = MockExecutor()

# Add multiple hooks
executor.register_hook(LoggingHook("weave.log"))
executor.register_hook(MetricsHook())
executor.register_hook(WebhookHook("https://..."))

# All hooks will be called
executor.execute_flow(graph, "my_weave")
```

Hooks are called in registration order.

---

## Custom Validators (Planned v2.0)

### Concept

Add custom validation logic to configs:

```python
from weave.core import Validator

class ModelValidator(Validator):
    """Ensure only approved models are used."""

    APPROVED_MODELS = ["gpt-4", "claude-3-opus"]

    def validate_agent(self, agent: Agent) -> None:
        if agent.model not in self.APPROVED_MODELS:
            raise ValidationError(
                f"Model '{agent.model}' not approved. "
                f"Use one of: {', '.join(self.APPROVED_MODELS)}"
            )

# Register
config.add_validator(ModelValidator())
```

---

## Plugin System (Planned v2.0)

### Overview

Plugins will provide:
- Custom tools for agents
- New agent types
- Output formatters
- Integration with external services

### Plugin Structure

```python
from weave.plugins import Plugin

class CustomToolPlugin(Plugin):
    """Add custom tool to Weave."""

    name = "custom_tool"
    version = "1.0.0"
    category = "data_processing"

    def execute(self, input_data: Any, config: Dict) -> Any:
        """Tool implementation."""
        # Your tool logic here
        return result

    def validate_config(self, config: Dict) -> None:
        """Validate tool configuration."""
        pass
```

### Plugin Categories

Planned categories:
- `data_processing` - ETL, cleaning, transformation
- `web` - Web scraping, API calls
- `analysis` - Statistical analysis, ML inference
- `output` - Formatters, exporters
- `integration` - External service connectors

### Using Plugins

```python
# Install plugin
weave plugin install custom-tool

# Use in config
agents:
  my_agent:
    model: "gpt-4"
    tools:
      - custom_tool    # From plugin
    config:
      custom_tool:
        option1: "value"
```

---

## Integration Examples

### Integrating with Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from weave.runtime import MockExecutor
from weave.parser import load_config_from_path
from weave.core.graph import DependencyGraph

def run_weave():
    config = load_config_from_path(".weave.yaml")
    graph = DependencyGraph(config)
    graph.build("my_weave")
    graph.validate()

    executor = MockExecutor()
    summary = executor.execute_flow(graph, "my_weave")

    if summary.failed > 0:
        raise Exception(f"{summary.failed} agents failed")

dag = DAG('weave_pipeline', ...)

task = PythonOperator(
    task_id='run_weave',
    python_callable=run_weave,
    dag=dag,
)
```

### Integrating with FastAPI

```python
from fastapi import FastAPI
from weave.runtime import MockExecutor
from weave.parser import load_config

app = FastAPI()

@app.post("/execute/{weave_name}")
async def execute_weave(weave_name: str):
    config = load_config_from_path("config.yaml")
    graph = DependencyGraph(config)
    graph.build(weave_name)
    graph.validate()

    executor = MockExecutor()
    summary = executor.execute_flow(graph, weave_name)

    return {
        "weave": weave_name,
        "agents": summary.total_agents,
        "successful": summary.successful,
        "failed": summary.failed,
        "time": summary.total_time,
    }
```

### Integrating with Celery

```python
from celery import Celery
from weave.runtime import MockExecutor

app = Celery('weave_tasks')

@app.task
def execute_weave_async(weave_name: str):
    config = load_config_from_path("config.yaml")
    graph = DependencyGraph(config)
    graph.build(weave_name)
    graph.validate()

    executor = MockExecutor()
    summary = executor.execute_flow(graph, weave_name)

    return {
        "weave": weave_name,
        "status": "success" if summary.failed == 0 else "failed",
    }

# Usage
result = execute_weave_async.delay("my_pipeline")
```

---

## Future Extension Points

### v2.0

- **Real Executors** - Implement for different LLM providers
- **State Managers** - Custom state persistence
- **Output Formatters** - Custom output formats
- **Tool Plugins** - Community-contributed tools

### v3.0

- **Agent Types** - Custom agent implementations
- **Execution Strategies** - Custom execution logic
- **UI Plugins** - Dashboard extensions
- **Provider Plugins** - New LLM providers

---

## Contributing Extensions

### Development Setup

```bash
# Clone repo
git clone https://github.com/weave/weave-cli.git
cd weave-cli

# Install dev dependencies
pip install -e ".[dev]"

# Create branch
git checkout -b feature/my-extension
```

### Creating a Hook

1. Create hook class implementing `ExecutorHook`
2. Add tests
3. Add documentation
4. Submit PR

### Creating a Plugin (Future)

1. Use plugin template
2. Implement plugin interface
3. Add tests and docs
4. Publish to plugin registry

---

## Best Practices

### Hook Development

1. **Keep hooks lightweight** - Don't slow down execution
2. **Handle errors gracefully** - Don't break execution flow
3. **Make hooks configurable** - Use constructor parameters
4. **Add logging** - Help with debugging
5. **Document thoroughly** - Clear usage examples

### Integration

1. **Isolate Weave logic** - Keep integration thin
2. **Handle failures** - Check summary.failed
3. **Set timeouts** - Prevent hanging
4. **Log appropriately** - Debug issues easily

---

## Next Steps

- [Architecture Overview](overview.md) - System architecture
- [Contributing](../../README.md#contributing) - How to contribute
- [Examples](../../examples/) - See working examples
