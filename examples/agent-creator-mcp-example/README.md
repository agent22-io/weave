# Agent Creator MCP Example

An interactive agent creation system using a Model Context Protocol (MCP) server. This example demonstrates how to build a meta-agent that helps users create Weave agent configurations through a guided question-and-answer process.

## 🎯 What This Example Does

This example shows how to:
- Create a custom MCP server that provides interactive tools
- Build a meta-agent that uses MCP tools to help create other agents
- Guide users through agent configuration with structured questions
- Generate valid Weave YAML configurations programmatically
- Validate generated configurations

## 📂 Files

```
agent-creator-mcp-example/
├── README.md                  # This file
├── agent_creator_server.py    # MCP server implementation
├── .weave.yaml               # Weave configuration using the MCP server
├── mcp_config.json           # MCP server configuration
├── example_interaction.md     # Sample interaction walkthrough
└── example_output.yaml       # Example generated configuration
```

## 🚀 Quick Start

### 1. Set Up the MCP Server

First, ensure the MCP server script is executable:

```bash
chmod +x agent_creator_server.py
```

### 2. Configure MCP in Weave

Copy the MCP configuration to your Weave config directory:

```bash
# Create MCP config directory if it doesn't exist
mkdir -p ~/.weave

# Copy the MCP configuration
cp mcp_config.json ~/.weave/mcp_config.json
```

Or manually add to `~/.weave/mcp_config.json`:

```json
{
  "mcpServers": {
    "agent_creator_mcp": {
      "command": "python",
      "args": ["/full/path/to/agent_creator_server.py"],
      "description": "Interactive agent creation through guided questions"
    }
  }
}
```

**Important:** Use the full absolute path to `agent_creator_server.py` in the configuration.

### 3. Verify MCP Server

Check that Weave can see the MCP server:

```bash
weave mcp --list
```

You should see `agent_creator_mcp` listed.

To see available tools:

```bash
weave mcp --server-tools agent_creator_mcp
```

### 4. Run the Agent Creator

```bash
# Interactive mode (prompts will guide you)
weave apply --real

# Or use a specific weave
weave apply --weave interactive_agent_creation --real
```

## 🔧 How It Works

### The MCP Server

The `agent_creator_server.py` implements an MCP server with three main tools:

#### 1. `start_agent_creation`
Starts a new agent creation session with a unique ID.

**Input:**
```json
{
  "session_id": "my-session-123"
}
```

**Output:**
```json
{
  "status": "started",
  "message": "Agent creation session started!",
  "next_question": {
    "step": 0,
    "question": "What is the name of your agent?",
    "field": "agent_name",
    "hint": "Choose a descriptive name",
    "example": "content_researcher"
  }
}
```

#### 2. `answer_question`
Answers the current question in a session.

**Input:**
```json
{
  "session_id": "my-session-123",
  "answer": "content_researcher"
}
```

**Output:**
```json
{
  "status": "continue",
  "message": "Answer recorded",
  "next_question": { /* next question */ },
  "progress": "1/8 questions answered"
}
```

When all questions are answered:
```json
{
  "status": "complete",
  "message": "Agent configuration created successfully!",
  "agent_name": "content_researcher",
  "configuration": "version: \"1.0\"\n\nagents:\n  content_researcher:\n    ..."
}
```

#### 3. `get_session_status`
Gets the current status of a session.

**Input:**
```json
{
  "session_id": "my-session-123"
}
```

**Output:**
```json
{
  "status": "active",
  "session_id": "my-session-123",
  "progress": "3/8 questions answered",
  "current_question": { /* current question */ }
}
```

### The Questions

The MCP server asks 8 questions to build a complete agent configuration:

1. **Agent Name** - Identifier for the agent
2. **Description** - Purpose of the agent
3. **Model** - Which LLM to use (gpt-4, claude-3-opus, etc.)
4. **Tools** - Tools the agent can use
5. **Temperature** - Creativity level (0.0-1.0)
6. **Max Tokens** - Response length limit
7. **Inputs** - Dependencies on other agents (optional)
8. **Outputs** - Name for this agent's output

