#!/usr/bin/env bash
# Deploy atle.dev: push main to GitHub, then pull + restart on the Lightsail server.
# Requires the "atle" host entry in ~/.ssh/config (see DEPLOY.md).
set -euo pipefail

cd "$(dirname "$0")/.."

branch=$(git branch --show-current)
if [ "$branch" != "main" ]; then
  echo "[deploy] on branch '$branch', not main; merge into main first" >&2
  exit 1
fi

echo "[deploy] pushing main"
git push origin main

echo "[deploy] updating server"
ssh atle 'cd /opt/agentic && test -z "$(git status --porcelain --untracked-files=no)" || { echo "[deploy] server checkout has local changes; aborting" >&2; git status --short; exit 1; } && ./update.sh && systemctl is-active agentic'

echo "[deploy] done: https://atle.dev"
