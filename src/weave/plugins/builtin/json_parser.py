"""JSON parsing plugin."""

import json
from typing import Any, Dict, Optional

from ..base import Plugin, PluginCategory, PluginMetadata


class JSONParserPlugin(Plugin):
    """Parses and validates JSON data."""

    metadata = PluginMetadata(
        name="json_parser",
        version="1.0.0",
        description="Parse and validate JSON data",
        category=PluginCategory.DATA_PROCESSING,
        author="Weave Team",
        tags=["json", "parsing", "data", "validation"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Parse JSON data.

        Args:
            input_data: JSON string or data structure
            context: Execution context

        Returns:
            Parsed JSON or validation result
        """
        if isinstance(input_data, str):
            # Parse JSON string
            try:
                parsed = json.loads(input_data)
                return {
                    "status": "success",
                    "data": parsed,
                    "type": type(parsed).__name__,
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "line": e.lineno,
                    "column": e.colno,
                }
        else:
            # Validate data is JSON-serializable
            try:
                serialized = json.dumps(input_data)
                return {
                    "status": "valid",
                    "size": len(serialized),
                    "serialized": serialized if self.config.get("include_output", False) else None,
                }
            except (TypeError, ValueError) as e:
                return {"status": "invalid", "error": str(e)}

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration."""
        if "include_output" in config and not isinstance(config["include_output"], bool):
            raise ValueError("include_output must be a boolean")
