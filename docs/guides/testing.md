# Testing Guide

This guide covers testing strategies and best practices for Weave configurations and workflows.

## Overview

Weave provides comprehensive testing capabilities to ensure your agent workflows are reliable and maintainable:

- **Example Testing**: Automated validation of all example configurations
- **Config Behavior Testing**: Tests for configuration loading and validation
- **CI/CD Integration**: GitHub Actions workflows for continuous testing
- **Dry-Run Mode**: Test workflows without making actual API calls

## Test Structure

```
tests/
├── __init__.py
├── test_examples.py           # Tests for all example configs
└── test_config_behavior.py    # Config loading and validation tests
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_examples.py -v
pytest tests/test_config_behavior.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src/weave --cov-report=html
```

### Run Tests in Watch Mode

```bash
pytest-watch tests/
```

## Test Categories

### 1. Example Configuration Tests

Tests that verify all example YAML files are valid and executable.

**File**: `tests/test_examples.py`

#### Test Classes:

**TestExampleConfigs**
- `test_example_config_loads`: Verifies configs load without errors
- `test_example_config_validates`: Validates dependency graphs
- `test_example_config_executes`: Tests dry-run execution

**TestExampleFeatureCoverage**
- Ensures examples exist for all major features
- Verifies feature-specific examples (tool calling, MCP, etc.)

**TestConfigFeatureCoverage**
- Tests that config features are demonstrated in examples
- Checks for model config, memory, storage, tools, dependencies

```python
# Example test
@pytest.mark.parametrize("config_file", EXAMPLE_CONFIGS, ids=lambda p: p.name)
def test_example_config_loads(self, config_file):
    """Example configuration should load without errors."""
    config = load_config_from_path(config_file)
    assert config is not None
    assert len(config.agents) > 0
    assert len(config.weaves) > 0
```

### 2. Configuration Behavior Tests

Tests for configuration loading, validation, and error handling.

**File**: `tests/test_config_behavior.py`

#### Test Coverage:

- Basic configuration loading
- Tool definitions and validation
- Storage settings
- Model configuration
- Memory configuration
- Environment variable substitution
- Error handling (missing agents, circular dependencies)
- Complex multi-agent pipelines

```python
def test_config_with_tools_loads_correctly(self):
    """Configuration with custom tools should load and validate."""
    config_content = """
version: "1.0"

tools:
  custom_tool:
    description: "A custom tool"
    parameters:
      param1:
        type: "string"
        required: true

agents:
  agent1:
    model: "gpt-4"
    tools: [custom_tool]

weaves:
  workflow1:
    agents: [agent1]
"""
    config = load_config(config_content)
    assert "custom_tool" in config.tools
```

## Dry-Run Testing

Test your workflows without making actual API calls or executing tools:

```bash
# Dry run a specific config
weave run examples/basic.weave.yaml --dry-run

# Dry run with verbose output
weave run examples/research-pipeline.weave.yaml --dry-run --verbose
```

### Dry-Run Benefits:

- ✅ Validates configuration syntax
- ✅ Checks dependency graph
- ✅ Verifies agent execution order
- ✅ Tests tool loading
- ✅ No API costs
- ✅ Fast feedback

## Configuration Validation

Validate configurations without executing:

```bash
# Validate a single config
weave validate examples/tool-calling.weave.yaml

# Validate all examples
for config in examples/*.weave.yaml; do
    weave validate "$config"
done
```

## Writing Tests for Your Configs

### 1. Test Config Loading

```python
def test_my_config_loads():
    """My configuration should load without errors."""
    config = load_config_from_path("path/to/my.weave.yaml")
    assert config is not None
    assert "my_agent" in config.agents
```

### 2. Test Dependency Graph

```python
def test_my_config_dependencies():
    """Dependencies should be valid."""
    config = load_config_from_path("path/to/my.weave.yaml")
    graph = DependencyGraph(config)
    graph.build("my_weave")
    graph.validate()  # Should not raise

    order = graph.get_execution_order()
    assert len(order) > 0
```

### 3. Test Dry-Run Execution

```python
def test_my_config_executes(tmp_path):
    """Config should execute in dry-run mode."""
    os.chdir(tmp_path)

    config = load_config_from_path("path/to/my.weave.yaml")
    graph = DependencyGraph(config)
    graph.build("my_weave")

    console = Console(quiet=True)
    executor = MockExecutor(console=console, config=config)
    summary = executor.execute_flow(graph, "my_weave", dry_run=True)

    assert summary.total_agents > 0
    assert summary.completed_agents == summary.total_agents
```

## CI/CD Integration

### GitHub Actions Workflow

Weave includes a GitHub Actions workflow for automated testing:

**File**: `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop, 'claude/**' ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        pytest tests/ -v
```

### Running CI Checks Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/ tests/

# Run tests
pytest tests/ -v

# Check CLI installation
weave --version
weave --help
```

## Test Best Practices

### 1. Use Parametrized Tests

```python
@pytest.mark.parametrize("config_file", EXAMPLE_CONFIGS, ids=lambda p: p.name)
def test_config(self, config_file):
    # Test runs for each config file
    pass
```

### 2. Use Fixtures for Setup

```python
@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "test.weave.yaml"
    config_file.write_text(CONFIG_CONTENT)
    return config_file