### The Weave Configuration

The `.weave.yaml` defines two agents:

1. **agent_designer** - Uses the MCP server tools to interactively create agent configs
2. **configuration_validator** - Validates the generated configuration

Two weaves are available:

1. **interactive_agent_creation** - Just the designer agent
2. **validated_agent_creation** - Designer + validator

## 📋 Example Interaction

Here's what a typical session looks like:

```
User: I want to create a new agent for summarizing research papers

Agent Designer: I'll help you create that agent! Let me start a session.

[Calls: start_agent_creation(session_id="session-001")]

Question 1/8: What is the name of your agent?
Hint: Choose a descriptive name (e.g., 'researcher', 'writer', 'analyzer')

User: research_summarizer

[Calls: answer_question(session_id="session-001", answer="research_summarizer")]

Question 2/8: What is the purpose of this agent?
Hint: Describe what this agent does in 1-2 sentences

User: Reads research papers and creates concise summaries highlighting key findings and methodology

[Calls: answer_question(session_id="session-001", answer="...")]

Question 3/8: Which LLM model should this agent use?
Hint: Choose from: gpt-4, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet, claude-3-haiku

User: claude-3-sonnet

... (continues through all 8 questions) ...

Agent Designer: Perfect! Here's your agent configuration:

version: "1.0"

agents:
  research_summarizer:
    # Reads research papers and creates concise summaries
    model: "claude-3-sonnet"
    tools: [text_length, json_validator]
    outputs: "research_summary"
    config:
      temperature: 0.3
      max_tokens: 2000
```

See [example_interaction.md](example_interaction.md) for a complete walkthrough.

## 🎨 Customization

### Adding New Questions

Edit `agent_creator_server.py` and add questions to the `get_next_question()` method:

```python
{
    "step": 8,
    "question": "Should this agent use streaming?",
    "field": "streaming",
    "hint": "Enable streaming for real-time responses",
    "example": "true"
}
```

### Supporting More Models

Update the `valid_models` list in the `set_answer()` method:

```python
valid_models = [
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
    "your-custom-model"
]
```

### Custom Tools

Add your tools to the question hint:

```python
"hint": "Available: web_search, calculator, your_custom_tool"
```

## 🔍 Advanced Usage

### Programmatic Access

You can also use the MCP server programmatically:

```python
import json
import subprocess

# Start the MCP server
server = subprocess.Popen(
    ["python", "agent_creator_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send a request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "start_agent_creation",
        "arguments": {"session_id": "test-001"}
    }
}

server.stdin.write(json.dumps(request) + "\n")
server.stdin.flush()

# Read response
response = json.loads(server.stdout.readline())
print(response)
```

### Integration with CI/CD

Use the agent creator in automated workflows:

```bash
# Create a script that answers questions non-interactively
./create_agent.sh \
  --name data_processor \
  --model gpt-4 \
  --tools "json_validator, data_cleaner" \
  --output config.yaml
```

## 🧪 Testing

Test the MCP server directly:

```bash
# Start the server
python agent_creator_server.py

# In another terminal, send test requests
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python agent_creator_server.py
```

## 📚 Related Documentation

- [MCP Integration Guide](../../docs/guides/mcp.md) - Learn more about MCP servers
- [Tool Calling Guide](../../docs/guides/tool-calling.md) - Tool calling in Weave
- [Configuration Reference](../../docs/reference/configuration.md) - YAML schema
- [Writing Configs](../../docs/guides/writing-configs.md) - Best practices

## 💡 Use Cases

This pattern is useful for:

- **Interactive CLI tools** - Guide users through complex configurations
- **Configuration wizards** - Step-by-step setup processes
- **Template generators** - Create configurations from templates
- **Validation systems** - Validate configs through Q&A
- **Learning tools** - Help users understand agent configuration

## 🤝 Contributing

Have ideas for improving this example? Contributions welcome!

- Add more question types
- Support for workflow (weaves) creation
- Configuration templates
- Visual configuration builder
- Export to different formats

## 📄 License

MIT License - same as the Weave project.
