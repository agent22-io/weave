"""Markdown formatting plugin."""

from typing import Any, Dict, Optional

from ..base import Plugin, PluginCategory, PluginMetadata


class MarkdownFormatterPlugin(Plugin):
    """Formats data as Markdown."""

    metadata = PluginMetadata(
        name="markdown_formatter",
        version="1.0.0",
        description="Format data as Markdown documents",
        category=PluginCategory.FORMATTING,
        author="Weave Team",
        tags=["markdown", "formatting", "documentation", "output"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Format data as Markdown.

        Args:
            input_data: Data to format (string, list, or dict)
            context: Execution context

        Returns:
            Markdown-formatted string
        """
        if isinstance(input_data, str):
            return input_data

        elif isinstance(input_data, dict):
            return self._format_dict(input_data)

        elif isinstance(input_data, list):
            return self._format_list(input_data)

        else:
            return str(input_data)

    def _format_dict(self, data: Dict) -> str:
        """Format dictionary as Markdown."""
        lines = []

        title = self.config.get("title", "Data")
        lines.append(f"# {title}\n")

        for key, value in data.items():
            lines.append(f"## {key}")
            lines.append("")

            if isinstance(value, (list, dict)):
                lines.append("```json")
                import json

                lines.append(json.dumps(value, indent=2))
                lines.append("```")
            else:
                lines.append(str(value))

            lines.append("")

        return "\n".join(lines)

    def _format_list(self, items: list) -> str:
        """Format list as Markdown."""
        lines = []

        title = self.config.get("title", "List")
        lines.append(f"# {title}\n")

        for i, item in enumerate(items, 1):
            if isinstance(item, str):
                lines.append(f"{i}. {item}")
            else:
                lines.append(f"{i}. `{str(item)}`")

        return "\n".join(lines)

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration."""
        if "title" in config and not isinstance(config["title"], str):
            raise ValueError("title must be a string")
