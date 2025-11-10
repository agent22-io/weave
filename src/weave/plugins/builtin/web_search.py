"""Web search plugin using DuckDuckGo (no API key required)."""

from typing import Any, Dict, Optional
import json

from ..base import Plugin, PluginCategory, PluginMetadata


class WebSearchPlugin(Plugin):
    """Real web search functionality using DuckDuckGo."""

    metadata = PluginMetadata(
        name="web_search",
        version="1.0.0",
        description="Search the web using DuckDuckGo",
        category=PluginCategory.WEB,
        author="Weave Team",
        tags=["search", "web", "internet", "research", "duckduckgo"],
        requires=["requests"],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute web search using DuckDuckGo Instant Answer API.

        Args:
            input_data: Search query string
            context: Execution context (optional)

        Returns:
            Search results with titles, URLs, and snippets
        """
        query = str(input_data)

        try:
            import requests
            from urllib.parse import quote

            # Use DuckDuckGo Instant Answer API (no API key required)
            # Note: This returns structured data but limited results
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"

            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Weave-CLI/1.0'
            })
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []

            # Add abstract if available
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                    "source": data.get("AbstractSource", "DuckDuckGo"),
                })

            # Add related topics
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "DuckDuckGo",
                    })

            return {
                "query": query,
                "results": results if results else [{
                    "title": f"No instant results for: {query}",
                    "url": f"https://duckduckgo.com/?q={quote(query)}",
                    "snippet": "Try searching directly on DuckDuckGo for more results.",
                    "source": "DuckDuckGo",
                }],
                "total_results": len(results),
                "search_engine": "DuckDuckGo",
            }

        except ImportError:
            raise ImportError(
                "requests library is required for web search. "
                "Install with: pip install requests"
            )
        except Exception as e:
            # Return error information
            return {
                "query": query,
                "error": str(e),
                "results": [{
                    "title": f"Search failed: {str(e)}",
                    "url": f"https://duckduckgo.com/?q={quote(query)}",
                    "snippet": "The search request failed. Try the DuckDuckGo link for manual search.",
                    "source": "Error",
                }],
                "total_results": 0,
            }

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration - DuckDuckGo doesn't require API keys."""
        pass
