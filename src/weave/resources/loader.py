"""Resource loader for reading files and folders."""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import (
    SystemPrompt,
    Skill,
    Recipe,
    KnowledgeBase,
    Rule,
    AgentBehavior,
    SubAgentPrompt,
    MemoryResource,
    ResourceType,
)


class ResourceLoader:
    """
    Loads resources from files and folders.

    Supports multiple formats: YAML, JSON, Markdown, and plain text.
    Organizes resources by type in a standard directory structure.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize resource loader.

        Args:
            base_path: Base directory for resources (default: .weave/)
        """
        self.base_path = base_path or Path(".weave")
        self._resources: Dict[ResourceType, Dict[str, Any]] = {
            rt: {} for rt in ResourceType
        }

    def load_all(self) -> None:
        """Load all resources from the base path."""
        if not self.base_path.exists():
            return

        # Load each resource type
        self.load_system_prompts()
        self.load_skills()
        self.load_recipes()
        self.load_knowledge_bases()
        self.load_rules()
        self.load_behaviors()
        self.load_sub_agents()
        self.load_memories()

    def load_system_prompts(self, path: Optional[Path] = None) -> Dict[str, SystemPrompt]:
        """
        Load system prompts from files.

        Args:
            path: Directory containing prompt files (default: .weave/prompts/)

        Returns:
            Dictionary of prompt name to SystemPrompt
        """
        prompts_path = path or self.base_path / "prompts"
        if not prompts_path.exists():
            return {}

        prompts = {}
        for file_path in prompts_path.glob("*.md"):
            prompt = self._load_prompt_file(file_path)
            if prompt:
                prompts[prompt.name] = prompt
                self._resources[ResourceType.SYSTEM_PROMPT][prompt.name] = prompt

        # Also load YAML/JSON prompt configs
        for file_path in prompts_path.glob("*.yaml"):
            prompt = self._load_prompt_yaml(file_path)
            if prompt:
                prompts[prompt.name] = prompt
                self._resources[ResourceType.SYSTEM_PROMPT][prompt.name] = prompt

        return prompts

    def load_skills(self, path: Optional[Path] = None) -> Dict[str, Skill]:
        """
        Load skills from files.

        Args:
            path: Directory containing skill files (default: .weave/skills/)

        Returns:
            Dictionary of skill name to Skill
        """
        skills_path = path or self.base_path / "skills"
        if not skills_path.exists():
            return {}

        skills = {}
        for file_path in skills_path.glob("*.yaml"):
            skill = self._load_yaml_resource(file_path, Skill)
            if skill:
                skills[skill.name] = skill
                self._resources[ResourceType.SKILL][skill.name] = skill

        return skills

    def load_recipes(self, path: Optional[Path] = None) -> Dict[str, Recipe]:
        """
        Load workflow recipes from files.

        Args:
            path: Directory containing recipe files (default: .weave/recipes/)

        Returns:
            Dictionary of recipe name to Recipe
        """
        recipes_path = path or self.base_path / "recipes"
        if not recipes_path.exists():
            return {}

        recipes = {}
        for file_path in recipes_path.glob("*.yaml"):
            recipe = self._load_yaml_resource(file_path, Recipe)
            if recipe:
                recipes[recipe.name] = recipe
                self._resources[ResourceType.RECIPE][recipe.name] = recipe

        return recipes

    def load_knowledge_bases(self, path: Optional[Path] = None) -> Dict[str, KnowledgeBase]:
        """
        Load knowledge base files.

        Args:
            path: Directory containing knowledge files (default: .weave/knowledge/)

        Returns:
            Dictionary of KB name to KnowledgeBase
        """
        kb_path = path or self.base_path / "knowledge"
        if not kb_path.exists():
            return {}

        knowledge_bases = {}

        # Load markdown files
        for file_path in kb_path.glob("*.md"):
            kb = self._load_knowledge_file(file_path, "markdown")
            if kb:
                knowledge_bases[kb.name] = kb
                self._resources[ResourceType.KNOWLEDGE_BASE][kb.name] = kb

        # Load text files
        for file_path in kb_path.glob("*.txt"):
            kb = self._load_knowledge_file(file_path, "text")
            if kb:
                knowledge_bases[kb.name] = kb
                self._resources[ResourceType.KNOWLEDGE_BASE][kb.name] = kb

        # Load JSON files
        for file_path in kb_path.glob("*.json"):
            kb = self._load_knowledge_file(file_path, "json")
            if kb:
                knowledge_bases[kb.name] = kb
                self._resources[ResourceType.KNOWLEDGE_BASE][kb.name] = kb

        return knowledge_bases

    def load_rules(self, path: Optional[Path] = None) -> Dict[str, Rule]:
        """
        Load rules from files.

        Args:
            path: Directory containing rule files (default: .weave/rules/)

        Returns:
            Dictionary of rule name to Rule
        """
        rules_path = path or self.base_path / "rules"
        if not rules_path.exists():
            return {}

        rules = {}
        for file_path in rules_path.glob("*.yaml"):
            rule = self._load_yaml_resource(file_path, Rule)
            if rule:
                rules[rule.name] = rule
                self._resources[ResourceType.RULE][rule.name] = rule

        return rules

    def load_behaviors(self, path: Optional[Path] = None) -> Dict[str, AgentBehavior]:
        """
        Load agent behaviors from files.

        Args:
            path: Directory containing behavior files (default: .weave/behaviors/)

        Returns:
            Dictionary of behavior name to AgentBehavior
        """
        behaviors_path = path or self.base_path / "behaviors"
        if not behaviors_path.exists():
            return {}

        behaviors = {}
        for file_path in behaviors_path.glob("*.yaml"):
            behavior = self._load_yaml_resource(file_path, AgentBehavior)
            if behavior:
                behaviors[behavior.name] = behavior
                self._resources[ResourceType.BEHAVIOR][behavior.name] = behavior

        return behaviors

    def load_sub_agents(self, path: Optional[Path] = None) -> Dict[str, SubAgentPrompt]:
        """
        Load sub-agent prompts from files.

        Args:
            path: Directory containing sub-agent files (default: .weave/sub_agents/)

        Returns:
            Dictionary of sub-agent name to SubAgentPrompt
        """
        sub_agents_path = path or self.base_path / "sub_agents"
        if not sub_agents_path.exists():
            return {}

        sub_agents = {}
        for file_path in sub_agents_path.glob("*.yaml"):
            sub_agent = self._load_yaml_resource(file_path, SubAgentPrompt)
            if sub_agent:
                sub_agents[sub_agent.name] = sub_agent
                self._resources[ResourceType.SUB_AGENT][sub_agent.name] = sub_agent

        return sub_agents

    def load_memories(self, path: Optional[Path] = None) -> Dict[str, MemoryResource]:
        """
        Load agent memories from markdown files.

        Args:
            path: Directory containing memory files (default: .weave/memory/)

        Returns:
            Dictionary of agent name to MemoryResource
        """
        memory_path = path or self.base_path / "memory"
        if not memory_path.exists():
            return {}

        memories = {}
        # Load markdown memory files (agent_name_memory.md format)
        for file_path in memory_path.glob("*_memory.md"):
            memory = self._load_memory_file(file_path)
            if memory:
                memories[memory.agent_name] = memory
                self._resources[ResourceType.MEMORY][memory.agent_name] = memory

        return memories

    def get_resource(
        self, resource_type: ResourceType, name: str
    ) -> Optional[Union[SystemPrompt, Skill, Recipe, KnowledgeBase, Rule, AgentBehavior, MemoryResource]]:
        """
        Get a specific resource by type and name.

        Args:
            resource_type: Type of resource
            name: Resource name

        Returns:
            Resource object or None if not found
        """
        return self._resources[resource_type].get(name)

    def list_resources(self, resource_type: Optional[ResourceType] = None) -> Dict[str, List[str]]:
        """
        List all available resources.

        Args:
            resource_type: Optional filter by type

        Returns:
            Dictionary of resource type to list of names
        """
        if resource_type:
            return {resource_type.value: list(self._resources[resource_type].keys())}

        return {
            rt.value: list(resources.keys())
            for rt, resources in self._resources.items()
        }

    def _load_prompt_file(self, file_path: Path) -> Optional[SystemPrompt]:
        """Load a system prompt from a markdown file."""
        try:
            content = file_path.read_text()

            # Parse frontmatter if present (YAML between --- markers)
            metadata = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    content = parts[2].strip()

            return SystemPrompt(
                name=metadata.get("name", file_path.stem),
                content=content,
                description=metadata.get("description", ""),
                tags=metadata.get("tags", []),
                variables=metadata.get("variables", {}),
            )
        except Exception as e:
            print(f"Error loading prompt {file_path}: {e}")
            return None

    def _load_prompt_yaml(self, file_path: Path) -> Optional[SystemPrompt]:
        """Load a system prompt from a YAML config file."""
        return self._load_yaml_resource(file_path, SystemPrompt)

    def _load_knowledge_file(self, file_path: Path, format: str) -> Optional[KnowledgeBase]:
        """Load a knowledge base file."""
        try:
            if format == "json":
                content = json.loads(file_path.read_text())
                content_str = json.dumps(content, indent=2)
            else:
                content_str = file_path.read_text()

            return KnowledgeBase(
                name=file_path.stem,
                content=content_str,
                format=format,
                metadata={"file_path": str(file_path)},
            )
        except Exception as e:
            print(f"Error loading knowledge file {file_path}: {e}")
            return None

    def _load_yaml_resource(self, file_path: Path, model_class):
        """Load a resource from a YAML file using a Pydantic model."""
        try:
            data = yaml.safe_load(file_path.read_text())
            if data is None:
                return None
            return model_class(**data)
        except Exception as e:
            print(f"Error loading {model_class.__name__} from {file_path}: {e}")
            return None

    def _load_memory_file(self, file_path: Path) -> Optional[MemoryResource]:
        """Load agent memory from a markdown file."""
        try:
            content = file_path.read_text()

            # Extract agent name from filename (e.g., "agent1_memory.md" -> "agent1")
            agent_name = file_path.stem.replace("_memory", "")

            return MemoryResource(
                agent_name=agent_name,
                content=content,
                format="markdown",
                metadata={"file_path": str(file_path)},
            )
        except Exception as e:
            print(f"Error loading memory file {file_path}: {e}")
            return None

    def create_default_structure(self) -> None:
        """Create default directory structure for resources."""
        directories = [
            self.base_path / "prompts",
            self.base_path / "skills",
            self.base_path / "recipes",
            self.base_path / "knowledge",
            self.base_path / "rules",
            self.base_path / "behaviors",
            self.base_path / "sub_agents",
            self.base_path / "memory",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Create example files
        self._create_example_files()

    def _create_example_files(self) -> None:
        """Create example resource files."""
        # Example system prompt
        prompt_file = self.base_path / "prompts" / "example.md"
        if not prompt_file.exists():
            prompt_file.write_text("""---
name: helpful_assistant
description: A helpful AI assistant system prompt
tags: [assistant, helpful]
variables:
  agent_name: "AI Assistant"
  role: "helpful assistant"
---

You are {{agent_name}}, a {{role}}.

Your goal is to:
- Help users accomplish their tasks
- Provide clear, accurate information
- Be friendly and professional

Always follow these guidelines:
1. Be concise and clear
2. Ask clarifying questions when needed
3. Admit when you don't know something
""")

        # Example skill
        skill_file = self.base_path / "skills" / "data_analysis.yaml"
        if not skill_file.exists():
            skill_file.write_text("""name: data_analysis
description: Analyze data and extract insights
instructions: |
  1. Review the provided data
  2. Identify patterns and trends
  3. Extract key insights
  4. Present findings clearly
examples:
  - "Analyze sales data for Q4 2023"
  - "Find trends in customer behavior"
required_tools:
  - data_cleaner
  - json_parser
tags:
  - data
  - analysis
""")

        # Example recipe
        recipe_file = self.base_path / "recipes" / "content_creation.yaml"
        if not recipe_file.exists():
            recipe_file.write_text("""name: content_creation
description: Complete content creation workflow
steps:
  - step: research
    action: gather_information
    tools: [web_search]
  - step: outline
    action: create_outline
    input: research
  - step: draft
    action: write_content
    input: outline
  - step: edit
    action: refine_content
    input: draft
inputs:
  topic: string
  target_audience: string
outputs:
  final_content: string
tags:
  - content
  - writing
""")

        # Example knowledge base
        kb_file = self.base_path / "knowledge" / "company_info.md"
        if not kb_file.exists():
            kb_file.write_text("""# Company Information

## About Us
We are a technology company focused on AI solutions.

## Products
- Product A: AI-powered analytics
- Product B: Automation tools

## Values
- Innovation
- Quality
- Customer Focus
""")

        # Example rule
        rule_file = self.base_path / "rules" / "content_guidelines.yaml"
        if not rule_file.exists():
            rule_file.write_text("""name: content_length_check
condition: content_length > 5000
action: split_into_sections
priority: 10
enabled: true
description: Split long content into manageable sections
tags:
  - content
  - formatting
""")

        # Example behavior
        behavior_file = self.base_path / "behaviors" / "professional.yaml"
        if not behavior_file.exists():
            behavior_file.write_text("""name: professional
personality: Professional, courteous, and detail-oriented
constraints:
  - Always use proper grammar
  - Avoid slang or casual language
  - Maintain professional tone
guidelines:
  - Be concise and clear
  - Use bullet points for lists
  - Cite sources when appropriate
examples:
  - input: "yo what's up"
    output: "Hello! How may I assist you today?"
  - input: "gimme the data"
    output: "Certainly, I'll provide the data analysis for you."
tags:
  - professional
  - business
""")

        # Example sub-agent
        sub_agent_file = self.base_path / "sub_agents" / "researcher.yaml"
        if not sub_agent_file.exists():
            sub_agent_file.write_text("""name: researcher
role: Research Specialist
instructions: |
  You are a research specialist focused on gathering accurate information.

  Your responsibilities:
  - Search for relevant sources
  - Verify information accuracy
  - Summarize key findings
  - Cite sources appropriately

  Always be thorough and factual.
context: Research assistant for the main agent
tools:
  - web_search
  - summarizer
tags:
  - research
  - information
""")
