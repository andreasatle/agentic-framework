#!/usr/bin/env bash

echo "=== BEHAVIORAL CONSTRAINTS ==="
cat ai_behavior_prompt.txt

echo
echo "=== PROJECT SNAPSHOT ==="
./project-snapshot.sh "$@"