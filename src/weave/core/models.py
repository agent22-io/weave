"""Pydantic models for Weave configuration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum


class AgentCapability(str, Enum):
    """Standard agent capabilities."""

    # Core capabilities
    CODING = "coding"  # Code generation, analysis, review
    IMAGE_GEN = "image-gen"  # Image generation and manipulation
    IMAGE_ANALYSIS = "image-analysis"  # Image understanding and analysis
    AUDIO_GEN = "audio-gen"  # Audio/music generation
    AUDIO_ANALYSIS = "audio-analysis"  # Audio transcription and analysis
    VIDEO_GEN = "video-gen"  # Video generation
    VIDEO_ANALYSIS = "video-analysis"  # Video understanding

    # Content capabilities
    TEXT_GENERATION = "text-generation"  # Creative writing, content creation
    TEXT_ANALYSIS = "text-analysis"  # NLP, sentiment analysis, summarization
    TRANSLATION = "translation"  # Language translation
    SEARCH = "search"  # Web/knowledge search
    RESEARCH = "research"  # Information gathering and synthesis

    # Technical capabilities
    DATA_PROCESSING = "data-processing"  # Data transformation and analysis
    DATA_VISUALIZATION = "data-visualization"  # Chart and graph creation
    SQL = "sql"  # Database queries and analysis
    API_INTEGRATION = "api-integration"  # External API interaction
    WEB_SCRAPING = "web-scraping"  # Web data extraction

    # Business capabilities
    ANALYTICS = "analytics"  # Business intelligence and reporting
    PLANNING = "planning"  # Strategic planning and organization
    DECISION_MAKING = "decision-making"  # Analysis and recommendations
    CLASSIFICATION = "classification"  # Categorization and tagging
    EXTRACTION = "extraction"  # Information extraction from text

    # Communication capabilities
    EMAIL = "email"  # Email composition and processing
    CHAT = "chat"  # Conversational interaction
    DOCUMENTATION = "documentation"  # Technical documentation
    REPORTING = "reporting"  # Report generation

    # Specialized capabilities
    SECURITY = "security"  # Security analysis and review
    COMPLIANCE = "compliance"  # Regulatory compliance checking
    QA = "qa"  # Quality assurance and testing
    MONITORING = "monitoring"  # System monitoring and alerting
    OPTIMIZATION = "optimization"  # Performance and efficiency optimization


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

    model_config = ConfigDict(populate_by_name=True)  # Pydantic config - must be first

    name: str = ""  # Will be injected from dict key
    model: str  # Model name (e.g., "gpt-4", "claude-3-opus")
    capabilities: List[str] = Field(default_factory=list)  # Agent capabilities
    llm_config: Optional[ModelConfig] = Field(default=None, alias="model_config")  # Model-specific configuration
    memory: Optional[MemoryConfig] = None  # Memory configuration
    storage: Optional[StorageConfig] = None  # Storage configuration
    tools: List[str] = Field(default_factory=list)
    inputs: Optional[str] = None  # Reference to another agent
    outputs: Optional[str] = None  # Output key name
    prompt: Optional[str] = None  # Agent-specific prompt/instructions
    config: Dict[str, Any] = Field(default_factory=dict)  # Backward compatibility

    @property
    def model_settings(self) -> Optional[ModelConfig]:
        """Alias for llm_config to avoid name conflict with Pydantic's model_config."""
        return self.llm_config

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

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, v: List[str]) -> List[str]:
        """Validate capability names against known capabilities."""
        if not v:
            return v

        valid_capabilities = {cap.value for cap in AgentCapability}
        unknown = [cap for cap in v if cap not in valid_capabilities]

        if unknown:
            # Warning only - allow custom capabilities
            import warnings
            warnings.warn(
                f"Unknown capabilities (will be treated as custom): {unknown}. "
                f"Known capabilities: {sorted(valid_capabilities)}"
            )

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


