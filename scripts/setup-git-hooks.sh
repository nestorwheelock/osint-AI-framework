#!/bin/bash
# Setup script to install git hooks for the project

set -e

echo "🔧 Setting up Git hooks for OSINT LLM Framework..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook
if [ -f ".githooks/pre-commit" ]; then
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook installed (AI attribution prevention)"
else
    echo "❌ Warning: .githooks/pre-commit not found"
fi

# Configure git to use the hooks directory
git config core.hooksPath .githooks

echo ""
echo "🎉 Git hooks setup complete!"
echo ""
echo "The following hooks are now active:"
echo "  • pre-commit: Prevents AI attribution from being committed"
echo ""
echo "These hooks enforce security requirements automatically."
echo "To bypass a hook (NOT RECOMMENDED), use: git commit --no-verify"