```

### 3. Test High-Level Behavior

Focus on behavior, not implementation:

```python
# Good: Tests behavior
def test_agent_pipeline_completes():
    summary = run_pipeline()
    assert summary.status == "completed"

# Avoid: Tests implementation details
def test_internal_queue_size():
    assert executor._queue.size() == 3  # Too specific
```

### 4. Use Dry-Run for Integration Tests

```python
def test_full_workflow():
    # Use dry-run to test without API calls
    summary = executor.execute_flow(graph, "workflow", dry_run=True)
    assert summary.total_agents == 5
```

### 5. Test Error Conditions

```python
def test_invalid_agent_reference():
    with pytest.raises(ValueError, match="unknown agent"):
        load_config(invalid_config)
```

## Testing Tools and MCP

### Test Tool Loading

```python
def test_tools_loaded_from_config():
    config = load_config_from_path("tool-config.yaml")
    executor = MockExecutor(console=console, config=config)

    # Verify tools are registered
    assert executor.tool_executor is not None
    assert len(executor.tool_executor.tools) > 0
```

### Test MCP Integration

```python
def test_mcp_tools_available():
    config = load_config_from_path("mcp-config.yaml")
    # Verify MCP tools are configured
    assert any(agent.tools for agent in config.agents.values())
```

## Testing State Management

### Test State Persistence

```python
def test_execution_state_saved():
    state_manager = StateManager()
    run_id = state_manager.create_run_id()

    state = ExecutionState(
        weave_name="test",
        run_id=run_id,
        status="completed",
        start_time=time.time()
    )

    state_manager.save_state(state)
    loaded = state_manager.load_state(run_id)

    assert loaded is not None
    assert loaded.weave_name == "test"
```

### Test Lock Files

```python
def test_lock_prevents_concurrent_execution():
    manager = StateManager()

    # Create lock
    manager.create_lock("test_weave", "run_1")

    # Second lock should fail
    with pytest.raises(RuntimeError, match="already locked"):
        manager.create_lock("test_weave", "run_2")
```

## Testing Storage

### Test Storage Backend

```python
def test_storage_saves_and_loads(tmp_path):
    storage = StorageBackend(base_path=str(tmp_path))

    data = {"result": "test"}
    storage.save("test_key", data)

    loaded = storage.load("test_key")
    assert loaded == data
```

## Debugging Failed Tests

### 1. Run with Verbose Output

```bash
pytest tests/ -v -s
```

### 2. Run Single Test

```bash
pytest tests/test_examples.py::TestExampleConfigs::test_example_config_loads -v
```

### 3. Use Debugger

```python
import pytest

def test_something():
    pytest.set_trace()  # Breakpoint
    # ... test code
```

### 4. Check Test Logs

```bash
pytest tests/ -v --tb=long
```

## Coverage Reports

Generate coverage reports to identify untested code:

```bash
# Run with coverage
pytest tests/ --cov=src/weave --cov-report=html

# View report
open htmlcov/index.html
```

## Continuous Testing

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Example: Complete Test File

```python
"""Test custom workflow configurations."""

import pytest
from pathlib import Path
from weave.parser.config import load_config_from_path
from weave.core.graph import DependencyGraph
from weave.runtime.executor import MockExecutor
from rich.console import Console


class TestCustomWorkflow:
    """Test custom workflow configuration."""

    def test_config_loads(self):
        """Configuration should load successfully."""
        config = load_config_from_path("my-workflow.weave.yaml")
        assert config is not None
        assert len(config.agents) >= 2

    def test_dependencies_valid(self):
        """Dependency graph should be valid."""
        config = load_config_from_path("my-workflow.weave.yaml")
        graph = DependencyGraph(config)
        graph.build("my_workflow")
        graph.validate()

        order = graph.get_execution_order()
        assert len(order) == 3  # Expected agent count

    def test_executes_successfully(self, tmp_path):
        """Workflow should execute in dry-run mode."""
        import os
        os.chdir(tmp_path)

        config = load_config_from_path("my-workflow.weave.yaml")
        graph = DependencyGraph(config)
        graph.build("my_workflow")

        console = Console(quiet=True)
        executor = MockExecutor(console=console, config=config)
        summary = executor.execute_flow(graph, "my_workflow", dry_run=True)

        assert summary.total_agents == 3
        assert summary.completed_agents == 3
        assert summary.failed_agents == 0
```

## Summary

- ✅ Use `pytest` for all tests
- ✅ Test high-level behavior, not implementation details
- ✅ Use dry-run mode for integration testing
- ✅ Validate all configurations before execution
- ✅ Set up CI/CD for automated testing
- ✅ Test error conditions and edge cases
- ✅ Use parametrized tests for multiple configs
- ✅ Generate coverage reports regularly

## Next Steps

1. Write tests for your custom configurations
2. Set up GitHub Actions for your repository
3. Add pre-commit hooks for local validation
4. Review coverage reports and add missing tests
5. Document test requirements for contributors

For more information, see:
- [Configuration Guide](configuration.md)
- [Development Guide](../DEVELOPMENT.md)
- [Contributing Guide](../CONTRIBUTING.md)
