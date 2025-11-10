# Memory Management Example

This example demonstrates how to configure and use short-term and long-term memory for agents in Weave.

## Overview

Agents can maintain two types of memory:

1. **Short-Term Memory**: Manages conversation context during execution
2. **Long-Term Memory**: Persists important facts across sessions

## Memory Strategies

### Buffer Strategy
Keeps system messages + recent N messages. Best for maintaining important context while limiting token usage.

```yaml
memory:
  type: "buffer"
  max_messages: 20
```

### Sliding Window Strategy
Keeps only the last N messages. Best for tasks that only need recent context.

```yaml
memory:
  type: "sliding_window"
  max_messages: 10
```

## Long-Term Memory

Enable persistence to save important information across sessions:

```yaml
memory:
  type: "buffer"
  max_messages: 50
  persist: true  # Saves to .weave/memory/agent_name_memory.md
```

## Memory as a Resource

Long-term memories are stored in `.weave/memory/` as markdown files:

```
.weave/
  memory/
    agent1_memory.md
    agent2_memory.md
```

These files can be:
- Read by agents using built-in file tools
- Edited manually to add/update information
- Version controlled with your project
- Shared across sessions

## Memory File Format

Long-term memory is stored in markdown with this structure:

```markdown
# Long-Term Memory: agent_name

**2025-01-15 10:30:45** (Importance: 8)

Memory content here.

*Tags: tag1, tag2*

---
Metadata:
- key: value
---

**2025-01-15 11:15:22** (Importance: 9)

Another memory entry.

*Tags: important*
```

## Using This Example

1. Run the workflow:
   ```bash
   weave run memory_example.weave.yaml
   ```

2. Check the memory files:
   ```bash
   ls -la .weave/memory/
   cat .weave/memory/knowledge_keeper_memory.md
   ```

3. Long-term memory is automatically injected into agent prompts

## Memory Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | "buffer" | Memory strategy: "buffer", "sliding_window", or "auto_compact" |
| `max_messages` | int | 100 | Maximum messages to keep in short-term memory |
| `persist` | bool | false | Whether to save long-term memory |
| `context_window` | int | 4000 | Context window size in tokens - triggers auto-compact when exceeded |
| `summarize_after` | int | null | Auto-compact after N messages (null = use context_window) |

## Auto-Compact Feature

Auto-compact automatically manages conversation context by summarizing old messages when limits are exceeded. This prevents token limits from being reached while preserving conversation history.

### How Auto-Compact Works

1. **Token Counting**: Tracks approximate token usage in conversation history
2. **Threshold Detection**: Triggers when either:
   - Total tokens exceed `context_window`, OR
   - Message count exceeds `summarize_after` (if set)
3. **Smart Summarization**:
   - Keeps all system messages (important instructions)
   - Keeps last 10 conversation messages (recent context)
   - Summarizes older messages into a concise summary
   - Injects summary as a system message

### Example Configuration

```yaml
memory:
  type: "buffer"
  max_messages: 100
  context_window: 4000      # Trigger when tokens exceed 4000
  summarize_after: 50       # Also trigger after 50 messages
  persist: true
```

### When to Use Auto-Compact

- **Long conversations**: Maintain context without hitting token limits
- **Streaming applications**: Keep memory footprint manageable
- **Cost optimization**: Reduce token usage by compacting history
- **Multi-turn interactions**: Preserve important context over many exchanges

## Best Practices

1. **Use buffer strategy** for agents that need to remember system instructions
2. **Use sliding window** for stateless processing tasks
3. **Enable persistence** for agents that should learn from conversations
4. **Configure auto-compact** with `context_window` for long conversations
5. **Set appropriate max_messages** based on your model's context window
6. **Use summarize_after** for predictable compaction at message thresholds
7. **Tag memories** for better organization and retrieval

## How It Works

1. **During Execution**:
   - Short-term memory limits messages sent to the LLM
   - System messages are preserved in buffer strategy
   - Long-term memory is injected into system prompt

2. **After Execution**:
   - Session history is saved if session_id is provided
   - Long-term memories are appended to markdown files
   - Memory files are available as resources

3. **Next Session**:
   - Long-term memory is loaded from `.weave/memory/`
   - Agent can access past important information
   - New memories are appended to existing ones
