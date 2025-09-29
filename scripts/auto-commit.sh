#!/bin/bash
# Automated commit script for TDD checkpoints

CHECKPOINT_MSG="$1"

if [ -z "$CHECKPOINT_MSG" ]; then
    echo "Usage: $0 'commit message'"
    exit 1
fi

echo "🚀 Auto-commit checkpoint: $CHECKPOINT_MSG"

# Add all changes
git add .

# Create commit with TDD checkpoint format
git commit -m "$CHECKPOINT_MSG

📋 TDD Checkpoint - automated commit for development milestone

🔧 Generated with OSINT LLM Framework TDD workflow"

if [ $? -eq 0 ]; then
    echo "✅ Committed: $CHECKPOINT_MSG"
else
    echo "❌ Commit failed"
    exit 1
fi
