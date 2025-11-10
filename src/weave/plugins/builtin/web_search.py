"""Web search plugin for gathering information from the internet."""

from typing import Any, Dict, Optional

from ..base import Plugin, PluginCategory, PluginMetadata


class WebSearchPlugin(Plugin):
    """Simulates web search functionality."""

    metadata = PluginMetadata(
        name="web_search",
        version="1.0.0",
        description="Search the web for information",
        category=PluginCategory.WEB,
        author="Weave Team",
        tags=["search", "web", "internet", "research"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute web search.

        Args:
            input_data: Search query string
            context: Execution context

        Returns:
            Mock search results
        """
        query = str(input_data)

        # Mock results (in real implementation, would call search API)
        results = {
            "query": query,
            "results": [
                {
                    "title": f"Search result 1 for: {query}",
                    "url": "https://example.com/1",
                    "snippet": f"This is a relevant result for {query}...",
                },
                {
                    "title": f"Search result 2 for: {query}",
                    "url": "https://example.com/2",
                    "snippet": f"Another relevant result about {query}...",
                },
                {
                    "title": f"Search result 3 for: {query}",
                    "url": "https://example.com/3",
                    "snippet": f"More information about {query}...",
                },
            ],
            "total_results": 3,
        }

        return results

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration."""
        # Could validate API keys, rate limits, etc.
        pass
