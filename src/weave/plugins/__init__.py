"""Weave plugin system for extending agent capabilities."""

from .base import Plugin, PluginCategory, PluginRegistry
from .manager import PluginManager

__all__ = ["Plugin", "PluginCategory", "PluginRegistry", "PluginManager"]
