#!/usr/bin/env bash
# Install git hooks by symlinking from scripts/ to .git/hooks/
# Usage: bash scripts/install-hooks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_DIR="$(git rev-parse --show-toplevel)/.git/hooks"

for hook in pre-commit commit-msg; do
    if [ -f "$SCRIPT_DIR/$hook" ]; then
        ln -sf "$SCRIPT_DIR/$hook" "$HOOKS_DIR/$hook"
        chmod +x "$HOOKS_DIR/$hook"
        echo "Installed $hook hook"
    fi
done

echo "Done! Git hooks installed."
