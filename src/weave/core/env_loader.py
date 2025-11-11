"""Simple .env file loader for Weave."""

import os
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Optional[Path] = None) -> None:
    """
    Load environment variables from a .env file.

    Searches for .env file in this order:
    1. Provided env_path
    2. .agent/.env in current directory
    3. .env in current directory

    Args:
        env_path: Optional path to .env file
    """
    if env_path and env_path.exists():
        _parse_env_file(env_path)
        return

    # Try .agent/.env first
    agent_env = Path.cwd() / ".agent" / ".env"
    if agent_env.exists():
        _parse_env_file(agent_env)
        return

    # Fall back to .env in current directory
    root_env = Path.cwd() / ".env"
    if root_env.exists():
        _parse_env_file(root_env)


def _parse_env_file(path: Path) -> None:
    """
    Parse .env file and set environment variables.

    Supports:
    - KEY=value
    - KEY="value"
    - KEY='value'
    - Comments starting with #
    - Empty lines

    Args:
        path: Path to .env file
    """
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            # Set environment variable (don't override existing ones)
            if key and not os.getenv(key):
                os.environ[key] = value