class ObservabilityConfig(BaseModel):
    """Observability configuration for monitoring and debugging."""

    # Logging configuration
    enabled: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "json"  # json, text, structured
    log_file: Optional[str] = ".weave/logs/weave.log"
    log_to_console: bool = True
    log_agent_inputs: bool = True  # Log agent inputs
    log_agent_outputs: bool = True  # Log agent outputs
    log_tool_calls: bool = True  # Log tool invocations

    # Metrics configuration
    collect_metrics: bool = True
    metrics_format: str = "prometheus"  # prometheus, statsd, datadog
    metrics_endpoint: Optional[str] = None
    track_token_usage: bool = True  # Track LLM token usage
    track_latency: bool = True  # Track agent execution time
    track_success_rate: bool = True  # Track success/failure rates

    # Tracing configuration
    enable_tracing: bool = False  # Distributed tracing
    tracing_backend: str = "opentelemetry"  # opentelemetry, jaeger, zipkin
    tracing_endpoint: Optional[str] = None
    trace_sampling_rate: float = 1.0  # 0.0 to 1.0

    # Export configuration
    export_traces: bool = False
    export_metrics: bool = False
    export_logs: bool = False
    export_dir: str = ".weave/exports"


class RuntimeConfig(BaseModel):
    """Runtime execution configuration."""

    # Execution mode
    mode: str = "sequential"  # sequential, parallel, async
    max_concurrent_agents: int = 1  # Max agents running in parallel
    enable_caching: bool = True  # Cache agent outputs

    # Retry policy
    max_retries: int = 0  # Number of retries on failure
    retry_delay: float = 1.0  # Initial retry delay in seconds
    retry_backoff: str = "exponential"  # exponential, linear, constant
    retry_backoff_multiplier: float = 2.0  # Backoff multiplier
    retry_on_errors: List[str] = Field(default_factory=lambda: ["timeout", "api_error"])

    # Timeouts
    default_timeout: Optional[float] = 300.0  # Default agent timeout (seconds)
    weave_timeout: Optional[float] = 3600.0  # Total weave timeout (seconds)
    tool_timeout: Optional[float] = 60.0  # Tool execution timeout (seconds)

    # Rate limiting
    enable_rate_limiting: bool = False
    requests_per_minute: int = 60
    tokens_per_minute: Optional[int] = None

    # Resource limits
    max_memory_mb: Optional[int] = None  # Max memory per agent
    max_cpu_percent: Optional[float] = None  # Max CPU usage

    # Error handling
    stop_on_error: bool = True  # Stop execution on first error
    continue_on_agent_failure: bool = False  # Continue if agent fails
    save_partial_results: bool = True  # Save results of successful agents

    # Execution options
    dry_run: bool = False  # Dry run mode (no actual execution)
    verbose: bool = False  # Verbose output
    debug: bool = False  # Debug mode


class ProviderConfig(BaseModel):
    """Cloud/infrastructure provider configuration."""

    # Provider identification
    provider: str = "local"  # local, aws, azure, gcp, kubernetes, docker
    name: Optional[str] = None  # Provider instance name

    # Credentials
    credentials_source: str = "env"  # env, file, vault, keychain
    credentials_path: Optional[str] = None  # Path to credentials file
    credentials_env_prefix: str = ""  # Environment variable prefix

    # Region/Location
    region: Optional[str] = None  # Provider region (e.g., us-east-1, westus2)
    zone: Optional[str] = None  # Availability zone

    # Provider-specific settings
    aws: Optional[Dict[str, Any]] = None  # AWS-specific config
    azure: Optional[Dict[str, Any]] = None  # Azure-specific config
    gcp: Optional[Dict[str, Any]] = None  # GCP-specific config
    kubernetes: Optional[Dict[str, Any]] = None  # K8s-specific config

    # API configuration
    api_endpoint: Optional[str] = None  # Custom API endpoint
    api_version: Optional[str] = None  # API version
    timeout: float = 30.0  # API timeout in seconds

    # Tags/Labels
    tags: Dict[str, str] = Field(default_factory=dict)


