# OpenAI-Compatible API Mode

Weave now supports running agents as OpenAI-compatible API endpoints. This allows you to consume Weave agents using any OpenAI-compatible client or library.

## Installation

Install Weave with API support:

```bash
pip install 'weave-cli[api]'
```

Or install the dependencies separately:

```bash
pip install fastapi uvicorn[standard]
```

## Usage

### Starting the Server

Start a Weave agent as an OpenAI-compatible API server:

```bash
weave run agent researcher --openai-mode
```

This will start a server on `http://0.0.0.0:8765` by default.

### Custom Host and Port

You can customize the host and port:

```bash
weave run agent researcher --openai-mode --host 127.0.0.1 --port 3000
```

### Server Output

When running in OpenAI mode, you'll see simple feedback output:

```
[2025-11-12 10:30:45] [INFO] Starting Weave OpenAI-Compatible API server...
[2025-11-12 10:30:45] [INFO] Agent: researcher
[2025-11-12 10:30:45] [INFO] Config: .agent.yaml
[2025-11-12 10:30:45] [INFO] ✓ Loaded agent: researcher
[2025-11-12 10:30:45] [INFO] ✓ Model: gemini-2.5-flash
[2025-11-12 10:30:45] [INFO] ✓ Server started on http://0.0.0.0:8765
[2025-11-12 10:30:45] [INFO] ✓ Endpoint: http://0.0.0.0:8765/v1/chat/completions
```

Request/response logs:

```
[2025-11-12 10:31:00] [INFO] → Request: model=researcher, stream=false
[2025-11-12 10:31:00] [INFO]   Message: What is the capital of France?
[2025-11-12 10:31:02] [INFO] ← Response: session=a1b2c3d4
[2025-11-12 10:31:02] [INFO]   Content: The capital of France is Paris. It is the country's largest city...
```

Tool call logs (when agent uses tools):

```
[2025-11-12 10:32:15] [INFO] → Request: model=researcher, stream=false
[2025-11-12 10:32:15] [INFO]   Message: Search for latest AI news
[2025-11-12 10:32:17] [INFO] 🔧 Tool Calls: session=b2c3d4e5, count=1
[2025-11-12 10:32:17] [INFO]   [1] web_search({"query": "latest AI news 2025"})
[2025-11-12 10:32:17] [INFO] ← Response: session=b2c3d4e5
[2025-11-12 10:32:17] [INFO]   Content: Based on recent searches, here are the latest AI developments...
```

## API Endpoints

### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint.

**Request:**

```json
{
  "model": "researcher",
  "messages": [
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "stream": false
}
```

**Response:**

```json
{
  "id": "chatcmpl-a1b2c3d4e5f6",
  "object": "chat.completion",
  "created": 1699564800,
  "model": "researcher",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 7,
    "completion_tokens": 15,
    "total_tokens": 22
  }
}
```

### GET /v1/models

List available models.

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "researcher",
      "object": "model",
      "created": 1699564800,
      "owned_by": "weave"
    }
  ]
}
```

### GET /

Server information.

**Response:**

```json
{
  "name": "Weave OpenAI-Compatible API",
  "agent": "researcher",
  "model": "gemini-2.5-flash",
  "endpoints": ["/v1/chat/completions"]
}
```

## Using with OpenAI Client Libraries

### Python (OpenAI SDK)

```python
from openai import OpenAI

# Point to your Weave server
client = OpenAI(
    base_url="http://localhost:8765/v1",
    api_key="dummy"  # Not used, but required by the SDK
)

response = client.chat.completions.create(
    model="researcher",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

### JavaScript/TypeScript

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8765/v1',
  apiKey: 'dummy'  // Not used, but required by the SDK
});

const response = await client.chat.completions.create({
  model: 'researcher',
  messages: [
    { role: 'user', content: 'What is the capital of France?' }
  ]
});

console.log(response.choices[0].message.content);
```

### cURL

```bash
curl http://localhost:8765/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "researcher",
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "stream": false
  }'
```

## Streaming Support

Enable streaming responses by setting `stream: true`:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8765/v1",
    api_key="dummy"
)

stream = client.chat.completions.create(
    model="researcher",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='', flush=True)
```

## Configuration

The server uses your existing `.agent.yaml` configuration:

```yaml
version: "1.0"

agents:
  researcher:
    model: "gemini-2.5-flash"
    tools:
      - http_request
      - file_read
      - json_validator
    config:
      temperature: 0.7
      max_tokens: 1000
```

## Features

- ✅ OpenAI-compatible API format
- ✅ Non-streaming responses
- ✅ Streaming responses
- ✅ Simple, clean logging output with timestamps
- ✅ Tool call logging (shows when agents use tools)
- ✅ Works with any OpenAI-compatible client
- ✅ Headless operation (no interactive prompts)
- ✅ Uses existing Weave agent configurations

## Use Cases

1. **Integration with existing tools**: Use Weave agents with tools that expect OpenAI endpoints
2. **Multi-language support**: Access Weave from any language with an OpenAI client library
3. **Microservices**: Deploy Weave agents as standalone API services
4. **Development**: Test agent behavior programmatically
5. **Production deployments**: Run agents in containerized environments

## Notes

- The `model` parameter in API requests is currently informational (the configured agent model is used)
- API keys from the request are not validated (authentication should be handled at the infrastructure level)
- The server is single-threaded by default; for production use, consider using multiple workers
- Session management is automatic; each request creates a new session

## Advanced Configuration

### Running with Multiple Workers

```bash
uvicorn weave.api.openai_server:app --host 0.0.0.0 --port 8765 --workers 4
```

### Behind a Reverse Proxy

Configure nginx or similar to handle TLS and authentication:

```nginx
location /v1/ {
    proxy_pass http://localhost:8765/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Troubleshooting

### Missing Dependencies

If you see `ModuleNotFoundError: No module named 'fastapi'`:

```bash
pip install 'weave-cli[api]'
```

### Port Already in Use

Change the port:

```bash
weave run agent researcher --openai-mode --port 8766
```

### Agent Not Found

Ensure the agent exists in your config:

```bash
weave plugins  # List available agents
```
