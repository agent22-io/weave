"""Plugin manager for loading and managing plugins."""

import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from .base import Plugin, PluginCategory, PluginRegistry


class PluginManager:
    """
    Manages plugin lifecycle and discovery.

    Handles loading built-in plugins, discovering community plugins,
    and providing plugins to the runtime.
    """

    def __init__(self, console: Optional[Console] = None):
        self.registry = PluginRegistry()
        self.console = console or Console()
        self._loaded = False

    def load_builtin_plugins(self) -> None:
        """Load all built-in plugins."""
        # Import and register built-in plugins
        from .builtin import (
            WebSearchPlugin,
            TextSummarizerPlugin,
            DataCleanerPlugin,
            JSONParserPlugin,
            MarkdownFormatterPlugin,
        )

        builtin_plugins = [
            WebSearchPlugin(),
            TextSummarizerPlugin(),
            DataCleanerPlugin(),
            JSONParserPlugin(),
            MarkdownFormatterPlugin(),
        ]

        for plugin in builtin_plugins:
            try:
                self.registry.register(plugin)
            except ValueError as e:
                self.console.print(f"[yellow]Warning: {e}[/yellow]")

        self._loaded = True

    def load_plugin_from_file(self, path: Path) -> None:
        """
        Load a plugin from a Python file.

        Args:
            path: Path to plugin Python file

        Raises:
            ImportError: If plugin cannot be loaded
            ValueError: If plugin is invalid
        """
        spec = importlib.util.spec_from_file_location("custom_plugin", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin from {path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find Plugin subclass in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Plugin)
                and attr is not Plugin
            ):
                plugin = attr()
                self.registry.register(plugin)
                return

        raise ValueError(f"No Plugin class found in {path}")

    def load_plugins_from_directory(self, directory: Path) -> None:
        """
        Load all plugins from a directory.

        Args:
            directory: Directory containing plugin files
        """
        if not directory.exists():
            return

        for plugin_file in directory.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                self.load_plugin_from_file(plugin_file)
            except Exception as e:
                self.console.print(
                    f"[yellow]Failed to load {plugin_file.name}: {e}[/yellow]"
                )

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        if not self._loaded:
            self.load_builtin_plugins()

        return self.registry.get(name)

    def execute_plugin(
        self,
        name: str,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a plugin by name.

        Args:
            name: Plugin name
            input_data: Input data for plugin
            context: Execution context
            config: Plugin configuration override

        Returns:
            Plugin output

        Raises:
            ValueError: If plugin not found
        """
        plugin = self.get_plugin(name)
        if plugin is None:
            available = ", ".join(p.metadata.name for p in self.registry.list())
            raise ValueError(
                f"Plugin '{name}' not found. Available plugins: {available}"
            )

        # Override config if provided
        if config:
            plugin.config.update(config)

        return plugin.execute(input_data, context)

    def list_plugins(
        self, category: Optional[PluginCategory] = None, verbose: bool = False
    ) -> None:
        """
        Display list of available plugins.

        Args:
            category: Filter by category
            verbose: Show detailed information
        """
        if not self._loaded:
            self.load_builtin_plugins()

        plugins = self.registry.list(category)

        if not plugins:
            self.console.print("[yellow]No plugins found[/yellow]")
            return

        # Create table
        table = Table(title="Available Plugins", show_header=True, header_style="bold magenta")

        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Category", style="yellow")

        if verbose:
            table.add_column("Description", style="white")
            table.add_column("Author", style="dim")

        for plugin in plugins:
            row = [
                plugin.metadata.name,
                plugin.metadata.version,
                plugin.metadata.category.value,
            ]

            if verbose:
                row.extend([plugin.metadata.description, plugin.metadata.author])

            table.add_row(*row)

        self.console.print(table)

        # Show summary
        categories = self.registry.get_categories()
        active_categories = {cat: count for cat, count in categories.items() if count > 0}

        self.console.print(f"\n[bold]Total plugins:[/bold] {len(plugins)}")
        if not category:
            self.console.print(f"[bold]Categories:[/bold] {len(active_categories)}")

    def get_plugins_for_agent(self, agent_tools: List[str]) -> Dict[str, Plugin]:
        """
        Get plugins matching agent's tool list.

        Args:
            agent_tools: List of tool names from agent config

        Returns:
            Dictionary of tool name to plugin
        """
        if not self._loaded:
            self.load_builtin_plugins()

        plugins = {}
        for tool_name in agent_tools:
            plugin = self.registry.get(tool_name)
            if plugin:
                plugins[tool_name] = plugin

        return plugins

    def validate_agent_tools(self, agent_tools: List[str]) -> List[str]:
        """
        Validate that all agent tools have corresponding plugins.

        Args:
            agent_tools: List of tool names

        Returns:
            List of missing tool names
        """
        if not self._loaded:
            self.load_builtin_plugins()

        missing = []
        for tool_name in agent_tools:
            if tool_name not in self.registry:
                missing.append(tool_name)

        return missing
