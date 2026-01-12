#!/usr/bin/env bash
set -e

if [ "$#" -eq 0 ]; then
  set -- src
fi

git ls-files "$@" | sort | while read -r file; do
  echo
  echo "===== FILE: $file ====="
  echo
  cat "$file"
done
