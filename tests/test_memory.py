"""Tests for memory management functionality."""

import pytest
import time
from pathlib import Path
from weave.core.memory import (
    Memory,
    ShortTermMemory,
    LongTermMemory,
    MemoryManager,
    estimate_tokens,
    count_message_tokens,
)
from weave.core.sessions import ConversationSession, ConversationMessage


class TestMemory:
    """Test Memory data class."""

    def test_memory_creation(self):
        """Memory should be created with content and metadata."""
        memory = Memory(
            content="Important fact about user preferences",
            importance=8,
            tags=["user", "preferences"],
        )

        assert memory.content == "Important fact about user preferences"
        assert memory.importance == 8
        assert "user" in memory.tags
        assert "preferences" in memory.tags

    def test_memory_to_markdown(self):
        """Memory should convert to markdown format."""
        memory = Memory(
            content="Test memory content",
            importance=5,
            tags=["test"],
        )

        markdown = memory.to_markdown()

        assert "Test memory content" in markdown
        assert "Importance: 5" in markdown
        assert "Tags: test" in markdown


class TestShortTermMemory:
    """Test short-term memory strategies."""

    def test_buffer_strategy_with_few_messages(self):
        """Buffer strategy should keep all messages when under limit."""
        stm = ShortTermMemory(strategy="buffer", max_messages=10)

        messages = [
            ConversationMessage(role="system", content="System prompt"),
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="assistant", content="Hi there"),
        ]

        filtered = stm.apply_strategy(messages)

        assert len(filtered) == 3
        assert filtered[0].role == "system"
        assert filtered[1].role == "user"
        assert filtered[2].role == "assistant"

    def test_buffer_strategy_keeps_system_message(self):
        """Buffer strategy should always keep system messages."""
        stm = ShortTermMemory(strategy="buffer", max_messages=5)

        # Create 10 messages including system
        messages = [ConversationMessage(role="system", content="System prompt")]
        for i in range(10):
            messages.append(ConversationMessage(role="user", content=f"Message {i}"))

        filtered = stm.apply_strategy(messages)

        # Should keep system + last 4 user messages
        assert len(filtered) == 5
        assert filtered[0].role == "system"
        assert filtered[0].content == "System prompt"

    def test_sliding_window_strategy(self):
        """Sliding window should keep only last N messages."""
        stm = ShortTermMemory(strategy="sliding_window", max_messages=3)

        messages = [
            ConversationMessage(role="system", content="System"),
            ConversationMessage(role="user", content="Message 1"),
            ConversationMessage(role="assistant", content="Response 1"),
            ConversationMessage(role="user", content="Message 2"),
            ConversationMessage(role="assistant", content="Response 2"),
        ]

        filtered = stm.apply_strategy(messages)

        # Should keep only last 3 messages
        assert len(filtered) == 3
        assert filtered[0].content == "Response 1"
        assert filtered[1].content == "Message 2"
        assert filtered[2].content == "Response 2"

    def test_default_strategy_is_buffer(self):
        """Unknown strategy should default to buffer."""
        stm = ShortTermMemory(strategy="unknown", max_messages=5)

        messages = [ConversationMessage(role="user", content=f"Msg {i}") for i in range(10)]

        filtered = stm.apply_strategy(messages)

        # Should use buffer strategy
        assert len(filtered) == 5


class TestLongTermMemory:
    """Test long-term memory storage."""

    def test_save_and_load_memory(self, tmp_path):
        """Memory should be saved and loaded from markdown files."""
        ltm = LongTermMemory(memory_dir=tmp_path)

        memory = Memory(
            content="User prefers dark mode",
            importance=7,
            tags=["preferences", "ui"],
        )

        ltm.save_memory("test_agent", memory)

        # Check file exists
        memory_file = tmp_path / "test_agent_memory.md"
        assert memory_file.exists()

        # Load memories
        loaded = ltm.load_memories("test_agent")
        assert loaded is not None
        assert "User prefers dark mode" in loaded
        assert "Importance: 7" in loaded

    def test_multiple_memories_appended(self, tmp_path):
        """Multiple memories should be appended to the same file."""
        ltm = LongTermMemory(memory_dir=tmp_path)

        memory1 = Memory(content="First memory", importance=5)
        memory2 = Memory(content="Second memory", importance=6)

        ltm.save_memory("test_agent", memory1)
        ltm.save_memory("test_agent", memory2)

        loaded = ltm.load_memories("test_agent")

        assert "First memory" in loaded
        assert "Second memory" in loaded

    def test_clear_memories(self, tmp_path):
        """Clearing memories should delete the memory file."""
        ltm = LongTermMemory(memory_dir=tmp_path)

        memory = Memory(content="Test memory", importance=5)
        ltm.save_memory("test_agent", memory)

        # Clear memories
        result = ltm.clear_memories("test_agent")

        assert result is True
        assert ltm.load_memories("test_agent") is None

    def test_clear_nonexistent_memories(self, tmp_path):
        """Clearing non-existent memories should return False."""
        ltm = LongTermMemory(memory_dir=tmp_path)

        result = ltm.clear_memories("nonexistent_agent")

        assert result is False

    def test_list_agents_with_memory(self, tmp_path):
        """Should list all agents that have memory."""
        ltm = LongTermMemory(memory_dir=tmp_path)

        memory = Memory(content="Test", importance=5)
        ltm.save_memory("agent1", memory)
        ltm.save_memory("agent2", memory)

        agents = ltm.list_agents_with_memory()

        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents


