"""Storage backend for Weave state management."""

import json
import yaml
import pickle
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum


class StorageFormat(str, Enum):
    """Storage format options."""

    JSON = "json"
    YAML = "yaml"
    PICKLE = "pickle"


class StorageBackend:
    """Backend for storing and retrieving data."""

    def __init__(self, base_path: str = ".agent/storage", format: str = "json"):
        """Initialize storage backend.

        Args:
            base_path: Base directory for storage
            format: Storage format (json, yaml, pickle)
        """
        self.base_path = Path(base_path)
        self.format = StorageFormat(format)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: Any, subdir: Optional[str] = None) -> Path:
        """Save data to storage.

        Args:
            key: Storage key (filename without extension)
            data: Data to save
            subdir: Optional subdirectory

        Returns:
            Path to saved file
        """
        # Create path
        if subdir:
            path = self.base_path / subdir
            path.mkdir(parents=True, exist_ok=True)
        else:
            path = self.base_path

        # Determine filename
        ext = f".{self.format.value}"
        filepath = path / f"{key}{ext}"

        # Save based on format
        if self.format == StorageFormat.JSON:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)
        elif self.format == StorageFormat.YAML:
            with open(filepath, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        elif self.format == StorageFormat.PICKLE:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)

        return filepath

    def load(self, key: str, subdir: Optional[str] = None) -> Optional[Any]:
        """Load data from storage.

        Args:
            key: Storage key
            subdir: Optional subdirectory

        Returns:
            Loaded data or None if not found
        """
        # Create path
        if subdir:
            path = self.base_path / subdir
        else:
            path = self.base_path

        # Try each format
        for fmt in StorageFormat:
            ext = f".{fmt.value}"
            filepath = path / f"{key}{ext}"

            if filepath.exists():
                try:
                    if fmt == StorageFormat.JSON:
                        with open(filepath, "r") as f:
                            return json.load(f)
                    elif fmt == StorageFormat.YAML:
                        with open(filepath, "r") as f:
                            return yaml.safe_load(f)
                    elif fmt == StorageFormat.PICKLE:
                        with open(filepath, "rb") as f:
                            return pickle.load(f)
                except Exception:
                    continue

        return None

    def delete(self, key: str, subdir: Optional[str] = None) -> bool:
        """Delete data from storage.

        Args:
            key: Storage key
            subdir: Optional subdirectory

        Returns:
            True if deleted, False if not found
        """
        if subdir:
            path = self.base_path / subdir
        else:
            path = self.base_path

        deleted = False
        for fmt in StorageFormat:
            ext = f".{fmt.value}"
            filepath = path / f"{key}{ext}"
            if filepath.exists():
                filepath.unlink()
                deleted = True

        return deleted

    def list_keys(self, subdir: Optional[str] = None, pattern: str = "*") -> list[str]:
        """List all keys in storage.

        Args:
            subdir: Optional subdirectory
            pattern: Glob pattern for filtering

        Returns:
            List of storage keys (without extensions)
        """
        if subdir:
            path = self.base_path / subdir
        else:
            path = self.base_path

        if not path.exists():
            return []

        keys = set()
        for fmt in StorageFormat:
            ext = f".{fmt.value}"
            for filepath in path.glob(f"{pattern}{ext}"):
                keys.add(filepath.stem)

        return sorted(keys)

    def cleanup_old(self, retention_days: int, subdir: Optional[str] = None) -> int:
        """Clean up old files based on retention period.

        Args:
            retention_days: Number of days to retain files
            subdir: Optional subdirectory

        Returns:
            Number of files deleted
        """
        if subdir:
            path = self.base_path / subdir
        else:
            path = self.base_path

        if not path.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        for filepath in path.rglob("*"):
            if filepath.is_file():
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if mtime < cutoff_time:
                    filepath.unlink()
                    deleted_count += 1

        return deleted_count


class Storage:
    """High-level storage interface."""

    def __init__(self, base_path: str = ".agent/storage", format: str = "json"):
        """Initialize storage.

        Args:
            base_path: Base directory for storage
            format: Storage format
        """
        self.backend = StorageBackend(base_path, format)

    def save_agent_output(
        self, agent_name: str, output: Any, run_id: Optional[str] = None
    ) -> Path:
        """Save agent output.

        Args:
            agent_name: Name of the agent
            output: Output data
            run_id: Optional run ID

        Returns:
            Path to saved file
        """
        if run_id:
            key = f"{agent_name}_{run_id}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f"{agent_name}_{timestamp}"

        return self.backend.save(key, output, subdir="outputs")

    def save_agent_memory(
        self, agent_name: str, memory: Any, storage_key: Optional[str] = None
    ) -> Path:
        """Save agent memory.

        Args:
            agent_name: Name of the agent
            memory: Memory data
            storage_key: Optional custom storage key

        Returns:
            Path to saved file
        """
        key = storage_key or f"{agent_name}_memory"
        return self.backend.save(key, memory, subdir="memory")

    def load_agent_memory(
        self, agent_name: str, storage_key: Optional[str] = None
    ) -> Optional[Any]:
        """Load agent memory.

        Args:
            agent_name: Name of the agent
            storage_key: Optional custom storage key

        Returns:
            Loaded memory or None
        """
        key = storage_key or f"{agent_name}_memory"
        return self.backend.load(key, subdir="memory")

    def save_execution_log(self, run_id: str, log_data: Any) -> Path:
        """Save execution log.

        Args:
            run_id: Execution run ID
            log_data: Log data

        Returns:
            Path to saved file
        """
        return self.backend.save(run_id, log_data, subdir="logs")

    def list_agent_outputs(self, agent_name: Optional[str] = None) -> list[str]:
        """List agent outputs.

        Args:
            agent_name: Optional agent name filter

        Returns:
            List of output keys
        """
        if agent_name:
            pattern = f"{agent_name}_*"
        else:
            pattern = "*"

        return self.backend.list_keys(subdir="outputs", pattern=pattern)

    def cleanup_old_data(self, retention_days: int) -> Dict[str, int]:
        """Clean up old data.

        Args:
            retention_days: Number of days to retain

        Returns:
            Dictionary with cleanup counts by subdirectory
        """
        return {
            "outputs": self.backend.cleanup_old(retention_days, subdir="outputs"),
            "memory": self.backend.cleanup_old(retention_days, subdir="memory"),
            "logs": self.backend.cleanup_old(retention_days, subdir="logs"),
        }
