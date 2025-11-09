#!/bin/bash
# Script to install pre-commit hooks for introligo project
# This will run all quality checks (ruff, mypy, bandit, pylint, interrogate, xenon) before each commit

set -e

echo "Installing pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "pre-commit is not installed. Installing..."
    pip install pre-commit
fi

# Install the git hooks
pre-commit install

echo ""
echo "✓ Pre-commit hooks installed successfully!"
echo ""
echo "The following checks will run before each commit:"
echo "  1. Ruff (linter and formatter)"
echo "  2. MyPy (type checker)"
echo "  3. Bandit (security checker)"
echo "  4. Pylint (code quality)"
echo "  5. Interrogate (docstring coverage)"
echo "  6. Xenon (complexity checker)"
echo ""
echo "To run hooks manually on all files: pre-commit run --all-files"
echo "To skip hooks for a commit: git commit --no-verify"