class EnvironmentConfig(BaseModel):
    """Environment/staging configuration."""

    # Environment identification
    name: str  # dev, staging, production, test
    description: Optional[str] = None

    # Environment overrides
    config_overrides: Dict[str, Any] = Field(default_factory=dict)

    # Secrets management
    secrets_backend: str = "env"  # env, vault, aws-secrets, azure-keyvault, gcp-secret-manager
    secrets_path: Optional[str] = None

    # Environment variables
    env_vars: Dict[str, str] = Field(default_factory=dict)
    env_file: Optional[str] = None  # Path to .env file

    # Feature flags
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

    # Promotion/Demotion
    promote_to: Optional[str] = None  # Next environment (staging -> production)
    require_approval: bool = False  # Require approval for promotion

    # Environment constraints
    max_concurrent_runs: Optional[int] = None
    allowed_models: Optional[List[str]] = None  # Restrict models per environment


class InfrastructureConfig(BaseModel):
    """Infrastructure requirements and configuration."""

    # Compute resources
    cpu: Optional[str] = None  # CPU request (e.g., "2", "500m")
    memory: Optional[str] = None  # Memory request (e.g., "4Gi", "512Mi")
    gpu: Optional[str] = None  # GPU request (e.g., "1", "nvidia-tesla-t4")

    # Resource limits
    cpu_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    gpu_limit: Optional[str] = None

    # Networking
    network_mode: str = "bridge"  # bridge, host, none
    vpc_id: Optional[str] = None
    subnet_ids: List[str] = Field(default_factory=list)
    security_groups: List[str] = Field(default_factory=list)
    load_balancer: Optional[str] = None

    # Storage
    persistent_volumes: List[Dict[str, Any]] = Field(default_factory=list)
    ephemeral_storage: Optional[str] = None

    # Scaling
    min_replicas: int = 1
    max_replicas: int = 1
    auto_scaling: bool = False
    scaling_metric: str = "cpu"  # cpu, memory, requests, custom
    scaling_threshold: float = 70.0  # Percentage or value

    # Container configuration
    image: Optional[str] = None  # Container image
    image_pull_policy: str = "IfNotPresent"  # Always, IfNotPresent, Never
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None

    # Service mesh
    service_mesh: bool = False
    service_mesh_type: Optional[str] = None  # istio, linkerd, consul

    # Labels and annotations
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)


class DeploymentConfig(BaseModel):
    """Deployment strategy and configuration."""

    # Deployment identification
    name: Optional[str] = None
    version: Optional[str] = None

    # Deployment strategy
    strategy: str = "rolling"  # rolling, blue-green, canary, recreate, manual

    # Rolling update configuration
    max_surge: str = "25%"  # Max pods above desired during update
    max_unavailable: str = "25%"  # Max pods unavailable during update

    # Canary deployment
    canary_percentage: float = 10.0  # Initial canary traffic percentage
    canary_increment: float = 10.0  # Traffic increment per step
    canary_interval: int = 300  # Seconds between increments

    # Blue-green deployment
    blue_green_active: str = "blue"  # Which environment is active

    # Health checks
    health_check_enabled: bool = True
    health_check_path: str = "/health"
    health_check_interval: int = 10  # Seconds
    health_check_timeout: int = 5  # Seconds
    health_check_retries: int = 3

    # Readiness checks
    readiness_check_enabled: bool = True
    readiness_check_path: str = "/ready"
    readiness_check_initial_delay: int = 30  # Seconds

    # Liveness checks
    liveness_check_enabled: bool = True
    liveness_check_path: str = "/health"
    liveness_check_initial_delay: int = 60  # Seconds

    # Rollback configuration
    auto_rollback: bool = True
    rollback_on_failure: bool = True
    rollback_threshold: float = 0.05  # Error rate threshold for rollback (5%)
    revision_history_limit: int = 10

    # CI/CD integration
    ci_cd_enabled: bool = False
    ci_cd_provider: Optional[str] = None  # github-actions, gitlab-ci, jenkins, etc.
    ci_cd_webhook: Optional[str] = None

    # Pre/Post deployment hooks
    pre_deploy_hooks: List[str] = Field(default_factory=list)
    post_deploy_hooks: List[str] = Field(default_factory=list)

    # Deployment notifications
    notifications_enabled: bool = False
    notification_channels: List[str] = Field(default_factory=list)  # slack, email, pagerduty

    # Versioning
    versioning_strategy: str = "semantic"  # semantic, timestamp, commit-sha
    version_prefix: Optional[str] = None

    # Deployment windows
    maintenance_windows: List[Dict[str, str]] = Field(default_factory=list)
    allow_deploy_on_weekend: bool = True
    allow_deploy_on_holiday: bool = False


