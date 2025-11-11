#!/bin/bash
# Development environment setup script using uv
# This script sets up a local development environment that mirrors CI

set -e

echo "🔧 Setting up Weave development environment..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Install it with:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Found uv: $(uv --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate
echo ""

# Install dependencies
echo "📥 Installing dependencies (this may take a moment)..."
uv pip install -e ".[dev,all]"
echo "✅ Dependencies installed"
echo ""

# Verify installation
echo "🧪 Verifying installation..."
weave --version
echo ""

echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "   source .venv/bin/activate"
echo ""
echo "To run CI checks locally, use:"
echo "   ./scripts/run-ci.sh"
echo "   or: make test lint"
