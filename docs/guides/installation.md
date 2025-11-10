# Installation Guide

Complete guide to installing and setting up Weave CLI.

## Quick Start

The fastest way to get started:

```bash
# Install Weave
curl -fsSL https://weave.dev/install.sh | bash

# Run setup wizard
weave setup

# Verify installation
weave doctor
```

---

## Installation Methods

### Method 1: One-Command Install (Recommended)

The installation script handles everything automatically:

```bash
curl -fsSL https://weave.dev/install.sh | bash
```

**What it does:**
- ✓ Checks Python 3.9+ is installed
- ✓ Clones Weave repository
- ✓ Installs core dependencies
- ✓ Offers to install optional features (LLM, deployment, dev tools)
- ✓ Verifies installation

After installation, run:

```bash
weave setup
```

### Method 2: Manual Installation

For more control over the installation process:

```bash
# 1. Clone repository
git clone https://github.com/weave/weave-cli.git
cd weave-cli

# 2. Install core package
pip install -e .

# 3. Verify
weave --version

# 4. Run setup wizard
weave setup
```

### Method 3: pip Install (Coming Soon)

Once published to PyPI:

```bash
# Basic installation
pip install weave-cli

# With all features
pip install weave-cli[all]
```

---

## Optional Features

Weave has modular optional dependencies. Install what you need:

### LLM Execution

For real OpenAI and Anthropic API calls:

```bash
pip install weave-cli[llm]
```

Includes:
- `openai>=1.0.0`
- `anthropic>=0.18.0`

### Cloud Deployment

For deploying to AWS, GCP, or Docker:

```bash
# All deployment providers
pip install weave-cli[deploy]

# Or specific providers
pip install weave-cli[aws]    # AWS Lambda
pip install weave-cli[gcp]    # GCP Cloud Functions
pip install weave-cli[docker] # Docker
```

### Development Tools

For file watching and auto-reload:

```bash
pip install weave-cli[watch]
```

Includes:
- `watchdog>=3.0.0` for `weave dev --watch`

### Everything

All optional features at once:

```bash
pip install weave-cli[all]
```

---

## Post-Install Setup

### Setup Wizard

Run the interactive setup wizard after installation:

```bash
weave setup
```

**The wizard will:**

1. **Create ~/.weave directory**
   - Configuration storage
   - State tracking
   - Cache directory

2. **Configure API keys** (optional)
   - OpenAI API key
   - Anthropic API key
   - Creates `.env` file in current directory

3. **Install shell completion** (optional)
   - Auto-detects your shell (bash/zsh/fish)
   - Installs tab-completion
   - Updates shell config file

4. **Create example project** (optional)
   - Generates `.weave.yaml` in current directory
   - Ready-to-run example workflow

### Manual Setup Steps

If you prefer manual setup:

#### 1. Install Shell Completion

```bash
# Auto-detect shell and install
weave completion bash --install
weave completion zsh --install
weave completion fish --install

# Show completion script
weave completion bash --show
```

After installation, restart your shell or:

```bash
# Bash
source ~/.bashrc

# Zsh
source ~/.zshrc

# Fish
source ~/.config/fish/config.fish
```

#### 2. Configure API Keys

Create `.env` file in your project:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Or set environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

#### 3. Create Configuration Directory

```bash
mkdir -p ~/.weave/cache
touch ~/.weave/state.yaml
```

---

## Verification

### Check Installation

Run the diagnostic command:

```bash
weave doctor
```

**Example output:**

```
Weave Installation Status

Component      Status           Notes
─────────────────────────────────────────────
Core           ✓ Installed      v0.1.0
OpenAI         ✓ Installed
Anthropic      ✓ Installed
Watchdog       ✓ Installed
Boto3 (AWS)    - Not installed  Optional
Docker         - Not installed  Optional
Config Dir     ✓ Exists         ~/.weave
OpenAI Key     ✓ Set
Anthropic Key  ✓ Set

Recommendations:
  • Install deployment support: pip install weave-cli[deploy]
```

### Test Weave

Create a simple workflow and test it:

```bash
# Create example
weave init

# Test in mock mode (no API calls)
weave apply

# View help
weave --help
```

---

## System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher
- **pip**: Latest version recommended
- **Git**: For cloning repository
- **Operating System**: Linux, macOS, or Windows (WSL)

### Recommended

- **Python**: 3.11+ for best performance
- **Shell**: bash, zsh, or fish for completion support
- **Memory**: 512MB+ available RAM
- **Disk**: 100MB+ for installation

### Optional Requirements

For specific features:

- **AWS CLI**: For AWS deployments
- **gcloud CLI**: For GCP deployments
- **Docker**: For container deployments

---

## Troubleshooting

### Common Issues

#### "Python not found"

```bash
# Check Python version
python3 --version

# Install Python 3.9+ if needed
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Windows
# Download from python.org
```

#### "pip not found"

```bash
# Install pip
python3 -m ensurepip --upgrade

# Or
curl https://bootstrap.pypa.io/get-pip.py | python3
```

#### "weave command not found"

The weave command may not be in your PATH. Try:

```bash
# Find where pip installed it
pip show weave-cli

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$HOME/.local/bin"

# Or use python -m
python3 -m weave --help
```

#### "Permission denied" during install

```bash
# Use --user flag
pip install --user -e .

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### Shell completion not working

```bash
# Manually source completion
source <(weave completion bash --show)

# Or add to shell config manually
weave completion bash --show >> ~/.bashrc
```

---

## Updating Weave

### From Git

```bash
cd weave-cli
git pull
pip install -e . --upgrade
```

### From pip (when available)

```bash
pip install --upgrade weave-cli
```

---

## Uninstalling

### Remove Package

```bash
pip uninstall weave-cli
```

### Clean Up Files

```bash
# Remove configuration
rm -rf ~/.weave

# Remove shell completion
# Edit your shell config file and remove Weave completion lines

# Remove cloned repository
rm -rf weave-cli
```

---

## Advanced Installation

### Virtual Environment

Recommended for isolation:

```bash
# Create virtual environment
python3 -m venv weave-env

# Activate
source weave-env/bin/activate  # Linux/macOS
# or
weave-env\Scripts\activate  # Windows

# Install
pip install weave-cli[all]

# Deactivate when done
deactivate
```

### Development Installation

For contributing to Weave:

```bash
# Clone repository
git clone https://github.com/weave/weave-cli.git
cd weave-cli

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
```

### Docker Installation

Run Weave in a container:

```bash
# Build image
docker build -t weave-cli .

# Run
docker run -it weave-cli weave --help

# With volume mount
docker run -v $(pwd):/workspace -it weave-cli
```

---

## Next Steps

After installation:

1. **Run setup wizard**: `weave setup`
2. **Create example project**: `weave init`
3. **Test with mock mode**: `weave apply`
4. **Set up API keys** for real execution
5. **Install shell completion** for better UX
6. **Read the documentation**: [docs.weave.dev](https://docs.weave.dev)

---

## Getting Help

- **Check installation**: `weave doctor`
- **View help**: `weave --help`
- **Report issues**: [GitHub Issues](https://github.com/weave/weave-cli/issues)
- **Documentation**: [docs.weave.dev](https://docs.weave.dev)
