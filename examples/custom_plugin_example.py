"""
Example custom plugin for Weave.

This demonstrates how to create your own plugin to extend Weave's capabilities.
"""

from typing import Any, Dict, Optional
from weave.plugins import Plugin, PluginCategory, PluginMetadata


class WeatherPlugin(Plugin):
    """
    Example plugin that simulates weather data fetching.

    In a real implementation, this would call a weather API.
    """

    metadata = PluginMetadata(
        name="weather_api",
        version="1.0.0",
        description="Fetch weather data for locations",
        category=PluginCategory.API,
        author="Example Author",
        tags=["weather", "api", "data"],
        requires=["requests"],  # External dependencies needed
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Fetch weather data for a location.

        Args:
            input_data: Location name (string) or dict with location info
            context: Execution context from Weave

        Returns:
            Weather data dictionary
        """
        # Parse input
        if isinstance(input_data, dict):
            location = input_data.get("location", "Unknown")
        else:
            location = str(input_data)

        # Get configuration
        units = self.config.get("units", "celsius")
        include_forecast = self.config.get("include_forecast", False)

        # Mock weather data (real implementation would call API)
        weather_data = {
            "location": location,
            "temperature": 22 if units == "celsius" else 72,
            "units": units,
            "conditions": "Partly cloudy",
            "humidity": 65,
            "wind_speed": 15,
        }

        if include_forecast:
            weather_data["forecast"] = [
                {"day": "Tomorrow", "temp": 24, "conditions": "Sunny"},
                {"day": "Day After", "temp": 20, "conditions": "Rainy"},
            ]

        return weather_data

    def validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate plugin configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if "units" in config:
            valid_units = ["celsius", "fahrenheit"]
            if config["units"] not in valid_units:
                raise ValueError(f"units must be one of: {', '.join(valid_units)}")

        if "include_forecast" in config:
            if not isinstance(config["include_forecast"], bool):
                raise ValueError("include_forecast must be a boolean")


class SentimentAnalyzerPlugin(Plugin):
    """
    Example plugin for sentiment analysis.

    Demonstrates text analysis capabilities.
    """

    metadata = PluginMetadata(
        name="sentiment_analyzer",
        version="1.0.0",
        description="Analyze sentiment of text (positive, negative, neutral)",
        category=PluginCategory.CONTENT_ANALYSIS,
        author="Example Author",
        tags=["sentiment", "nlp", "analysis", "text"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Analyze sentiment of text.

        Args:
            input_data: Text to analyze
            context: Execution context

        Returns:
            Sentiment analysis results
        """
        text = str(input_data)

        # Mock sentiment analysis (real implementation would use NLP model)
        # Count positive/negative words (very simplified)
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "love"]
        negative_words = ["bad", "terrible", "awful", "hate", "horrible", "worst"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.7 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = 0.3 - (negative_count * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5

        # Clamp score
        score = max(0.0, min(1.0, score))

        return {
            "text": text,
            "sentiment": sentiment,
            "score": score,
            "confidence": "high" if abs(score - 0.5) > 0.3 else "medium",
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
        }


class TemplateRendererPlugin(Plugin):
    """
    Example plugin for template rendering.

    Demonstrates content generation capabilities.
    """

    metadata = PluginMetadata(
        name="template_renderer",
        version="1.0.0",
        description="Render text templates with variables",
        category=PluginCategory.CONTENT_GENERATION,
        author="Example Author",
        tags=["template", "rendering", "generation"],
        requires=[],
    )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Render a template with variables.

        Args:
            input_data: Dict with 'template' and 'variables' keys
            context: Execution context

        Returns:
            Rendered template string
        """
        if not isinstance(input_data, dict):
            return {"error": "Input must be a dictionary with 'template' and 'variables'"}

        template = input_data.get("template", "")
        variables = input_data.get("variables", {})

        # Simple variable substitution
        rendered = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))

        return {
            "template": template,
            "rendered": rendered,
            "variables_used": list(variables.keys()),
        }


# Example usage in a .weave.yaml file:
"""
agents:
  weather_agent:
    model: "gpt-4"
    tools:
      - weather_api       # Reference custom plugin
    config:
      weather_api:
        units: "celsius"
        include_forecast: true

  sentiment_agent:
    model: "gpt-4"
    tools:
      - sentiment_analyzer

weaves:
  analysis_pipeline:
    agents: [weather_agent, sentiment_agent]
"""

# To use this plugin:
# 1. Save this file as custom_plugin_example.py
# 2. Load it in your code:
#    from weave.plugins.manager import PluginManager
#    manager = PluginManager()
#    manager.load_plugin_from_file("custom_plugin_example.py")
# 3. Use the plugins in your weave configuration
