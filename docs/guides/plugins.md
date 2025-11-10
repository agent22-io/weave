# Plugins

Extend Weave with custom tools and capabilities using the plugin system.

## Overview

Plugins provide reusable tools that agents can use during execution. Weave includes built-in plugins and supports community-developed plugins.

### Plugin Categories

Plugins are organized by use case:

| Category | Description | Examples |
|----------|-------------|----------|
| `data_collection` | Gather data from sources | API clients, web scrapers |
| `data_processing` | Transform and clean data | Parsers, cleaners, validators |
| `data_analysis` | Analyze and extract insights | Statistical tools, ML models |
| `content_generation` | Create content | Text generators, templates |
| `content_analysis` | Analyze content | Sentiment analysis, summarizers |
| `web` | Web operations | Search, scraping, HTTP clients |
| `api` | API integrations | REST clients, GraphQL |
| `database` | Database operations | SQL, NoSQL clients |
| `llm` | LLM operations | Model calls, embeddings |
| `formatting` | Format output | Markdown, JSON, HTML |
| `validation` | Validate data | Schema validators, type checkers |
| `integration` | External service connectors | Cloud services, SaaS tools |
| `custom` | Custom functionality | Domain-specific tools |

---

## Built-in Plugins

### List Available Plugins

```bash
# List all plugins
weave plugins

# Verbose output with descriptions
weave plugins --verbose

# Filter by category
weave plugins --category web
weave plugins --category data_processing
```

**Output:**
```
Available Plugins
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Name               ┃ Version ┃ Category         ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ web_search         │ 1.0.0   │ web              │
│ summarizer         │ 1.0.0   │ content_analysis │
│ data_cleaner       │ 1.0.0   │ data_processing  │
│ json_parser        │ 1.0.0   │ data_processing  │
│ markdown_formatter │ 1.0.0   │ formatting       │
└────────────────────┴─────────┴──────────────────┘
```

### Built-in Plugin Descriptions

#### web_search
- **Category:** Web
- **Description:** Search the web for information
- **Use Case:** Research, information gathering

#### summarizer
- **Category:** Content Analysis
- **Description:** Summarize long text into shorter form
- **Use Case:** Content condensation, key points extraction

#### data_cleaner
- **Category:** Data Processing
- **Description:** Clean and normalize data (remove nulls, whitespace, etc.)
- **Use Case:** Data preprocessing, ETL pipelines

#### json_parser
- **Category:** Data Processing
- **Description:** Parse and validate JSON data
- **Use Case:** API response handling, data validation

#### markdown_formatter
- **Category:** Formatting
- **Description:** Format data as Markdown documents
- **Use Case:** Documentation generation, reporting

---

## Using Plugins in Configs

### Basic Usage

Reference plugins by name in the `tools` field:

```yaml
agents:
  researcher:
    model: "gpt-4"
    tools:
      - web_search          # Built-in plugin
      - summarizer          # Built-in plugin
```

### Plugin Configuration

Some plugins accept configuration:

```yaml
agents:
  text_processor:
    model: "gpt-4"
    tools:
      - summarizer
    config:
      summarizer:
        max_length: 500     # Plugin-specific config
```

### Multiple Plugins

Agents can use multiple plugins:

```yaml
agents:
  data_analyst:
    model: "gpt-4"
    tools:
      - web_search
      - json_parser
      - data_cleaner
      - markdown_formatter
```

---

## Creating Custom Plugins

### Plugin Structure

Create a Python file with a Plugin subclass:

```python
# my_plugin.py
from weave.plugins import Plugin, PluginCategory, PluginMetadata
from typing import Any, Dict, Optional


class MyCustomPlugin(Plugin):
    """My custom plugin."""

    metadata = PluginMetadata(
        name="my_custom_tool",
        version="1.0.0",
        description="What my plugin does",
        category=PluginCategory.CUSTOM,
        author="Your Name",
        tags=["custom", "example"],
        requires=[],  # External dependencies
    )

    def execute(
        self, input_data: Any, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute the plugin.

        Args:
            input_data: Input data to process
            context: Execution context (agent info, etc.)

        Returns:
            Plugin output
        """
        # Your plugin logic here
        result = self.process(input_data)
        return result

    def process(self, data: Any) -> Any:
        """Plugin-specific processing."""
        # Implement your logic
        return {"result": data, "processed": True}

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate plugin configuration."""
        # Optional: validate config parameters
        if "required_param" in config:
            if not isinstance(config["required_param"], str):
                raise ValueError("required_param must be a string")
```

### Loading Custom Plugins

```python
from weave.plugins.manager import PluginManager
from pathlib import Path

# Create manager
manager = PluginManager()

# Load built-in plugins
manager.load_builtin_plugins()

# Load custom plugin
manager.load_plugin_from_file(Path("my_plugin.py"))

# Or load all plugins from directory
manager.load_plugins_from_directory(Path("./plugins"))
```

---

## Plugin Examples

### Example 1: API Client Plugin

```python
from weave.plugins import Plugin, PluginCategory, PluginMetadata
import requests


class APIClientPlugin(Plugin):
    """HTTP API client plugin."""

    metadata = PluginMetadata(
        name="api_client",
        version="1.0.0",
        description="Make HTTP API requests",
        category=PluginCategory.API,
        author="Your Name",
        tags=["api", "http", "rest"],
    )

    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Any:
        """Make API request."""
        url = self.config.get("url")
        method = self.config.get("method", "GET")
        headers = self.config.get("headers", {})

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=input_data, headers=headers)

        return {
            "status_code": response.status_code,
            "data": response.json(),
            "headers": dict(response.headers),
        }

    def validate_config(self, config: Dict) -> None:
        if "url" not in config:
            raise ValueError("API client requires 'url' in config")
```

