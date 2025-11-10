"""OpenRouter plugin for unified access to multiple LLM providers."""

import os
from typing import Any, Dict, Optional
import time

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
        """Initialize OpenRouter plugin with API configuration."""
        super().__init__(config)

        self.api_key = self.config.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        self.api_base = self.config.get("api_base", "https://openrouter.ai/api/v1")
        self.default_model = self.config.get("default_model", "openai/gpt-3.5-turbo")
        self.site_url = self.config.get("site_url", "")
        self.site_name = self.config.get("site_name", "Weave")
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)
        self.fallback_models = self.config.get("fallback_models", [])

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY or provide 'api_key'. "
                "Get your key at: https://openrouter.ai/keys"
            )

    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute LLM request through OpenRouter API."""
        try:
            import requests
        except ImportError:
            raise ImportError("requests required for OpenRouter. Install: pip install requests")

        # Parse input
        if isinstance(input_data, str):
            payload = {"messages": [{"role": "user", "content": input_data}]}
        elif isinstance(input_data, dict):
            payload = input_data.copy()
        else:
            raise ValueError(f"Invalid input type: {type(input_data)}")

        payload.setdefault("model", self.default_model)
        if self.site_url:
            payload.setdefault("site_url", self.site_url)
        if self.site_name:
            payload.setdefault("site_name", self.site_name)

        # Try models with retries
        models_to_try = [payload["model"]] + self.fallback_models
        last_error = None

        for model in models_to_try:
            payload["model"] = model
            for attempt in range(self.max_retries):
                try:
                    return self._make_request(payload, requests)
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff

        raise Exception(
            f"OpenRouter failed after {len(models_to_try)} models, "
            f"{self.max_retries} retries each. Last error: {last_error}"
        )

    def _make_request(self, payload: Dict[str, Any], requests: Any) -> Dict[str, Any]:
        """Make request to OpenRouter API."""
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url or "https://github.com/weave/weave-cli",
            "X-Title": self.site_name or "Weave",
        }

        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)

        if response.status_code != 200:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("error", {}).get("message", response.text)
            raise Exception(f"OpenRouter API error ({response.status_code}): {error_msg}")

        return response.json()

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate plugin configuration."""
        if "timeout" in config and (not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0):
            raise ValueError(f"Invalid timeout: {config['timeout']}")
        if "max_retries" in config and (not isinstance(config["max_retries"], int) or config["max_retries"] < 0):
            raise ValueError(f"Invalid max_retries: {config['max_retries']}")
        if "fallback_models" in config and not isinstance(config["fallback_models"], list):
            raise ValueError("fallback_models must be a list")

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models from OpenRouter."""
        try:
            import requests
            url = f"{self.api_base}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Failed to fetch models: {response.status_code}")
        except Exception as e:
            return {"error": str(e), "message": "Failed to fetch models from OpenRouter API"}

    def __str__(self) -> str:
        return f"OpenRouter Plugin (model: {self.default_model})"
