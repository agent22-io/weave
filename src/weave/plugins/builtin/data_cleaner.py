"""Data cleaning plugin."""

from typing import Any, Dict, List, Optional

from ..base import Plugin, PluginCategory, PluginMetadata


class DataCleanerPlugin(Plugin):
    """Cleans and normalizes data."""

    metadata = PluginMetadata(
        name="data_cleaner",
        version="1.0.0",
        description="Clean and normalize data (remove nulls, whitespace, etc.)",
        category=PluginCategory.DATA_PROCESSING,
        author="Weave Team",
        tags=["data", "cleaning", "preprocessing", "etl"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Clean data.

        Args:
            input_data: Data to clean (list, dict, or string)
            context: Execution context

        Returns:
            Cleaned data
        """
        if isinstance(input_data, str):
            return self._clean_string(input_data)
        elif isinstance(input_data, list):
            return self._clean_list(input_data)
        elif isinstance(input_data, dict):
            return self._clean_dict(input_data)
        else:
            return input_data

    def _clean_string(self, text: str) -> str:
        """Clean a string."""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Strip whitespace
        text = text.strip()
        return text

    def _clean_list(self, items: List) -> List:
        """Clean a list."""
        cleaned = []
        for item in items:
            # Remove None values
            if item is None:
                continue
            # Recursively clean
            cleaned_item = self.execute(item)
            cleaned.append(cleaned_item)
        return cleaned

    def _clean_dict(self, data: Dict) -> Dict:
        """Clean a dictionary."""
        cleaned = {}
        for key, value in data.items():
            # Skip None values
            if value is None and self.config.get("remove_null", True):
                continue
            # Recursively clean
            cleaned[key] = self.execute(value)
        return cleaned

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration."""
        if "remove_null" in config and not isinstance(config["remove_null"], bool):
            raise ValueError("remove_null must be a boolean")
