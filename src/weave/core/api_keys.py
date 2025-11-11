"""API key management for Weave."""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet

from .env_loader import load_env_file


class APIKeyManager:
    """Manage API keys for LLM providers.

    Keys are stored encrypted in ~/.weave/api_keys.yaml
    Falls back to environment variables if key not found.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize API key manager.

        Args:
            config_dir: Config directory (default: ~/.weave)
        """
        # Load .env file from project directory first
        load_env_file()

        self.config_dir = config_dir or Path.home() / ".weave"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.keys_file = self.config_dir / "api_keys.yaml"
        self.key_file = self.config_dir / ".key"

        # Initialize encryption key
        self._ensure_encryption_key()
        self.cipher = Fernet(self._load_encryption_key())

    def _ensure_encryption_key(self):
        """Ensure encryption key exists."""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            # Secure the key file
            os.chmod(self.key_file, 0o600)

    def _load_encryption_key(self) -> bytes:
        """Load encryption key."""
        return self.key_file.read_bytes()

    def set_key(self, provider: str, api_key: str) -> None:
        """Set API key for a provider.

        Args:
            provider: Provider name (openai, anthropic, openrouter, etc.)
            api_key: API key value
        """
        # Load existing keys
        keys = self._load_keys_encrypted()

        # Encrypt and store new key
        encrypted = self.cipher.encrypt(api_key.encode()).decode()
        keys[provider.lower()] = encrypted

        # Save
        self._save_keys_encrypted(keys)

        # Secure the keys file
        os.chmod(self.keys_file, 0o600)

    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider.

        Falls back to environment variable if not found in config.

        Args:
            provider: Provider name (openai, anthropic, openrouter, etc.)

        Returns:
            API key or None if not found
        """
        provider = provider.lower()

        # Try config file first
        keys = self._load_keys_encrypted()
        if provider in keys:
            try:
                encrypted = keys[provider].encode()
                return self.cipher.decrypt(encrypted).decode()
            except Exception:
                # Decryption failed, fall through to env var
                pass

        # Fall back to environment variable
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "google": "GOOGLE_API_KEY",
            "cohere": "COHERE_API_KEY",
        }

        env_var = env_var_map.get(provider, f"{provider.upper()}_API_KEY")
        return os.getenv(env_var)

    def remove_key(self, provider: str) -> bool:
        """Remove API key for a provider.

        Args:
            provider: Provider name

        Returns:
            True if key was removed, False if not found
        """
        keys = self._load_keys_encrypted()
        provider = provider.lower()

        if provider in keys:
            del keys[provider]
            self._save_keys_encrypted(keys)
            return True

        return False

    def list_providers(self) -> Dict[str, bool]:
        """List configured providers and their key status.

        Returns:
            Dict mapping provider name to whether key is set
        """
        keys = self._load_keys_encrypted()
        result = {}

        # Check config file
        for provider in keys.keys():
            result[provider] = True

        # Check common environment variables
        env_providers = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }

        for provider, env_var in env_providers.items():
            if provider not in result and os.getenv(env_var):
                result[provider] = True

        return result

    def _load_keys_encrypted(self) -> Dict[str, str]:
        """Load encrypted keys from file."""
        if not self.keys_file.exists():
            return {}

        try:
            with open(self.keys_file) as f:
                data = yaml.safe_load(f)
                return data.get("keys", {}) if data else {}
        except Exception:
            return {}

    def _save_keys_encrypted(self, keys: Dict[str, str]):
        """Save encrypted keys to file."""
        data = {"keys": keys}
        with open(self.keys_file, "w") as f:
            yaml.safe_dump(data, f)


# Global instance
_key_manager = None


def get_key_manager() -> APIKeyManager:
    """Get global API key manager instance."""
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager()
    return _key_manager