class MCPServerConfig(BaseModel):
    """MCP server configuration."""

    command: str  # Command to start the MCP server
    args: List[str] = Field(default_factory=list)  # Command arguments
    env: Dict[str, str] = Field(default_factory=dict)  # Environment variables
    description: str = ""  # Server description
    enabled: bool = True  # Whether the server is enabled


class WeaveConfig(BaseModel):
    """Complete Weave configuration file."""

    version: str = "1.0"
    env: Dict[str, str] = Field(default_factory=dict)

    # Core configuration
    storage: Optional[GlobalStorageConfig] = None  # Global storage configuration
    observability: Optional[ObservabilityConfig] = None  # Observability configuration
    runtime: Optional[RuntimeConfig] = None  # Runtime configuration

    # Deployment configuration
    provider: Optional[ProviderConfig] = None  # Cloud/infrastructure provider
    environment: Optional[EnvironmentConfig] = None  # Environment/staging settings
    infrastructure: Optional[InfrastructureConfig] = None  # Infrastructure requirements
    deployment: Optional[DeploymentConfig] = None  # Deployment strategy

    # Tool and server configuration
    tools: Dict[str, CustomToolDef] = Field(default_factory=dict)  # Custom tool definitions
    mcp_servers: Dict[str, MCPServerConfig] = Field(default_factory=dict)  # MCP server configurations

    # Agent and workflow definitions
    agents: Dict[str, Agent]
    weaves: Dict[str, Weave]

    @model_validator(mode="after")
    def validate_references(self) -> "WeaveConfig":
        """Validate all agent references and tool definitions are valid."""
        from ..core.exceptions import ConfigError
        import difflib

        agent_names = set(self.agents.keys())

        # Inject agent names into agent objects
        for name, agent in self.agents.items():
            agent.name = name

        # Check inputs reference valid agents
        for name, agent in self.agents.items():
            if agent.inputs and agent.inputs not in agent_names:
                # Find similar agent names
                similar = difflib.get_close_matches(
                    agent.inputs, agent_names, n=3, cutoff=0.6
                )

                error_msg = f"Agent '{name}' references unknown input agent '{agent.inputs}'"

                if similar:
                    suggestion = f"Did you mean: {', '.join(similar)}?"
                else:
                    suggestion = f"Available agents: {', '.join(sorted(agent_names))}"

                raise ConfigError(error_msg, suggestion=suggestion)

        # Check weaves reference valid agents
        for weave_name, weave in self.weaves.items():
            weave.name = weave_name
            for agent_name in weave.agents:
                if agent_name not in agent_names:
                    # Find similar agent names
                    similar = difflib.get_close_matches(
                        agent_name, agent_names, n=3, cutoff=0.6
                    )

                    error_msg = f"Weave '{weave_name}' references unknown agent '{agent_name}'"

                    if similar:
                        suggestion = f"Did you mean: {', '.join(similar)}?"
                    else:
                        suggestion = f"Available agents: {', '.join(sorted(agent_names))}"

                    raise ConfigError(error_msg, suggestion=suggestion)

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
