"""Built-in plugins for Weave."""

from .web_search import WebSearchPlugin
from .text_summarizer import TextSummarizerPlugin
from .data_cleaner import DataCleanerPlugin
from .json_parser import JSONParserPlugin
from .markdown_formatter import MarkdownFormatterPlugin
from .openrouter import OpenRouterPlugin

__all__ = [
    "WebSearchPlugin",
    "TextSummarizerPlugin",
    "DataCleanerPlugin",
    "JSONParserPlugin",
    "MarkdownFormatterPlugin",
    "OpenRouterPlugin",
]
