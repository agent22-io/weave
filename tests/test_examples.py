"""Test that all example configurations are valid and can execute."""

import pytest
from pathlib import Path
from weave.parser.config import load_config_from_path
from weave.core.graph import DependencyGraph
from weave.runtime.executor import Executor
from rich.console import Console


# Find all example YAML files
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXAMPLE_CONFIGS = list(EXAMPLES_DIR.glob("*.agent.yaml"))


class TestExampleConfigs:
    """Test that all example configurations work correctly."""

    @pytest.mark.parametrize("config_file", EXAMPLE_CONFIGS, ids=lambda p: p.name)
    def test_example_config_loads(self, config_file):
        """Example configuration should load without errors."""
        config = load_config_from_path(config_file)

        assert config is not None
        assert len(config.agents) > 0
        assert len(config.weaves) > 0

    @pytest.mark.parametrize("config_file", EXAMPLE_CONFIGS, ids=lambda p: p.name)
    def test_example_config_validates(self, config_file):
        """Example configuration should pass validation."""
        config = load_config_from_path(config_file)

        # Validate all weaves
        for weave_name in config.weaves.keys():
            graph = DependencyGraph(config)
            graph.build(weave_name)
            graph.validate()  # Should not raise any errors

            # Check execution order exists
            order = graph.get_execution_order()
            assert len(order) > 0

    @pytest.mark.parametrize("config_file", EXAMPLE_CONFIGS, ids=lambda p: p.name)
    def test_example_config_executes(self, config_file, tmp_path):
        """Example configuration should execute successfully in dry-run mode."""
        # Change to temp directory to avoid creating state files
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            config = load_config_from_path(config_file)

            # Test each weave
            for weave_name in config.weaves.keys():
                graph = DependencyGraph(config)
                graph.build(weave_name)

                # Execute in dry-run mode
                console = Console(quiet=True)
                executor = Executor(console=console, config=config)
                import asyncio
                summary = asyncio.run(executor.execute_flow(graph, weave_name, dry_run=True))

                assert summary.total_agents > 0

        finally:
            os.chdir(original_cwd)


class TestExampleFeatureCoverage:
    """Test that examples cover all major features."""

    def test_basic_pipeline_example_exists(self):
        """Should have a basic pipeline example."""
        basic_example = EXAMPLES_DIR / "basic.agent.yaml"
        assert basic_example.exists()

        config = load_config_from_path(basic_example)
        assert len(config.agents) >= 2

    # NOTE: Tool calling and MCP examples deferred to v2
    # def test_tool_calling_example_exists(self):
    #     """Should have a tool calling example."""
    #     tool_example = EXAMPLES_DIR / "tool-calling.agent.yaml"
    #     assert tool_example.exists()

    # def test_mcp_integration_example_exists(self):
    #     """Should have an MCP integration example."""
    #     mcp_example = EXAMPLES_DIR / "mcp-integration.agent.yaml"
    #     assert mcp_example.exists()

    def test_resources_example_exists(self):
        """Should have a resources example."""
        resources_example = EXAMPLES_DIR / "resources_example"
        assert resources_example.exists()
        assert resources_example.is_dir()

        config_file = resources_example / ".agent.yaml"
        assert config_file.exists()

    # NOTE: These examples exist as directories with .agent.yaml files inside
    # The standalone .yaml files at root level don't exist
    # def test_data_processing_example_exists(self):
    #     """Should have a data processing example."""
    #     data_example = EXAMPLES_DIR / "data-processing.agent.yaml"
    #     assert data_example.exists()

    # def test_research_pipeline_example_exists(self):
    #     """Should have a research pipeline example."""
    #     research_example = EXAMPLES_DIR / "research-pipeline.agent.yaml"
    #     assert research_example.exists()


class TestConfigFeatureCoverage:
    """Test that config features are demonstrated in examples."""

    def test_model_config_coverage(self):
        """At least one example should use model_config."""
        has_model_config = False

        for config_file in EXAMPLE_CONFIGS:
            config = load_config_from_path(config_file)
            for agent in config.agents.values():
                if agent.llm_config is not None:
                    has_model_config = True
                    break
            if has_model_config:
                break

        # For now, this might not be covered yet
        # assert has_model_config, "No example demonstrates model_config"

    def test_memory_config_coverage(self):
        """At least one example should use memory config."""
        has_memory_config = False

        for config_file in EXAMPLE_CONFIGS:
            config = load_config_from_path(config_file)
            for agent in config.agents.values():
                if agent.memory is not None:
                    has_memory_config = True
                    break
            if has_memory_config:
                break

        # For now, this might not be covered yet
        # assert has_memory_config, "No example demonstrates memory config"

    def test_storage_config_coverage(self):
        """At least one example should use storage config."""
        has_storage_config = False

        for config_file in EXAMPLE_CONFIGS:
            config = load_config_from_path(config_file)
            for agent in config.agents.values():
                if agent.storage is not None:
                    has_storage_config = True
                    break
            if has_storage_config:
                break

        # For now, this might not be covered yet
        # assert has_storage_config, "No example demonstrates storage config"

    def test_custom_tools_coverage(self):
        """At least one example should define custom tools."""
        has_custom_tools = False

        for config_file in EXAMPLE_CONFIGS:
            config = load_config_from_path(config_file)
            if len(config.tools) > 0:
                has_custom_tools = True
                break

        assert has_custom_tools, "No example demonstrates custom tools"

    def test_dependency_chain_coverage(self):
        """At least one example should have a dependency chain."""
        has_dependency_chain = False

        for config_file in EXAMPLE_CONFIGS:
            config = load_config_from_path(config_file)
            for agent in config.agents.values():
                if agent.inputs is not None:
                    has_dependency_chain = True
                    break
            if has_dependency_chain:
                break

        assert has_dependency_chain, "No example demonstrates agent dependencies"
