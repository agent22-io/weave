"""Pydantic models for Weave configuration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum


class ModelConfig(BaseModel):
    """Model-specific configuration."""

    provider: str = "openai"  # openai, anthropic, local, etc.
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = Field(default_factory=list)
    api_base: Optional[str] = None
    api_key_env: str = "API_KEY"  # Environment variable name for API key


class MemoryConfig(BaseModel):
    """Memory configuration for an agent."""

    type: str = "buffer"  # buffer, summary, sliding_window, vector
    max_messages: int = 100  # Maximum messages to keep in memory
    summarize_after: Optional[int] = None  # Summarize after N messages
    context_window: int = 4000  # Context window size in tokens
    persist: bool = False  # Save memory to storage
    storage_key: Optional[str] = None  # Key for memory storage


class StorageConfig(BaseModel):
    """Storage configuration for agent state and outputs."""

    enabled: bool = True
    base_path: str = ".weave/storage"  # Base storage directory
    save_outputs: bool = True  # Save agent outputs
    save_memory: bool = False  # Save memory state
    save_logs: bool = True  # Save execution logs
    retention_days: Optional[int] = None  # Auto-delete after N days
    format: str = "json"  # json, yaml, pickle


class AgentConfig(BaseModel):
    """Configuration for an agent's behavior."""

    model_config = ConfigDict(extra="allow")  # Allow custom fields

    temperature: float = 0.7
    max_tokens: int = 1000


class Agent(BaseModel):
    """An AI agent definition."""

    name: str = ""  # Will be injected from dict key
    model: str  # Model name (e.g., "gpt-4", "claude-3-opus")
    model_config: Optional[ModelConfig] = None  # Model-specific configuration
    memory: Optional[MemoryConfig] = None  # Memory configuration
    storage: Optional[StorageConfig] = None  # Storage configuration
    tools: List[str] = Field(default_factory=list)
    inputs: Optional[str] = None  # Reference to another agent
    outputs: Optional[str] = None  # Output key name
    config: Dict[str, Any] = Field(default_factory=dict)  # Backward compatibility

    @field_validator("inputs")
    @classmethod
    def normalize_inputs(cls, v: Optional[str]) -> Optional[str]:
        """Normalize inputs to just agent name (strip .outputs if present)."""
        if v and "." in v:
            return v.split(".")[0]  # "researcher.outputs" -> "researcher"
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure agent name is valid identifier."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Agent name must be alphanumeric with - or _: {v}")
        return v


class Weave(BaseModel):
    """An orchestration flow definition."""

    name: str = ""  # Will be injected from dict key
    description: str = ""
    agents: List[str]

    @field_validator("agents")
    @classmethod
    def validate_agents_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure weave has at least one agent."""
        if not v:
            raise ValueError("Weave must contain at least one agent")
        return v


class ToolParameterDef(BaseModel):
    """Tool parameter definition for YAML config."""

    type: str  # string, number, integer, boolean, array, object
    description: str = ""
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


class CustomToolDef(BaseModel):
    """Custom tool definition for YAML config."""

    description: str
    parameters: Dict[str, ToolParameterDef] = Field(default_factory=dict)
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    handler: Optional[str] = None  # Python module path (e.g., "mymodule.my_function")


class GlobalStorageConfig(BaseModel):
    """Global storage configuration for the entire weave."""

    enabled: bool = True
    base_path: str = ".weave/storage"
    state_file: str = ".weave/state.yaml"  # Weave execution state
    lock_file: str = ".weave/weave.lock"  # Execution lock file
    format: str = "json"  # Storage format (json, yaml)
    auto_cleanup: bool = False  # Auto-cleanup old state
    retention_days: int = 30  # Days to retain old state


class WeaveConfig(BaseModel):
    """Complete Weave configuration file."""

    version: str = "1.0"
    env: Dict[str, str] = Field(default_factory=dict)
    storage: Optional[GlobalStorageConfig] = None  # Global storage configuration
    tools: Dict[str, CustomToolDef] = Field(default_factory=dict)  # Custom tool definitions
    agents: Dict[str, Agent]
    weaves: Dict[str, Weave]

    @model_validator(mode="after")
    def validate_references(self) -> "WeaveConfig":
        """Validate all agent references and tool definitions are valid."""
        agent_names = set(self.agents.keys())

        # Inject agent names into agent objects
        for name, agent in self.agents.items():
            agent.name = name

        # Check inputs reference valid agents
        for name, agent in self.agents.items():
            if agent.inputs and agent.inputs not in agent_names:
                raise ValueError(
                    f"Agent '{name}' references unknown input agent '{agent.inputs}'"
                )

        # Check weaves reference valid agents
        for weave_name, weave in self.weaves.items():
            weave.name = weave_name
            for agent_name in weave.agents:
                if agent_name not in agent_names:
                    raise ValueError(
                        f"Weave '{weave_name}' references unknown agent '{agent_name}'"
                    )

        # Note: We don't validate tool names here because:
        # 1. Built-in tools are loaded at runtime
        # 2. MCP tools come from external servers
        # 3. Tool availability can change dynamically
        # Tool validation happens during execution instead

        return self

    @model_validator(mode="after")
    def ensure_at_least_one_weave(self) -> "WeaveConfig":
        """Ensure at least one weave is defined."""
        if not self.weaves:
            raise ValueError("Configuration must define at least one weave")
        return self
