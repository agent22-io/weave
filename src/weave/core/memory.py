"""Memory management for agents - short-term and long-term memory.

This module provides:
- Short-term memory: Buffer and sliding window strategies for conversation management
- Long-term memory: Simple markdown-based persistent storage for important facts
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from weave.core.sessions import ConversationMessage, ConversationSession


@dataclass
class Memory:
    """A single memory entry for long-term storage."""

    content: str
    timestamp: float = field(default_factory=time.time)
    importance: int = 5  # 1-10, higher is more important
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert memory to markdown format."""
        lines = [
            f"**{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}** (Importance: {self.importance})",
            "",
            self.content,
        ]

        if self.tags:
            lines.extend(["", f"*Tags: {', '.join(self.tags)}*"])

        if self.metadata:
            lines.extend(["", "---", "Metadata:"])
            for key, value in self.metadata.items():
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)


class ShortTermMemory:
    """Manages short-term memory (conversation context) with different strategies."""

    def __init__(self, strategy: str = "buffer", max_messages: int = 100):
        """Initialize short-term memory.

        Args:
            strategy: Memory strategy ("buffer" or "sliding_window")
            max_messages: Maximum messages to keep
        """
        self.strategy = strategy
        self.max_messages = max_messages

    def apply_strategy(self, messages: List[ConversationMessage]) -> List[ConversationMessage]:
        """Apply memory strategy to message list.

        Args:
            messages: Full message list

        Returns:
            Filtered message list according to strategy
        """
        if self.strategy == "buffer":
            return self._apply_buffer(messages)
        elif self.strategy == "sliding_window":
            return self._apply_sliding_window(messages)
        else:
            # Default to buffer
            return self._apply_buffer(messages)

    def _apply_buffer(self, messages: List[ConversationMessage]) -> List[ConversationMessage]:
        """Buffer strategy: Keep system message + last N messages.

        Args:
            messages: Full message list

        Returns:
            System message + last N messages
        """
        if len(messages) <= self.max_messages:
            return messages

        # Keep system messages
        system_messages = [msg for msg in messages if msg.role == "system"]

        # Get recent messages
        other_messages = [msg for msg in messages if msg.role != "system"]
        recent_messages = other_messages[-(self.max_messages - len(system_messages)) :]

        return system_messages + recent_messages

    def _apply_sliding_window(self, messages: List[ConversationMessage]) -> List[ConversationMessage]:
        """Sliding window strategy: Keep last N messages only.

        Args:
            messages: Full message list

        Returns:
            Last N messages
        """
        if len(messages) <= self.max_messages:
            return messages

        return messages[-self.max_messages :]


class LongTermMemory:
    """Manages long-term memory using simple markdown files."""

    def __init__(self, memory_dir: Optional[Path] = None):
        """Initialize long-term memory.

        Args:
            memory_dir: Directory to store memory files (default: .weave/memory)
        """
        self.memory_dir = memory_dir or Path(".weave") / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Secure the memory directory
        os.chmod(self.memory_dir, 0o700)

    def save_memory(self, agent_name: str, memory: Memory) -> None:
        """Save a memory to the agent's memory file.

        Args:
            agent_name: Name of the agent
            memory: Memory to save
        """
        memory_file = self.memory_dir / f"{agent_name}_memory.md"

        # Append to existing file or create new
        mode = "a" if memory_file.exists() else "w"

        with open(memory_file, mode) as f:
            if mode == "a":
                f.write("\n\n---\n\n")
            else:
                f.write(f"# Long-Term Memory: {agent_name}\n\n")

            f.write(memory.to_markdown())

        # Secure the memory file
        os.chmod(memory_file, 0o600)

    def load_memories(self, agent_name: str) -> Optional[str]:
        """Load all memories for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Memory content as markdown string, or None if no memories exist
        """
        memory_file = self.memory_dir / f"{agent_name}_memory.md"

        if not memory_file.exists():
            return None

        try:
            with open(memory_file) as f:
                return f.read()
        except Exception:
            return None

    def clear_memories(self, agent_name: str) -> bool:
        """Clear all memories for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            True if cleared, False if no memories existed
        """
        memory_file = self.memory_dir / f"{agent_name}_memory.md"

        if memory_file.exists():
            memory_file.unlink()
            return True

        return False

    def list_agents_with_memory(self) -> List[str]:
        """List all agents that have long-term memory.

        Returns:
            List of agent names
        """
        agents = []

        for memory_file in self.memory_dir.glob("*_memory.md"):
            agent_name = memory_file.stem.replace("_memory", "")
            agents.append(agent_name)

        return sorted(agents)


class MemoryManager:
    """Unified memory manager combining short-term and long-term memory."""

    def __init__(
        self,
        agent_name: str,
        strategy: str = "buffer",
        max_messages: int = 100,
        persist: bool = False,
        memory_dir: Optional[Path] = None,
    ):
        """Initialize memory manager.

        Args:
            agent_name: Name of the agent
            strategy: Short-term memory strategy
            max_messages: Maximum messages to keep in short-term memory
            persist: Whether to enable long-term memory persistence
            memory_dir: Directory for long-term memory storage
        """
        self.agent_name = agent_name
        self.short_term = ShortTermMemory(strategy=strategy, max_messages=max_messages)
        self.long_term = LongTermMemory(memory_dir=memory_dir) if persist else None
        self.persist = persist

    def apply_short_term_strategy(
        self, session: ConversationSession
    ) -> List[ConversationMessage]:
        """Apply short-term memory strategy to a session.

        Args:
            session: Conversation session

        Returns:
            Filtered messages according to strategy
        """
        return self.short_term.apply_strategy(session.messages)

    def save_long_term_memory(self, content: str, importance: int = 5, tags: Optional[List[str]] = None) -> None:
        """Save a memory to long-term storage.

        Args:
            content: Memory content
            importance: Importance level (1-10)
            tags: Optional tags for categorization
        """
        if not self.persist or not self.long_term:
            return

        memory = Memory(content=content, importance=importance, tags=tags or [])
        self.long_term.save_memory(self.agent_name, memory)

    def get_long_term_context(self) -> Optional[str]:
        """Get long-term memory context for the agent.

        Returns:
            Memory content as string, or None if no memories exist
        """
        if not self.persist or not self.long_term:
            return None

        return self.long_term.load_memories(self.agent_name)

    def clear_long_term_memory(self) -> bool:
        """Clear all long-term memories for this agent.

        Returns:
            True if cleared, False if no memories existed
        """
        if not self.persist or not self.long_term:
            return False

        return self.long_term.clear_memories(self.agent_name)


# Global instances
_long_term_memory = None


def get_long_term_memory() -> LongTermMemory:
    """Get global long-term memory instance."""
    global _long_term_memory
    if _long_term_memory is None:
        _long_term_memory = LongTermMemory()
    return _long_term_memory