class TestMemoryManager:
    """Test unified memory manager."""

    def test_memory_manager_without_persistence(self):
        """Memory manager should work without long-term persistence."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=10,
            persist=False,
        )

        # Long-term memory should be None
        assert manager.long_term is None
        assert manager.persist is False

    def test_memory_manager_with_persistence(self, tmp_path):
        """Memory manager should support long-term persistence."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=10,
            persist=True,
            memory_dir=tmp_path,
        )

        # Long-term memory should exist
        assert manager.long_term is not None
        assert manager.persist is True

    def test_apply_short_term_strategy(self):
        """Memory manager should apply short-term strategy to sessions."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="sliding_window",
            max_messages=3,
            persist=False,
        )

        session = ConversationSession(session_id="test")
        for i in range(5):
            session.add_message("user", f"Message {i}")

        filtered = manager.apply_short_term_strategy(session)

        assert len(filtered) == 3
        assert filtered[0].content == "Message 2"

    def test_save_long_term_memory(self, tmp_path):
        """Memory manager should save to long-term storage."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=10,
            persist=True,
            memory_dir=tmp_path,
        )

        manager.save_long_term_memory(
            content="Important fact",
            importance=8,
            tags=["important"],
        )

        context = manager.get_long_term_context()

        assert context is not None
        assert "Important fact" in context

    def test_get_long_term_context_without_persistence(self):
        """Getting long-term context without persistence should return None."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=10,
            persist=False,
        )

        context = manager.get_long_term_context()

        assert context is None

    def test_clear_long_term_memory(self, tmp_path):
        """Memory manager should clear long-term memory."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=10,
            persist=True,
            memory_dir=tmp_path,
        )

        manager.save_long_term_memory("Test memory", importance=5)

        result = manager.clear_long_term_memory()

        assert result is True
        assert manager.get_long_term_context() is None


