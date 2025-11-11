"""Test resource loading and integration with config system."""

import pytest
from pathlib import Path
from weave.parser.config import load_config_from_path
from weave.resources.loader import ResourceLoader
from weave.resources.models import ResourceType


class TestResourceExamples:
    """Test that resources example works correctly."""

    def test_resources_example_exists(self):
        """Should have a resources example directory."""
        resources_example = Path(__file__).parent.parent / "examples" / "resources_example"
        assert resources_example.exists()
        assert resources_example.is_dir()

        config_file = resources_example / ".agent.yaml"
        assert config_file.exists()

    def test_resources_example_loads(self):
        """Resources example configuration should load successfully."""
        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        config = load_config_from_path(config_file)

        assert config is not None
        assert len(config.agents) == 3
        assert len(config.weaves) == 1

    def test_resources_example_agents(self):
        """Resources example agents should have proper resource references."""
        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        config = load_config_from_path(config_file)

        # Check writer agent
        writer = config.agents["writer"]
        assert writer.prompt is not None
        assert "content writer" in writer.prompt.lower()  # Should be loaded from resource
        assert len(writer.knowledge) > 0  # Should have knowledge references
        assert writer.knowledge[0] == "brand_voice"  # Resource name without @ prefix

        # Check seo_specialist agent
        seo = config.agents["seo_specialist"]
        assert len(seo.skills) > 0  # Should have skill references
        assert seo.skills[0] == "seo_optimization"  # Resource name without @ prefix


class TestResourceLoader:
    """Test ResourceLoader functionality."""

    def test_resource_loader_loads_prompts(self):
        """ResourceLoader should load system prompts."""
        base_path = Path(__file__).parent.parent / "examples" / "resources_example" / ".weave"
        loader = ResourceLoader(base_path)
        loader.load_all()

        # Check that content_writer prompt was loaded
        prompt = loader.get_resource(ResourceType.SYSTEM_PROMPT, "content_writer")
        assert prompt is not None
        assert prompt.name == "content_writer"
        assert "content writer" in prompt.content.lower()

    def test_resource_loader_loads_skills(self):
        """ResourceLoader should load skills."""
        base_path = Path(__file__).parent.parent / "examples" / "resources_example" / ".weave"
        loader = ResourceLoader(base_path)
        loader.load_all()

        # Check that seo_optimization skill was loaded
        skill = loader.get_resource(ResourceType.SKILL, "seo_optimization")
        assert skill is not None
        assert skill.name == "seo_optimization"
        assert "search" in skill.description.lower() or "seo" in skill.tags
        assert skill.required_tools is not None
        assert "web_search" in skill.required_tools

    def test_resource_loader_loads_knowledge(self):
        """ResourceLoader should load knowledge bases."""
        base_path = Path(__file__).parent.parent / "examples" / "resources_example" / ".weave"
        loader = ResourceLoader(base_path)
        loader.load_all()

        # Check that brand_voice knowledge was loaded
        kb = loader.get_resource(ResourceType.KNOWLEDGE_BASE, "brand_voice")
        assert kb is not None
        assert kb.name == "brand_voice"
        assert "brand" in kb.content.lower()

    def test_resource_loader_list_resources(self):
        """ResourceLoader should list all available resources."""
        base_path = Path(__file__).parent.parent / "examples" / "resources_example" / ".weave"
        loader = ResourceLoader(base_path)
        loader.load_all()

        resources = loader.list_resources()
        assert isinstance(resources, dict)

        # Should have at least prompts, skills, and knowledge
        assert ResourceType.SYSTEM_PROMPT.value in resources
        assert ResourceType.SKILL.value in resources
        assert ResourceType.KNOWLEDGE_BASE.value in resources

        # Check counts
        assert len(resources[ResourceType.SYSTEM_PROMPT.value]) >= 1
        assert len(resources[ResourceType.SKILL.value]) >= 1
        assert len(resources[ResourceType.KNOWLEDGE_BASE.value]) >= 1


class TestResourceProcessor:
    """Test ResourceProcessor functionality."""

    def test_resource_processor_processes_prompt_reference(self):
        """ResourceProcessor should process @prompts/ references."""
        from weave.parser.resources import ResourceProcessor

        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        processor = ResourceProcessor(config_file)

        agent_config = {
            "model": "gpt-4",
            "prompt": "@prompts/content_writer",
        }

        processed = processor.process_agent(agent_config)

        # Prompt should be replaced with actual content
        assert processed["prompt"] != "@prompts/content_writer"
        assert "content writer" in processed["prompt"].lower()

    def test_resource_processor_processes_skill_references(self):
        """ResourceProcessor should process @skills/ references."""
        from weave.parser.resources import ResourceProcessor

        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        processor = ResourceProcessor(config_file)

        agent_config = {
            "model": "gpt-4",
            "skills": ["@skills/seo_optimization"],
        }

        processed = processor.process_agent(agent_config)

        # Skills should be processed to resource names
        assert len(processed["skills"]) > 0
        assert processed["skills"][0] == "seo_optimization"

    def test_resource_processor_processes_knowledge_references(self):
        """ResourceProcessor should process @knowledge/ references."""
        from weave.parser.resources import ResourceProcessor

        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        processor = ResourceProcessor(config_file)

        agent_config = {
            "model": "gpt-4",
            "knowledge": ["@knowledge/brand_voice"],
        }

        processed = processor.process_agent(agent_config)

        # Knowledge should be processed to resource names
        assert len(processed["knowledge"]) > 0
        assert processed["knowledge"][0] == "brand_voice"

    def test_resource_processor_handles_missing_resources(self):
        """ResourceProcessor should handle missing resources gracefully."""
        from weave.parser.resources import ResourceProcessor

        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        processor = ResourceProcessor(config_file)

        agent_config = {
            "model": "gpt-4",
            "skills": ["@skills/nonexistent_skill"],
        }

        # Should not raise an error, but keep the reference
        processed = processor.process_agent(agent_config)
        assert len(processed["skills"]) > 0


class TestResourceIntegration:
    """Test end-to-end resource integration."""

    def test_config_with_resources_validates(self):
        """Configuration with resources should validate successfully."""
        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        config = load_config_from_path(config_file)

        # Validate all weaves
        from weave.core.graph import DependencyGraph

        for weave_name in config.weaves.keys():
            graph = DependencyGraph(config)
            graph.build(weave_name)
            graph.validate()  # Should not raise any errors

            # Check execution order exists
            order = graph.get_execution_order()
            assert len(order) > 0

    def test_agent_with_resources_has_correct_fields(self):
        """Agent loaded with resources should have correct field values."""
        config_file = Path(__file__).parent.parent / "examples" / "resources_example" / ".agent.yaml"
        config = load_config_from_path(config_file)

        writer = config.agents["writer"]

        # Check that resources are properly loaded
        assert writer.prompt is not None  # Should be loaded from @prompts/content_writer
        assert isinstance(writer.knowledge, list)  # Should be a list of resource names
        assert len(writer.knowledge) > 0  # Should have at least one knowledge base

        seo = config.agents["seo_specialist"]

        assert isinstance(seo.skills, list)  # Should be a list of resource names
        assert len(seo.skills) > 0  # Should have at least one skill
