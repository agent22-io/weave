"""Models for resource types."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    """Types of resources that can be loaded."""

    SYSTEM_PROMPT = "system_prompt"
    SKILL = "skill"
    RECIPE = "recipe"
    KNOWLEDGE_BASE = "knowledge_base"
    RULE = "rule"
    BEHAVIOR = "behavior"
    SUB_AGENT = "sub_agent"
    MEMORY = "memory"


class SystemPrompt(BaseModel):
    """System prompt for an agent."""

    name: str
    content: str
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    variables: Dict[str, str] = Field(default_factory=dict)


class Skill(BaseModel):
    """A skill that an agent can perform."""

    name: str
    description: str
    instructions: str
    examples: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class Recipe(BaseModel):
    """A reusable workflow recipe."""

    name: str
    description: str
    steps: List[Dict[str, Any]]
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class KnowledgeBase(BaseModel):
    """Knowledge base content."""

    name: str
    content: str
    format: str = "text"  # text, markdown, json
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class Rule(BaseModel):
    """A rule for agent behavior."""

    name: str
    condition: str
    action: str
    priority: int = 0
    enabled: bool = True
    description: str = ""
    tags: List[str] = Field(default_factory=list)


class AgentBehavior(BaseModel):
    """Behavior configuration for an agent."""

    name: str
    personality: str = ""
    constraints: List[str] = Field(default_factory=list)
    guidelines: List[str] = Field(default_factory=list)
    examples: List[Dict[str, str]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class SubAgentPrompt(BaseModel):
    """Prompt configuration for a sub-agent."""

    name: str
    role: str
    instructions: str
    context: str = ""
    tools: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class MemoryResource(BaseModel):
    """Long-term memory for an agent."""

    agent_name: str
    content: str  # Memory content in markdown format
    format: str = "markdown"
    metadata: Dict[str, Any] = Field(default_factory=dict)
