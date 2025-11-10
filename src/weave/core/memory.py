"""Memory management for agents - short-term and long-term memory.

This module provides:
- Short-term memory: Buffer and sliding window strategies for conversation management
- Long-term memory: Simple markdown-based persistent storage for important facts
- Auto-compact: Automatic summarization when context exceeds token limits
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from weave.core.sessions import ConversationMessage, ConversationSession


def estimate_tokens(text: str) -> int:
    """Estimate token count from text.

    Uses a simple heuristic: ~4 characters per token for English text.
    This is approximate but sufficient for memory management.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return len(text) // 4


def count_message_tokens(messages: List[ConversationMessage]) -> int:
    """Count total tokens in a list of messages.

    Args:
        messages: List of conversation messages

    Returns:
        Total estimated token count
    """
    return sum(estimate_tokens(msg.content) for msg in messages)


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

    def __init__(
        self,
        strategy: str = "buffer",
        max_messages: int = 100,
        context_window: int = 4000,
        summarize_after: Optional[int] = None,
    ):
        """Initialize short-term memory.

        Args:
            strategy: Memory strategy ("buffer", "sliding_window", or "auto_compact")
            max_messages: Maximum messages to keep
            context_window: Maximum tokens to keep in context
            summarize_after: Summarize after N messages (None = use context_window)
        """
        self.strategy = strategy
        self.max_messages = max_messages
        self.context_window = context_window
        self.summarize_after = summarize_after
        self.summary_message: Optional[ConversationMessage] = None

    def apply_strategy(
        self, messages: List[ConversationMessage], auto_compact: bool = True
    ) -> List[ConversationMessage]:
        """Apply memory strategy to message list.

        Args:
            messages: Full message list
            auto_compact: Whether to apply auto-compaction based on token limits

        Returns:
            Filtered message list according to strategy
        """
        # Check if auto-compact is needed
        if auto_compact and self._should_compact(messages):
            messages = self._compact_messages(messages)

        # Apply selected strategy
        if self.strategy == "buffer" or self.strategy == "auto_compact":
            return self._apply_buffer(messages)
        elif self.strategy == "sliding_window":
            return self._apply_sliding_window(messages)
        else:
            # Default to buffer
            return self._apply_buffer(messages)

    def _should_compact(self, messages: List[ConversationMessage]) -> bool:
        """Check if messages should be compacted.

        Args:
            messages: Message list to check

        Returns:
            True if compaction is needed
        """
        # Skip if we have a summary already or too few messages
        if self.summary_message or len(messages) < 5:
            return False

        # Check token count
        token_count = count_message_tokens(messages)
        if token_count > self.context_window:
            return True

        # Check message count if summarize_after is set
        if self.summarize_after and len(messages) > self.summarize_after:
            return True

        return False

    def _compact_messages(
        self, messages: List[ConversationMessage]
    ) -> List[ConversationMessage]:
        """Compact messages by summarizing old ones.

        Strategy:
        - Keep system messages
        - Keep last 10 messages (configurable)
        - Summarize the rest into a single message

        Args:
            messages: Full message list

        Returns:
            Compacted message list with summary
        """
        if len(messages) <= 10:
            return messages

        # Separate system messages and conversation messages
        system_messages = [msg for msg in messages if msg.role == "system"]
        conversation_messages = [msg for msg in messages if msg.role != "system"]

        # Keep last 10 conversation messages
        recent_messages = conversation_messages[-10:]
        old_messages = conversation_messages[:-10]

        if not old_messages:
            return messages

        # Create summary of old messages
        summary_parts = ["## Conversation Summary"]
        summary_parts.append(
            f"The following is a summary of {len(old_messages)} earlier messages:\n"
        )

        # Group by role and create concise summary
        for msg in old_messages[::2]:  # Sample every other message to keep summary short
            role = msg.role.title()
            content_preview = msg.content[:200] + (
                "..." if len(msg.content) > 200 else ""
            )
            summary_parts.append(f"- {role}: {content_preview}")

        summary_content = "\n".join(summary_parts)
        self.summary_message = ConversationMessage(
            role="system", content=summary_content, timestamp=time.time()
        )

        # Return: system messages + summary + recent messages
        return system_messages + [self.summary_message] + recent_messages

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
        context_window: int = 4000,
        summarize_after: Optional[int] = None,
        persist: bool = False,
        memory_dir: Optional[Path] = None,
    ):
        """Initialize memory manager.

        Args:
            agent_name: Name of the agent
            strategy: Short-term memory strategy
            max_messages: Maximum messages to keep in short-term memory
            context_window: Maximum tokens to keep in context
            summarize_after: Summarize after N messages (None = use context_window)
            persist: Whether to enable long-term memory persistence
            memory_dir: Directory for long-term memory storage
        """
        self.agent_name = agent_name
        self.short_term = ShortTermMemory(
            strategy=strategy,
            max_messages=max_messages,
            context_window=context_window,
            summarize_after=summarize_after,
        )
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
