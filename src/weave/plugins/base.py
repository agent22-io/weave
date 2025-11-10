"""Base plugin infrastructure for Weave."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PluginCategory(str, Enum):
    """Plugin categories for organization."""

    # Data operations
    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    DATA_ANALYSIS = "data_analysis"

    # Content operations
    CONTENT_GENERATION = "content_generation"
    CONTENT_ANALYSIS = "content_analysis"

    # Communication
    WEB = "web"
    API = "api"
    DATABASE = "database"

    # AI/ML
    LLM = "llm"
    EMBEDDING = "embedding"
    IMAGE = "image"

    # Utilities
    FORMATTING = "formatting"
    VALIDATION = "validation"
    TESTING = "testing"

    # Integration
    INTEGRATION = "integration"

    # Custom/Other
    CUSTOM = "custom"


class PluginMetadata(BaseModel):
    """Metadata for a plugin."""

    name: str = Field(..., description="Unique plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="What the plugin does")
    category: PluginCategory = Field(..., description="Plugin category")
    author: str = Field(default="Unknown", description="Plugin author")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    requires: List[str] = Field(default_factory=list, description="Required dependencies")


class PluginConfig(BaseModel):
    """Configuration schema for a plugin."""

    model_config = {"extra": "allow"}  # Allow arbitrary config fields


class Plugin(ABC):
    """
    Base class for all Weave plugins.

    Plugins extend agent capabilities by providing tools and functionality.
    """

    # Plugin metadata (override in subclass)
    metadata: PluginMetadata

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with configuration.

        Args:
            config: Plugin-specific configuration
        """
        self.config = config or {}
        self.validate_config(self.config)

    @abstractmethod
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the plugin's main functionality.

        Args:
            input_data: Input data to process
            context: Optional execution context (agent info, previous outputs, etc.)

        Returns:
            Plugin output
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate plugin configuration.

        Args:
            config: Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def on_load(self) -> None:
        """Called when plugin is loaded. Override for initialization logic."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unloaded. Override for cleanup logic."""
        pass

    def __str__(self) -> str:
        return f"{self.metadata.name} v{self.metadata.version}"

    def __repr__(self) -> str:
        return f"<Plugin: {self.metadata.name} ({self.metadata.category})>"


class PluginRegistry:
    """Registry for managing available plugins."""

    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._categories: Dict[PluginCategory, List[str]] = {
            category: [] for category in PluginCategory
        }

    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance to register

        Raises:
            ValueError: If plugin name already registered
        """
        name = plugin.metadata.name

        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered")

        plugin.on_load()
        self._plugins[name] = plugin
        self._categories[plugin.metadata.category].append(name)

    def unregister(self, name: str) -> None:
        """
        Unregister a plugin.

        Args:
            name: Plugin name to unregister
        """
        if name in self._plugins:
            plugin = self._plugins[name]
            plugin.on_unload()
            self._categories[plugin.metadata.category].remove(name)
            del self._plugins[name]

    def get(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)

    def list(self, category: Optional[PluginCategory] = None) -> List[Plugin]:
        """
        List registered plugins.

        Args:
            category: Optional category filter

        Returns:
            List of plugins
        """
        if category:
            names = self._categories.get(category, [])
            return [self._plugins[name] for name in names]
        return list(self._plugins.values())

    def list_by_tags(self, tags: List[str]) -> List[Plugin]:
        """
        Find plugins by tags.

        Args:
            tags: Tags to search for

        Returns:
            Plugins matching any of the tags
        """
        matching = []
        for plugin in self._plugins.values():
            if any(tag in plugin.metadata.tags for tag in tags):
                matching.append(plugin)
        return matching

    def get_categories(self) -> Dict[PluginCategory, int]:
        """
        Get plugin count by category.

        Returns:
            Dictionary of category to count
        """
        return {category: len(plugins) for category, plugins in self._categories.items()}

    def __contains__(self, name: str) -> bool:
        return name in self._plugins

    def __len__(self) -> int:
        return len(self._plugins)
