#!/usr/bin/env bash

ROOT="${1:-.}"

find "$ROOT" -type f \
  ! -path "*/.git/*" \
  ! -path "*/.venv/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/node_modules/*" \
  ! -name "*.pyc" \
  | sort \
  | while read -r file; do
      echo
      echo "===== FILE: $file ====="
      echo
      cat "$file"
    done
