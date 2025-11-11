.PHONY: help clean clean-build clean-pyc install install-dev install-uv test lint format build dist release check-version ci

help:
	@echo "Weave CLI - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install package in development mode (pip)"
	@echo "  make install-dev    - Install package with dev dependencies (pip)"
	@echo "  make install-uv     - Install with uv (recommended, faster)"
	@echo "  make test           - Run tests with pytest"
	@echo "  make lint           - Run linting with ruff"
	@echo "  make format         - Format code with black"
	@echo "  make ci             - Run all CI checks locally"
	@echo ""
	@echo "Building:"
	@echo "  make clean          - Remove all build, test, and Python artifacts"
	@echo "  make build          - Build source and wheel distribution packages"
	@echo "  make dist           - Alias for build"
	@echo ""
	@echo "Release:"
	@echo "  make check-version  - Display current version from pyproject.toml"
	@echo "  make release        - Build and check packages for PyPI release"
	@echo ""

clean: clean-build clean-pyc

clean-build:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	@echo "Cleaning Python artifacts..."
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +

install:
	@echo "Installing package in development mode..."
	pip install -e .

install-dev:
	@echo "Installing package with dev dependencies..."
	pip install -e ".[dev,all]"

install-uv:
	@echo "Setting up development environment with uv (faster)..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ Found uv"; \
		if [ ! -d ".venv" ]; then \
			echo "Creating virtual environment..."; \
			uv venv; \
		fi; \
		echo "Installing dependencies..."; \
		uv pip install -e ".[dev,all]"; \
		echo "✅ Setup complete! Activate with: source .venv/bin/activate"; \
	else \
		echo "❌ uv not found. Install it with:"; \
		echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi

ci:
	@echo "Running CI checks locally..."
	@if [ -f "scripts/run-ci.sh" ]; then \
		./scripts/run-ci.sh; \
	else \
		echo "Running CI checks inline..."; \
		ruff check src/ tests/ && \
		pytest tests/ -v --tb=short --color=yes && \
		weave --version && \
		weave --help >/dev/null && \
		echo "✅ All CI checks passed!"; \
	fi

test:
	@echo "Running tests..."
	pytest tests/ -v --tb=short --color=yes

lint:
	@echo "Running linting checks..."
	ruff check src/ tests/
	@echo "Running type checks..."
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/
	ruff check --fix src/ tests/

build: clean
	@echo "Building source and wheel distribution..."
	pip install --upgrade build --break-system-packages 2>/dev/null || pip install --upgrade build --user || pip install build
	python -m build
	@echo ""
	@echo "Build complete! Packages created in dist/"
	@ls -lh dist/

dist: build

check-version:
	@echo "Current version:"
	@grep '^version = ' pyproject.toml | head -1

release: clean
	@echo "Preparing release build..."
	@echo "Current version:"
	@grep '^version = ' pyproject.toml | head -1
	@echo ""
	@echo "Building distribution packages..."
	pip install --upgrade build twine --break-system-packages 2>/dev/null || pip install --upgrade build twine --user || pip install build twine
	python -m build
	@echo ""
	@echo "Checking distribution packages..."
	twine check dist/*
	@echo ""
	@echo "Release build complete!"
	@echo "Packages ready for upload:"
	@ls -lh dist/
	@echo ""
	@echo "To upload to PyPI:"
	@echo "  twine upload dist/*"
	@echo ""
	@echo "To upload to Test PyPI:"
	@echo "  twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