### Example 2: Database Query Plugin

```python
from weave.plugins import Plugin, PluginCategory, PluginMetadata
import sqlite3


class SQLQueryPlugin(Plugin):
    """Execute SQL queries."""

    metadata = PluginMetadata(
        name="sql_query",
        version="1.0.0",
        description="Execute SQL queries on SQLite databases",
        category=PluginCategory.DATABASE,
        author="Your Name",
        tags=["sql", "database", "query"],
    )

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.conn = None

    def on_load(self):
        """Connect to database on load."""
        db_path = self.config.get("database", ":memory:")
        self.conn = sqlite3.connect(db_path)

    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Any:
        """Execute SQL query."""
        query = str(input_data)
        cursor = self.conn.cursor()
        cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            return {"rows": results, "count": len(results)}
        else:
            self.conn.commit()
            return {"affected_rows": cursor.rowcount}

    def on_unload(self):
        """Close connection on unload."""
        if self.conn:
            self.conn.close()
```

### Example 3: Email Sender Plugin

```python
from weave.plugins import Plugin, PluginCategory, PluginMetadata
import smtplib
from email.mime.text import MIMEText


class EmailPlugin(Plugin):
    """Send emails via SMTP."""

    metadata = PluginMetadata(
        name="email_sender",
        version="1.0.0",
        description="Send emails via SMTP",
        category=PluginCategory.INTEGRATION,
        author="Your Name",
        tags=["email", "smtp", "notification"],
    )

    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Any:
        """Send email."""
        # Parse input
        if isinstance(input_data, dict):
            to = input_data.get("to")
            subject = input_data.get("subject")
            body = input_data.get("body")
        else:
            # Input is email body, use config for to/subject
            to = self.config.get("to")
            subject = self.config.get("subject", "Notification from Weave")
            body = str(input_data)

        # Create message
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.config["from"]
        msg["To"] = to

        # Send
        with smtplib.SMTP(self.config["smtp_host"], self.config.get("smtp_port", 587)) as server:
            server.starttls()
            server.login(self.config["smtp_user"], self.config["smtp_password"])
            server.send_message(msg)

        return {"status": "sent", "to": to}

    def validate_config(self, config: Dict) -> None:
        required = ["smtp_host", "smtp_user", "smtp_password", "from"]
        for field in required:
            if field not in config:
                raise ValueError(f"Email plugin requires '{field}' in config")
```

---

## Plugin Best Practices

### 1. Clear Metadata

```python
metadata = PluginMetadata(
    name="descriptive_name",        # Clear, unique name
    version="1.0.0",                # Semantic versioning
    description="What it does",     # User-friendly description
    category=PluginCategory.WEB,    # Appropriate category
    author="Your Name",             # Attribution
    tags=["search", "api"],         # Searchable tags
)
```

### 2. Error Handling

```python
def execute(self, input_data: Any, context: Optional[Dict] = None) -> Any:
    try:
        result = self.process(input_data)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

### 3. Configuration Validation

```python
def validate_config(self, config: Dict) -> None:
    # Validate required fields
    if "api_key" not in config:
        raise ValueError("Plugin requires 'api_key' in config")

    # Validate types
    if not isinstance(config.get("timeout", 30), int):
        raise ValueError("'timeout' must be an integer")

    # Validate values
    if config.get("max_retries", 3) < 0:
        raise ValueError("'max_retries' must be non-negative")
```

### 4. Resource Management

```python
def on_load(self):
    """Initialize resources."""
    self.connection = create_connection(self.config)

def on_unload(self):
    """Clean up resources."""
    if self.connection:
        self.connection.close()
```

### 5. Type Hints

```python
from typing import Any, Dict, Optional, List

def execute(
    self,
    input_data: Any,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Type hints for clarity."""
    pass
```

---

## Plugin Distribution

### Sharing Plugins

1. **GitHub Repository:**
```bash
# Users can install
pip install git+https://github.com/username/weave-my-plugin
```

2. **PyPI Package:**
```bash
# Package as pip installable
pip install weave-my-plugin
```

3. **Local Distribution:**
```bash
# Share Python file
weave load-plugin ~/Downloads/my_plugin.py
```

### Plugin Naming Convention

- Prefix with `weave-` for PyPI packages
- Use snake_case for plugin names
- Example: `weave-slack-notifier`, plugin name: `slack_notifier`

---

## Troubleshooting

### Plugin Not Found

```bash
# List available plugins
weave plugins

# Check if plugin loaded
weave plugins --verbose | grep my_plugin
```

### Configuration Errors

```yaml
# Incorrect:
agents:
  my_agent:
    tools: my_plugin    # Should be a list!

# Correct:
agents:
  my_agent:
    tools: [my_plugin]
```

### Loading Errors

```python
# Check plugin file
python my_plugin.py

# Verify Plugin subclass exists
from my_plugin import MyPlugin
```

---

## Future Enhancements (v2.0)

- **Plugin Registry** - Central repository for community plugins
- **Plugin Marketplace** - Discover and install plugins via CLI
- **Plugin Dependencies** - Automatic dependency resolution
- **Plugin Hooks** - More extension points
- **Real-time Execution** - Plugins execute during agent runs

---

## Next Steps

- [Writing Configurations](writing-configs.md) - Using plugins in configs
- [Extensibility](../architecture/extensibility.md) - Advanced customization
- [Examples](../../examples/) - See plugins in action
