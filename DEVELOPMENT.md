# Development Guide

This guide covers setting up a local development environment and running CI checks locally.

## Quick Start

### Option 1: Using uv (Recommended - Faster)

```bash
# Setup development environment
make install-uv

# Activate virtual environment
source .venv/bin/activate

# Run all CI checks
make ci
```

### Option 2: Using pip (Traditional)

```bash
# Install with pip
make install-dev

# Run all CI checks
make ci
```

## Detailed Setup

### Using uv Package Manager

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver written in Rust. It's 10-100x faster than pip.

#### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

#### Setup Development Environment

Use the provided setup script:

```bash
./scripts/setup-dev.sh
```

Or manually:

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev,all]"
```

### Using pip (Traditional Method)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -e ".[dev,all]"
```

## Running CI Checks Locally

Before pushing code, run the same checks that GitHub Actions will run:

### Method 1: Using the CI Script (Recommended)

```bash
./scripts/run-ci.sh
```

This runs all checks:
- Linting (ruff)
- Type checking (mypy)
- Tests (pytest)
- CLI verification
- Example config validation

### Method 2: Using Make

```bash
# Run all CI checks
make ci

# Or run individual checks
make lint     # Linting only
make test     # Tests only
make format   # Auto-format code
```

### Method 3: Manual Commands

Run the exact commands from CI:

```bash
# 1. Lint
ruff check src/ tests/

# 2. Type check
mypy src/

# 3. Run tests
pytest tests/ -v --tb=short --color=yes

# 4. Verify CLI
weave --version
weave --help
```

## Development Workflow

### 1. Make Changes

Edit files in `src/` or `tests/`

### 2. Format Code

```bash
make format
```

This runs:
- `black` for code formatting
- `ruff --fix` for auto-fixable linting issues

### 3. Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_specific.py -v

# Run with coverage
pytest tests/ --cov=weave --cov-report=html
```

### 4. Run CI Checks

```bash
make ci
```

### 5. Commit and Push

```bash
git add .
git commit -m "Your commit message"
git push
```

## CI/CD Pipeline

### GitHub Actions Workflows

The repository has two GitHub Actions workflows:

#### Test Workflow (`.github/workflows/test.yml`)

Runs on pushes and PRs to `main`, `develop`, and `claude/**` branches:

- **Tests Job**: Runs on Python 3.10, 3.11, 3.12
  - Install dependencies
  - Lint with ruff
  - Run pytest
  - Test CLI installation

- **Examples Job**: Validates example configs
  - Validate all `.agent.yaml` files
  - Test configs in dry-run mode

#### Release Workflow (`.github/workflows/release.yml`)

Runs when version tags are pushed (e.g., `v0.1.0`):

- Build distribution packages
- Test installation on Python 3.9-3.12
- Create GitHub release
- Publish to PyPI

## Testing Examples

The CI validates all example configurations:

```bash
# Validate all examples
for config in examples/*.agent.yaml; do
  weave validate "$config"
done

# Test in dry-run mode
for config in examples/*.agent.yaml; do
  weave run "$config" --dry-run
done
```

## Makefile Commands

View all available commands:

```bash
make help
```

Common commands:

| Command | Description |
|---------|-------------|
| `make install-uv` | Setup with uv (recommended) |
| `make install-dev` | Setup with pip |
| `make ci` | Run all CI checks |
| `make test` | Run tests |
| `make lint` | Run linting |
| `make format` | Format code |
| `make clean` | Remove build artifacts |
| `make build` | Build distribution packages |

## Troubleshooting

### pip install errors

If you're getting errors with pip, switch to uv:

```bash
make install-uv
```

uv handles dependency resolution better and is more reliable.

### Virtual environment issues

If you have conflicts:

```bash
# Remove old virtual environment
rm -rf .venv

# Create fresh environment
make install-uv
source .venv/bin/activate
```

### Import errors

Make sure the package is installed in editable mode:

```bash
pip install -e ".[dev,all]"
# or
uv pip install -e ".[dev,all]"
```

### Test failures

Run tests with more verbose output:

```bash
pytest tests/ -vv --tb=long
```

## Python Version Support

The project supports Python 3.9+. CI tests on:
- Python 3.10
- Python 3.11
- Python 3.12

Make sure your code works on all supported versions.

## Pre-commit Checks

For extra safety, you can run CI checks before every commit. Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
make lint && make test
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

## Additional Resources

- [Contributing Guide](CONTRIBUTING.md) (if exists)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
