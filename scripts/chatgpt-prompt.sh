#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== BEHAVIORAL CONSTRAINTS ==="
cat "$SCRIPT_DIR/ai_behavior_prompt.txt"

echo
echo "=== PROJECT SNAPSHOT ==="
"$SCRIPT_DIR/project-snapshot.sh" "$@"
