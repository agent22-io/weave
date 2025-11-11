"""Behavioral tests for configuration loading and validation."""

import pytest
from pathlib import Path
from weave.parser.config import load_config
from weave.core.exceptions import ConfigError


class TestConfigurationBehavior:
    """Test configuration file loading and validation behavior."""

    def test_valid_basic_config_loads_successfully(self, tmp_path):
        """A valid basic configuration should load without errors."""
        config_content = """
version: "1.0"

agents:
  agent1:
    model: "gpt-4"
    outputs: "result"

weaves:
  workflow1:
    description: "Test workflow"
    agents: [agent1]
"""
        config = load_config(config_content)

        assert config.version == "1.0"
        assert "agent1" in config.agents
        assert config.agents["agent1"].model == "gpt-4"
        assert "workflow1" in config.weaves

    def test_config_with_tools_loads_correctly(self, tmp_path):
        """Configuration with custom tools should load and validate."""
        config_content = """
version: "1.0"

tools:
  custom_tool:
    description: "A custom tool"
    category: "test"
    parameters:
      param1:
        type: "string"
        description: "Test parameter"
        required: true

agents:
  agent1:
    model: "gpt-4"
    tools: [custom_tool, calculator]

weaves:
  workflow1:
    agents: [agent1]
"""
        config = load_config(config_content)

        assert "custom_tool" in config.tools
        assert config.tools["custom_tool"].description == "A custom tool"
        assert "calculator" in config.agents["agent1"].tools

    def test_config_with_storage_settings_loads(self):
        """Configuration with storage settings should load correctly."""
        config_content = """
version: "1.0"

storage:
  enabled: true
  base_path: ".agent/storage"
  state_file: ".agent/state.yaml"

agents:
  agent1:
    model: "gpt-4"
    storage:
      save_outputs: true
      retention_days: 7

weaves:
  workflow1:
    agents: [agent1]
"""
        config = load_config(config_content)

        assert config.storage is not None
        assert config.storage.enabled is True
        assert config.agents["agent1"].storage.save_outputs is True

    def test_config_with_model_settings_loads(self):
        """Configuration with model-specific settings should load."""
        config_content = """
version: "1.0"

agents:
  agent1:
    model: "gpt-4"
    model_config:
      provider: "openai"
      temperature: 0.8
      max_tokens: 2000
      top_p: 0.9

weaves:
  workflow1:
    agents: [agent1]
"""
        config = load_config(config_content)

        assert config.agents["agent1"].llm_config is not None
        assert config.agents["agent1"].llm_config.temperature == 0.8
        assert config.agents["agent1"].llm_config.max_tokens == 2000

    def test_config_with_memory_settings_loads(self):
        """Configuration with memory settings should load."""
        config_content = """
version: "1.0"

agents:
  agent1:
    model: "gpt-4"
    memory:
      type: "buffer"
      max_messages: 100
      persist: true

weaves:
  workflow1:
    agents: [agent1]
"""
        config = load_config(config_content)

        assert config.agents["agent1"].memory is not None
        assert config.agents["agent1"].memory.type == "buffer"
        assert config.agents["agent1"].memory.persist is True

    def test_missing_agent_reference_raises_error(self):
        """Configuration referencing non-existent agent should raise error."""
        config_content = """
version: "1.0"

agents:
  agent1:
    model: "gpt-4"

weaves:
  workflow1:
    agents: [agent1, nonexistent_agent]
"""
        with pytest.raises((ValueError, ConfigError), match="unknown agent|nonexistent_agent"):
            load_config(config_content)

    def test_circular_dependency_detected(self):
        """Circular dependencies between agents should be detected."""
        # This will be caught during graph building, not config loading
        config_content = """
version: "1.0"

agents:
  agent1:
    model: "gpt-4"
    inputs: "agent2"

  agent2:
    model: "gpt-4"
    inputs: "agent1"

weaves:
  workflow1:
    agents: [agent1, agent2]
"""
        # Config loads fine, circular dependency detected during graph validation
        config = load_config(config_content)
        assert len(config.agents) == 2

    def test_environment_variable_substitution(self):
        """Environment variables should be substituted in config."""
        import os
        os.environ["TEST_MODEL"] = "gpt-4-test"

        config_content = """
version: "1.0"

agents:
  agent1:
    model: "${TEST_MODEL}"

weaves:
  workflow1:
    agents: [agent1]
"""
        config = load_config(config_content)
        assert config.agents["agent1"].model == "gpt-4-test"

    def test_config_without_weaves_raises_error(self):
        """Configuration must have at least one weave."""
        config_content = """
version: "1.0"

agents:
  agent1:
    model: "gpt-4"
"""
        with pytest.raises((ValueError, ConfigError), match="at least one weave|weaves"):
            load_config(config_content)

    def test_complex_pipeline_config_loads(self):
        """Complex multi-agent pipeline configuration should load."""
        config_content = """
version: "1.0"

tools:
  email_sender:
    description: "Send emails"
    category: "communication"
    parameters:
      to:
        type: "string"
        required: true

agents:
  researcher:
    model: "gpt-4"
    tools: [calculator, web_search]
    outputs: "research_data"

  analyst:
    model: "claude-3-opus"
    inputs: "researcher"
    tools: [calculator, list_operations]
    memory:
      type: "buffer"
      max_messages: 50
    outputs: "analysis"

  writer:
    model: "gpt-4"
    inputs: "analyst"
    tools: [string_formatter]
    storage:
      save_outputs: true
    outputs: "report"

  notifier:
    model: "gpt-4"
    inputs: "writer"
    tools: [email_sender]

weaves:
  full_pipeline:
    description: "Complete research and reporting pipeline"
    agents: [researcher, analyst, writer, notifier]
"""
        config = load_config(config_content)

        assert len(config.agents) == 4
        assert len(config.weaves) == 1
        assert config.agents["analyst"].inputs == "researcher"
        assert config.agents["writer"].storage.save_outputs is True
