"""Resource reference processing for configuration."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..resources.loader import ResourceLoader
from ..resources.models import ResourceType


class ResourceProcessor:
    """
    Processes resource references in configuration files.

    Handles @resource_type/resource_name syntax and loads actual resources.
    """

    RESOURCE_PATTERN = re.compile(r"^@(\w+)/(.+)$")

    # Mapping from config field names to ResourceType
    RESOURCE_TYPE_MAP = {
        "prompts": ResourceType.SYSTEM_PROMPT,
        "skills": ResourceType.SKILL,
        "recipes": ResourceType.RECIPE,
        "knowledge": ResourceType.KNOWLEDGE_BASE,
        "rules": ResourceType.RULE,
        "behaviors": ResourceType.BEHAVIOR,
        "sub_agents": ResourceType.SUB_AGENT,
        "memory": ResourceType.MEMORY,
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize resource processor.

        Args:
            config_path: Path to config file (used to find .weave directory)
        """
        # Determine base path for resources
        if config_path:
            # Look for .weave directory relative to config file
            config_dir = config_path.parent if config_path.is_file() else config_path
            base_path = config_dir / ".weave"
        else:
            base_path = Path(".weave")

        self.loader = ResourceLoader(base_path)
        self.loader.load_all()

    def process_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all resource references in configuration data.

        Args:
            config_data: Raw config dictionary

        Returns:
            Config dictionary with resource references processed
        """
        # Process agents
        if "agents" in config_data:
            for agent_name, agent_config in config_data["agents"].items():
                config_data["agents"][agent_name] = self.process_agent(agent_config)

        return config_data

    def process_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process resource references in an agent configuration.

        Args:
            agent_config: Agent configuration dictionary

        Returns:
            Agent config with resource references processed
        """
        # Process prompt field (single reference)
        if "prompt" in agent_config:
            prompt_value = agent_config["prompt"]
            if isinstance(prompt_value, str) and prompt_value.startswith("@"):
                resource = self._load_resource_reference(prompt_value)
                if resource:
                    # Replace reference with actual content
                    agent_config["prompt"] = resource.content

        # Process list fields (skills, knowledge, rules, behaviors)
        list_fields = ["skills", "knowledge", "rules", "behaviors"]
        for field in list_fields:
            if field in agent_config and isinstance(agent_config[field], list):
                agent_config[field] = self._process_resource_list(
                    agent_config[field], field
                )

        return agent_config

    def _process_resource_list(
        self, references: List[str], field_name: str
    ) -> List[str]:
        """
        Process a list of resource references.

        Args:
            references: List of resource references (e.g., ["@skills/seo"])
            field_name: Name of the field (used for validation)

        Returns:
            List of resource names (without @ prefix)
        """
        processed = []

        for ref in references:
            if isinstance(ref, str) and ref.startswith("@"):
                # Extract resource name from reference
                match = self.RESOURCE_PATTERN.match(ref)
                if match:
                    resource_type_name = match.group(1)
                    resource_name = match.group(2)

                    # Verify resource exists
                    resource_type = self.RESOURCE_TYPE_MAP.get(resource_type_name)
                    if resource_type:
                        resource = self.loader.get_resource(resource_type, resource_name)
                        if resource:
                            # Store the resource name (will be looked up at runtime)
                            processed.append(resource_name)
                        else:
                            print(
                                f"Warning: Resource not found: {ref} "
                                f"(looked in .agent/{resource_type_name}/)"
                            )
                            processed.append(ref)  # Keep original reference
                    else:
                        print(f"Warning: Unknown resource type: {resource_type_name}")
                        processed.append(ref)  # Keep original reference
                else:
                    processed.append(ref)  # Not a valid resource reference
            else:
                processed.append(ref)  # Not a resource reference

        return processed

    def _load_resource_reference(self, reference: str):
        """
        Load a resource from a reference string.

        Args:
            reference: Resource reference (e.g., "@prompts/content_writer")

        Returns:
            Resource object or None if not found
        """
        match = self.RESOURCE_PATTERN.match(reference)
        if not match:
            return None

        resource_type_name = match.group(1)
        resource_name = match.group(2)

        resource_type = self.RESOURCE_TYPE_MAP.get(resource_type_name)
        if not resource_type:
            print(f"Warning: Unknown resource type: {resource_type_name}")
            return None

        resource = self.loader.get_resource(resource_type, resource_name)
        if not resource:
            print(
                f"Warning: Resource not found: {reference} "
                f"(looked in .agent/{resource_type_name}/)"
            )

        return resource

    def get_loader(self) -> ResourceLoader:
        """Get the underlying ResourceLoader instance."""
        return self.loader