class TestMemoryIntegration:
    """Integration tests for memory system."""

    def test_conversation_with_memory_management(self, tmp_path):
        """Full conversation with memory management."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=5,
            persist=True,
            memory_dir=tmp_path,
        )

        # Simulate a conversation
        session = ConversationSession(session_id="test_session")
        session.add_message("system", "You are a helpful assistant")

        for i in range(10):
            session.add_message("user", f"Question {i}")
            session.add_message("assistant", f"Answer {i}")

        # Apply short-term strategy
        filtered = manager.apply_short_term_strategy(session)

        # Should have limited messages
        assert len(filtered) <= 5

        # Save important fact to long-term memory
        manager.save_long_term_memory(
            content="User is interested in Python programming",
            importance=8,
            tags=["interests", "python"],
        )

        # Retrieve long-term context
        context = manager.get_long_term_context()
        assert "Python programming" in context


class TestTokenCounting:
    """Test token counting utilities."""

    def test_estimate_tokens_empty_string(self):
        """Empty string should have 0 tokens."""
        assert estimate_tokens("") == 0
        assert estimate_tokens(None) == 0

    def test_estimate_tokens_short_text(self):
        """Short text should estimate tokens correctly."""
        text = "Hello world"  # 11 chars
        tokens = estimate_tokens(text)
        assert tokens == 2  # 11 // 4 = 2

    def test_estimate_tokens_longer_text(self):
        """Longer text should estimate tokens correctly."""
        text = "This is a longer piece of text that should have more tokens"  # 60 chars
        tokens = estimate_tokens(text)
        assert tokens == 15  # 60 // 4 = 15

    def test_count_message_tokens(self):
        """Should count tokens across multiple messages."""
        messages = [
            ConversationMessage(role="user", content="Hello"),  # 5 chars = 1 token
            ConversationMessage(role="assistant", content="Hi there"),  # 8 chars = 2 tokens
            ConversationMessage(role="user", content="How are you?"),  # 12 chars = 3 tokens
        ]

        total_tokens = count_message_tokens(messages)
        assert total_tokens == 6  # 1 + 2 + 3


class TestAutoCompact:
    """Test auto-compact functionality."""

    def test_should_not_compact_with_few_messages(self):
        """Should not compact when messages are below threshold."""
        stm = ShortTermMemory(
            strategy="buffer",
            max_messages=100,
            context_window=1000,
            summarize_after=None,
        )

        messages = [
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="assistant", content="Hi"),
        ]

        # Should not compact
        assert not stm._should_compact(messages)

    def test_should_compact_when_exceeds_token_limit(self):
        """Should compact when token count exceeds context_window."""
        stm = ShortTermMemory(
            strategy="buffer",
            max_messages=100,
            context_window=50,  # Very low limit
            summarize_after=None,
        )

        # Create messages that exceed token limit
        messages = [
            ConversationMessage(
                role="user",
                content="This is a very long message " * 10,  # ~280 chars = ~70 tokens
            )
        ]

        # Should trigger compaction
        assert stm._should_compact(messages)

    def test_should_compact_when_exceeds_message_count(self):
        """Should compact when message count exceeds summarize_after."""
        stm = ShortTermMemory(
            strategy="buffer",
            max_messages=100,
            context_window=10000,  # High token limit
            summarize_after=5,  # Low message limit
        )

        # Create 10 short messages
        messages = [
            ConversationMessage(role="user", content=f"Message {i}") for i in range(10)
        ]

        # Should trigger compaction due to message count
        assert stm._should_compact(messages)

    def test_compact_messages_creates_summary(self):
        """Compacting should create a summary message."""
        stm = ShortTermMemory(
            strategy="buffer",
            max_messages=100,
            context_window=100,  # Low limit to trigger compaction
        )

        # Create many messages
        messages = [ConversationMessage(role="system", content="System prompt")]
        for i in range(20):
            messages.append(
                ConversationMessage(
                    role="user", content=f"This is a longer message number {i} with some content"
                )
            )
            messages.append(ConversationMessage(role="assistant", content=f"Response {i}"))

        # Compact messages
        compacted = stm._compact_messages(messages)

        # Should have: system messages + summary + last 10 conversation messages
        # System (1) + summary (1) + last 10 conversation messages (10) = 12
        assert len(compacted) <= 20  # Should be less than original
        assert any("Conversation Summary" in msg.content for msg in compacted)

    def test_auto_compact_integration(self):
        """Test auto-compact in apply_strategy."""
        stm = ShortTermMemory(
            strategy="buffer",
            max_messages=100,
            context_window=50,  # Very low limit
            summarize_after=None,
        )

        # Create messages exceeding token limit
        messages = [ConversationMessage(role="system", content="System prompt")]
        for i in range(15):
            messages.append(
                ConversationMessage(
                    role="user", content=f"This is a longer message {i} with content " * 3
                )
            )

        # Apply strategy with auto_compact
        filtered = stm.apply_strategy(messages, auto_compact=True)

        # Should have been compacted
        assert len(filtered) < len(messages)

    def test_auto_compact_disabled(self):
        """Auto-compact can be disabled."""
        stm = ShortTermMemory(
            strategy="buffer",
            max_messages=100,
            context_window=50,  # Very low limit
            summarize_after=None,
        )

        # Create messages exceeding token limit
        messages = [
            ConversationMessage(
                role="user",
                content="This is a very long message " * 10,  # Exceeds limit
            )
        ]

        # Apply strategy with auto_compact disabled
        filtered = stm.apply_strategy(messages, auto_compact=False)

        # Should not have been compacted
        assert len(filtered) == len(messages)

    def test_memory_manager_with_auto_compact_config(self, tmp_path):
        """Memory manager should use context_window and summarize_after."""
        manager = MemoryManager(
            agent_name="test_agent",
            strategy="buffer",
            max_messages=100,
            context_window=1000,
            summarize_after=20,
            persist=False,
        )

        # Check that parameters were passed to ShortTermMemory
        assert manager.short_term.context_window == 1000
        assert manager.short_term.summarize_after == 20
