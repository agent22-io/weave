"""Text summarization plugin."""

from typing import Any, Dict, Optional

from ..base import Plugin, PluginCategory, PluginMetadata


class TextSummarizerPlugin(Plugin):
    """Summarizes long text into concise summaries."""

    metadata = PluginMetadata(
        name="summarizer",
        version="1.0.0",
        description="Summarize long text into shorter form",
        category=PluginCategory.CONTENT_ANALYSIS,
        author="Weave Team",
        tags=["text", "summarization", "nlp", "content"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Summarize text.

        Args:
            input_data: Text to summarize
            context: Execution context

        Returns:
            Summary of text
        """
        text = str(input_data)
        max_length = self.config.get("max_length", 200)

        # Mock summarization (real implementation would use NLP model)
        if len(text) <= max_length:
            return text

        summary = text[: max_length - 3] + "..."

        return {
            "original_length": len(text),
            "summary_length": len(summary),
            "summary": summary,
            "compression_ratio": len(summary) / len(text),
        }

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration."""
        if "max_length" in config:
            if not isinstance(config["max_length"], int) or config["max_length"] <= 0:
                raise ValueError("max_length must be a positive integer")
