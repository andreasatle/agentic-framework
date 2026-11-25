#!/usr/bin/env bash
# A PDF beside every tutorial page in src/web/static/agentswarm/, printed by headless Chrome so the maths
# (KaTeX, loaded by the page) is rendered. Only pages newer than their PDF are printed again.
set -euo pipefail
cd "$(dirname "$0")/../src/web/static/agentswarm"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
for page in *.html; do
  pdf="${page%.html}.pdf"
  if [ -f "$pdf" ] && [ "$pdf" -nt "$page" ]; then continue; fi
  "$chrome" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 \
    --print-to-pdf="$PWD/$pdf" "file://$PWD/$page" 2>/dev/null
  echo "[pdf] $pdf"
done
