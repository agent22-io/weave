"""State and lock file management for Weave."""

import os
import time
import yaml
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentExecutionRecord(BaseModel):
    """Record of a single agent execution."""

    agent_name: str
    status: str  # pending, running, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    outputs: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0


class ExecutionState(BaseModel):
    """State of a weave execution."""

    weave_name: str
    run_id: str
    status: str  # pending, running, completed, failed, cancelled
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    agents: Dict[str, AgentExecutionRecord] = Field(default_factory=dict)
    total_agents: int = 0
    completed_agents: int = 0
    failed_agents: int = 0
    config_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LockFile(BaseModel):
    """Lock file for preventing concurrent executions."""

    weave_name: str
    run_id: str
    pid: int
    hostname: str
    locked_at: float
    locked_by: str  # User or process info
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StateManager:
    """Manages execution state and lock files."""

    def __init__(
        self,
        state_file: str = ".agent/state.yaml",
        lock_file: str = ".agent/weave.lock",
    ):
        """Initialize state manager.

        Args:
            state_file: Path to state file
            lock_file: Path to lock file
        """
        self.state_file = Path(state_file)
        self.lock_file = Path(lock_file)

        # Ensure directories exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)

    def create_run_id(self) -> str:
        """Create a unique run ID.

        Returns:
            Run ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run_{timestamp}_{os.getpid()}"

    def save_state(self, state: ExecutionState) -> None:
        """Save execution state to file.

        Args:
            state: Execution state to save
        """
        # Load existing states
        states = self.load_all_states()

        # Update or add current state
        states[state.run_id] = state.dict()

        # Save to file
        with open(self.state_file, "w") as f:
            yaml.dump(states, f, default_flow_style=False)

    def load_state(self, run_id: str) -> Optional[ExecutionState]:
        """Load execution state by run ID.

        Args:
            run_id: Run ID to load

        Returns:
            ExecutionState or None if not found
        """
        states = self.load_all_states()
        if run_id in states:
            return ExecutionState(**states[run_id])
        return None

    def load_all_states(self) -> Dict[str, Any]:
        """Load all execution states.

        Returns:
            Dictionary of all states
        """
        if not self.state_file.exists():
            return {}

        with open(self.state_file, "r") as f:
            data = yaml.safe_load(f) or {}
            return data

    def get_latest_state(
        self, weave_name: Optional[str] = None
    ) -> Optional[ExecutionState]:
        """Get the most recent execution state.

        Args:
            weave_name: Optional filter by weave name

        Returns:
            Latest ExecutionState or None
        """
        states = self.load_all_states()
        if not states:
            return None

        # Filter by weave name if specified
        if weave_name:
            states = {
                k: v for k, v in states.items() if v.get("weave_name") == weave_name
            }

        if not states:
            return None

        # Get most recent
        latest_key = max(states.keys(), key=lambda k: states[k].get("start_time", 0))
        return ExecutionState(**states[latest_key])

    def create_lock(
        self, weave_name: str, run_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> LockFile:
        """Create a lock file.

        Args:
            weave_name: Name of the weave
            run_id: Execution run ID
            metadata: Optional metadata

        Returns:
            LockFile object

        Raises:
            RuntimeError: If lock already exists
        """
        if self.is_locked():
            raise RuntimeError(
                f"Weave is already locked. Remove {self.lock_file} or wait for execution to complete."
            )

        import socket

        lock = LockFile(
            weave_name=weave_name,
            run_id=run_id,
            pid=os.getpid(),
            hostname=socket.gethostname(),
            locked_at=time.time(),
            locked_by=os.getenv("USER", "unknown"),
            metadata=metadata or {},
        )

        # Save lock file
        with open(self.lock_file, "w") as f:
            json.dump(lock.dict(), f, indent=2)

        return lock

    def release_lock(self) -> bool:
        """Release the lock file.

        Returns:
            True if lock was released, False if no lock existed
        """
        if self.lock_file.exists():
            self.lock_file.unlink()
            return True
        return False

    def is_locked(self) -> bool:
        """Check if a lock file exists.

        Returns:
            True if locked, False otherwise
        """
        if not self.lock_file.exists():
            return False

        # Check if lock is stale (process no longer exists)
        try:
            lock = self.read_lock()
            if lock:
                # Check if process still exists (Unix-like systems)
                try:
                    os.kill(lock.pid, 0)
                    return True
                except OSError:
                    # Process doesn't exist, lock is stale
                    self.release_lock()
                    return False
        except Exception:
            pass

        return True

    def read_lock(self) -> Optional[LockFile]:
        """Read the current lock file.

        Returns:
            LockFile or None if not locked
        """
        if not self.lock_file.exists():
            return None

        try:
            with open(self.lock_file, "r") as f:
                data = json.load(f)
                return LockFile(**data)
        except Exception:
            return None

    def cleanup_old_states(self, retention_days: int = 30) -> int:
        """Clean up old execution states.

        Args:
            retention_days: Number of days to retain states

        Returns:
            Number of states deleted
        """
        states = self.load_all_states()
        if not states:
            return 0

        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        new_states = {}
        deleted_count = 0

        for run_id, state_data in states.items():
            start_time = state_data.get("start_time", 0)
            if start_time >= cutoff_time:
                new_states[run_id] = state_data
            else:
                deleted_count += 1

        # Save updated states
        if deleted_count > 0:
            with open(self.state_file, "w") as f:
                yaml.dump(new_states, f, default_flow_style=False)

        return deleted_count

    def list_runs(
        self, weave_name: Optional[str] = None, status: Optional[str] = None
    ) -> List[ExecutionState]:
        """List all execution runs.

        Args:
            weave_name: Optional filter by weave name
            status: Optional filter by status

        Returns:
            List of ExecutionState objects
        """
        states = self.load_all_states()
        results = []

        for state_data in states.values():
            # Apply filters
            if weave_name and state_data.get("weave_name") != weave_name:
                continue
            if status and state_data.get("status") != status:
                continue

            results.append(ExecutionState(**state_data))

        # Sort by start time (most recent first)
        results.sort(key=lambda s: s.start_time, reverse=True)
        return results
