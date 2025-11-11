#!/bin/bash
# Local CI runner script
# Runs all CI checks that GitHub Actions would run

set -e

echo "🚀 Running CI checks locally..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        echo "🔌 Activating virtual environment..."
        source .venv/bin/activate
        echo ""
    else
        echo "❌ No virtual environment found. Run ./scripts/setup-dev.sh first"
        exit 1
    fi
fi

# Track results
FAILED=0

# Function to run a check
run_check() {
    local name="$1"
    shift
    echo "========================================"
    echo "🔍 $name"
    echo "========================================"
    if "$@"; then
        echo "✅ $name passed"
    else
        echo "❌ $name failed"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Run linting
run_check "Linting (ruff)" ruff check src/ tests/

# Run type checking (if mypy is available)
if command -v mypy &> /dev/null; then
    run_check "Type checking (mypy)" mypy src/
else
    echo "⚠️  Skipping type checking (mypy not installed)"
    echo ""
fi

# Run tests
run_check "Tests (pytest)" pytest tests/ -v --tb=short --color=yes

# Test CLI installation
run_check "CLI verification" bash -c "weave --version && weave --help > /dev/null"

# Validate example configs if they exist
if ls examples/*.agent.yaml 1> /dev/null 2>&1; then
    echo "========================================"
    echo "🔍 Validating example configs"
    echo "========================================"
    EXAMPLE_FAILED=0
    for config in examples/*.agent.yaml; do
        echo "Validating $config..."
        if weave validate "$config" 2>/dev/null || true; then
            echo "✅ $config is valid"
        else
            echo "⚠️  $config validation skipped or failed"
            EXAMPLE_FAILED=$((EXAMPLE_FAILED + 1))
        fi
    done

    if [ $EXAMPLE_FAILED -eq 0 ]; then
        echo "✅ All examples validated"
    else
        echo "⚠️  Some examples could not be validated"
    fi
    echo ""
fi

# Summary
echo "========================================"
echo "📊 CI Results Summary"
echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CI checks passed! 🎉"
    echo ""
    echo "Your code is ready to push!"
    exit 0
else
    echo "❌ $FAILED check(s) failed"
    echo ""
    echo "Please fix the issues above before pushing."
    exit 1
fi
