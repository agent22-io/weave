# Installation

## Requirements

- **Python**: 3.9 or higher
- **pip**: Latest version recommended

## Installation Methods

### From Source (Current)

```bash
# Clone the repository
git clone https://github.com/weave/weave-cli.git
cd weave-cli

# Install the package
pip install -e .

# Verify installation
weave --version
```

### From PyPI (Coming Soon)

```bash
pip install weave-cli
```

## Verify Installation

Run the following command to verify Weave is installed correctly:

```bash
weave --version
```

You should see:
```
Weave version 0.1.0
```

## Dependencies

Weave automatically installs these dependencies:

- `typer>=0.9.0` - CLI framework
- `rich>=13.7.0` - Terminal formatting
- `pydantic>=2.5.0` - Data validation
- `pyyaml>=6.0.1` - YAML parsing
- `networkx>=3.2.0` - Graph algorithms

## Development Installation

If you want to contribute or modify Weave:

```bash
# Clone and install with dev dependencies
git clone https://github.com/weave/weave-cli.git
cd weave-cli
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## Troubleshooting

### Command not found

If `weave` command is not found after installation:

1. Check if the installation directory is in your PATH
2. Try using `python -m weave` instead
3. Reinstall with `pip install --force-reinstall -e .`

### Permission Errors

If you encounter permission errors during installation:

```bash
# Use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Python Version Issues

Ensure you're using Python 3.9 or higher:

```bash
python --version
```

If you have multiple Python versions, use:

```bash
python3.9 -m pip install -e .
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Create your first workflow
- [Core Concepts](concepts.md) - Understand how Weave works
