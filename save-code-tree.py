#!/usr/bin/env python3
"""
code_tree_snapshot.py

Build a CODE TREE SNAPSHOT for a given subdirectory and PREPEND an
AUTHORITATIVE API EXTRACTION PROMPT before any code content.

The output is a single Markdown file suitable for closed-world reasoning
and downstream API canonization.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Iterable

# ---------------------------------------------------------------------
# AUTHORITATIVE API EXTRACTION PROMPT (VERBATIM)
# ---------------------------------------------------------------------

API_EXTRACTION_PROMPT = """AUTHORITATIVE API EXTRACTION PROMPT

You are given a CLOSED CODE SUBTREE SNAPSHOT in Markdown form.
The snapshot is authoritative ONLY for the files included.
Anything not present MUST be treated as unknown and MUST NOT be inferred.

Your task is to transform this subtree into a SINGLE, NORMATIVE API DOCUMENT.

GOAL
Produce an authoritative API specification that captures:
- contracts
- types
- invariants
- execution semantics
- extension points
- explicit non-features

This API document must be sufficient for correct reasoning WITHOUT access to the code.

SCOPE RULES
- Use ONLY the provided snapshot.
- Do NOT assume other files, modules, or behavior.
- If something is ambiguous or missing, state it explicitly.
- Prefer omission over guessing.

AUTHORITY RULES
- The API document is NORMATIVE, not descriptive.
- If the code deviates from the API, the code is wrong.
- Implementation details are included ONLY if they define observable behavior.

WHAT TO EXTRACT
1. Core entities (public classes, protocols, schemas)
2. Inputs / outputs and their types
3. Invariants (MUST / MUST NOT)
4. Execution semantics (ordering, atomicity, retry, termination)
5. Authority boundaries (what this layer owns vs delegates)
6. Explicit non-features and forbidden behavior

WHAT TO EXCLUDE
- Logging
- Helper utilities
- Internal normalization helpers
- Provider/client internals (unless they affect semantics)
- UI, CLI, or app wiring (unless this is an app API)

OUTPUT FORMAT
Produce a single Markdown document named appropriately for the subtree, e.g.:
- AGENTIC_API.md
- DOMAIN_<name>_API.md
- APP_<name>_EXECUTION.md

STYLE
- Precise
- Declarative
- Contract-focused
- No fluff

FAILURE MODE
If the subtree is NOT semantically closed, you MUST say so explicitly and list
exactly what is missing.

BEGIN TRANSFORMATION USING THE SNAPSHOT BELOW.
"""

# ---------------------------------------------------------------------
# DEFAULTS
# ---------------------------------------------------------------------

DEFAULT_EXTENSIONS = {".py", ".md", ".toml", ".yaml", ".yml", ".json"}

# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def project_root() -> pathlib.Path:
    return pathlib.Path.cwd().resolve()


def iter_files(root: pathlib.Path, extensions: set[str]) -> list[pathlib.Path]:
    return sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix in extensions
    )


def rel_from_root(path: pathlib.Path, root: pathlib.Path) -> pathlib.Path:
    return path.resolve().relative_to(root)


# ---------------------------------------------------------------------
# SNAPSHOT BUILDER
# ---------------------------------------------------------------------

def build_code_tree_snapshot(
    subdir: str,
    output: str,
    extensions: Iterable[str],
) -> None:
    root = project_root()
    target = (root / subdir).resolve()

    if not target.exists() or not target.is_dir():
        raise ValueError(f"Not a directory: {target}")

    exts = set(extensions)
    files = iter_files(target, exts)

    if not files:
        raise RuntimeError(f"No matching files found under {target}")

    out_path = root / output

    sections: list[str] = []

    # Prompt first
    sections.append(API_EXTRACTION_PROMPT.rstrip())
    sections.append("\n\n---\n\n")

    # Snapshot header
    sections.append("# === CODE TREE SNAPSHOT ===\n\n")
    sections.append(f"**Project root:** `{root}`\n\n")
    sections.append(f"**Subdirectory:** `{rel_from_root(target, root)}`\n\n")
    sections.append(
        "> This snapshot is authoritative only for the files included below.\n"
        "> Any file not present here must be treated as unknown.\n\n"
    )
    sections.append("---\n\n")

    # Files
    for file in files:
        rel = rel_from_root(file, root)
        lang = file.suffix.lstrip(".") or "text"

        sections.append(f"## FILE: `{rel}`\n\n")
        sections.append(f"```{lang}\n")
        sections.append(file.read_text())
        sections.append("\n```\n\n")

    out_path.write_text("".join(sections))

    print(f"Wrote {len(files)} files to {out_path}")
    print(f"Root: {root}")
    print(f"Scope: {rel_from_root(target, root)}")


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a code-tree snapshot with an API-extraction prompt prepended."
    )
    parser.add_argument(
        "subdir",
        help="Subdirectory (relative to project root) to snapshot",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="code_tree_snapshot.md",
        help="Output Markdown file (relative to project root)",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=list(DEFAULT_EXTENSIONS),
        help="File extension to include (repeatable).",
    )

    args = parser.parse_args()
    build_code_tree_snapshot(
        subdir=args.subdir,
        output=args.output,
        extensions=args.ext,
    )


if __name__ == "__main__":
    main()
