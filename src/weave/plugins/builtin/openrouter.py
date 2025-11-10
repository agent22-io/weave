"""OpenRouter plugin for unified access to multiple LLM providers."""

import os
from typing import Any, Dict, Optional

from ..base import Plugin, PluginCategory, PluginMetadata


class OpenRouterPlugin(Plugin):
    """
    OpenRouter integration plugin for unified LLM access.

    OpenRouter provides a unified API to access models from multiple providers:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude 3)
    - Google (Gemini, PaLM)
    - Meta (Llama 2, Code Llama)
    - Mistral AI
    - And many more

    Benefits:
    - Single API for multiple providers
    - Automatic fallbacks
    - Cost optimization
    - Rate limit management
    """

    metadata = PluginMetadata(
        name="openrouter",
        version="1.0.0",
        description="Unified access to multiple LLM providers through OpenRouter API",
        category=PluginCategory.LLM,
        author="Weave Team",
        tags=["llm", "api", "openai", "anthropic", "multi-model", "openrouter"],
        requires=["requests"],
    )

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenRouter plugin.

        Configuration options:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            api_base: API base URL (default: https://openrouter.ai/api/v1)
            default_model: Default model to use
            site_url: Your site URL for OpenRouter rankings
            site_name: Your site name for OpenRouter rankings
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum number of retries (default: 3)
            fallback_models: List of fallback models to try on failure
        """
        super().__init__(config)

        # API configuration
        self.api_key = self.config.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        self.api_base = self.config.get(
            "api_base", "https://openrouter.ai/api/v1"
        )
        self.default_model = self.config.get("default_model", "openai/gpt-3.5-turbo")

        # Site information (helps OpenRouter improve rankings)
        self.site_url = self.config.get("site_url", "")
        self.site_name = self.config.get("site_name", "Weave")

        # Request configuration
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)
        self.fallback_models = self.config.get("fallback_models", [])

        # Validate API key
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY environment "
                "variable or provide 'api_key' in plugin configuration. "
                "Get your key at: https://openrouter.ai/keys"
            )

    def execute(
        self, input_data: Any, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute LLM request through OpenRouter.

        Args:
            input_data: Request payload (dict or string)
                If dict, should contain:
                    - messages: List of messages (required)
                    - model: Model to use (optional, uses default_model)
                    - temperature: Temperature (optional)
                    - max_tokens: Max tokens (optional)
                    - top_p: Top P (optional)
                    - Other OpenAI-compatible parameters
                If string, treated as single user message
            context: Execution context (optional)

        Returns:
            LLM response dict with:
                - id: Response ID
                - model: Model used
                - choices: List of completion choices
                - usage: Token usage information
        """
        # Parse input
        if isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
            payload = {"messages": messages}
        elif isinstance(input_data, dict):
            payload = input_data.copy()
        else:
            raise ValueError(
                f"Invalid input type: {type(input_data)}. "
                "Expected str or dict with 'messages' field."
            )

        # Ensure model is specified
        if "model" not in payload:
            payload["model"] = self.default_model

        # Add site information for rankings
        if self.site_url:
            payload.setdefault("site_url", self.site_url)
        if self.site_name:
            payload.setdefault("site_name", self.site_name)

        # Mock response for v0.1.0 (v2.0 will implement actual API calls)
        model = payload["model"]
        messages = payload.get("messages", [])

        # Simulate response
        response = {
            "id": "or-mock-id-12345",
            "model": model,
            "object": "chat.completion",
            "created": 1234567890,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": self._generate_mock_response(messages, model),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": sum(
                    len(str(m.get("content", "")).split()) for m in messages
                ),
                "completion_tokens": 50,
                "total_tokens": sum(
                    len(str(m.get("content", "")).split()) for m in messages
                )
                + 50,
            },
        }

        return response

    def _generate_mock_response(self, messages: list, model: str) -> str:
        """Generate a mock response based on the conversation."""
        last_message = messages[-1] if messages else {}
        user_content = str(last_message.get("content", ""))

        return (
            f"[Mock response from {model} via OpenRouter]\n\n"
            f"This is a simulated response to: '{user_content[:100]}...'\n\n"
            f"In v2.0, this will make actual API calls to OpenRouter, "
            f"which provides unified access to {model} and many other models.\n\n"
            f"OpenRouter Benefits:\n"
            f"- Access 100+ models through one API\n"
            f"- Automatic fallbacks and retries\n"
            f"- Cost optimization\n"
            f"- No need for multiple API keys"
        )

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate plugin configuration."""
        # Validate timeout
        if "timeout" in config:
            timeout = config["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ValueError(
                    f"Invalid timeout: {timeout}. Must be positive number."
                )

        # Validate max_retries
        if "max_retries" in config:
            retries = config["max_retries"]
            if not isinstance(retries, int) or retries < 0:
                raise ValueError(
                    f"Invalid max_retries: {retries}. Must be non-negative integer."
                )

        # Validate fallback_models
        if "fallback_models" in config:
            fallbacks = config["fallback_models"]
            if not isinstance(fallbacks, list):
                raise ValueError(
                    f"Invalid fallback_models: {fallbacks}. Must be a list."
                )

    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available models from OpenRouter.

        Returns:
            Dict with model information including:
                - id: Model identifier
                - name: Human-readable name
                - pricing: Cost per token
                - context_length: Maximum context size
        """
        # Mock response for v0.1.0
        return {
            "models": [
                {
                    "id": "openai/gpt-4",
                    "name": "GPT-4",
                    "pricing": {"prompt": 0.03, "completion": 0.06},
                    "context_length": 8192,
                },
                {
                    "id": "openai/gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "pricing": {"prompt": 0.001, "completion": 0.002},
                    "context_length": 4096,
                },
                {
                    "id": "anthropic/claude-3-opus",
                    "name": "Claude 3 Opus",
                    "pricing": {"prompt": 0.015, "completion": 0.075},
                    "context_length": 200000,
                },
                {
                    "id": "google/gemini-pro",
                    "name": "Gemini Pro",
                    "pricing": {"prompt": 0.0005, "completion": 0.0015},
                    "context_length": 32768,
                },
                {
                    "id": "meta-llama/llama-2-70b-chat",
                    "name": "Llama 2 70B Chat",
                    "pricing": {"prompt": 0.0007, "completion": 0.0009},
                    "context_length": 4096,
                },
            ]
        }

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Estimate cost for a request.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model identifier

        Returns:
            Estimated cost in USD
        """
        # Mock pricing for v0.1.0
        pricing = {
            "openai/gpt-4": {"prompt": 0.03, "completion": 0.06},
            "openai/gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
            "anthropic/claude-3-opus": {"prompt": 0.015, "completion": 0.075},
            "google/gemini-pro": {"prompt": 0.0005, "completion": 0.0015},
        }

        model_pricing = pricing.get(model, {"prompt": 0.001, "completion": 0.002})

        prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * model_pricing["completion"]

        return prompt_cost + completion_cost

    def __str__(self) -> str:
        return f"OpenRouter Plugin (default_model: {self.default_model})"
