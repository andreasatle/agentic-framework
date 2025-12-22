#!/usr/bin/env python3
"""
This module injects a project-specific bootstrap prompt into ChatGPT and
builds a *selective, authoritative snapshot* of the codebase.

The snapshot is intentionally PARTIAL:
- Architecturally normative modules are always included
- Domain code is opt-in via --domain
- App code is opt-in via --app
- Anything not included must be treated as unknown

If this module drifts from actual architecture, the system will silently degrade.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Iterable

# ---------------------------------------------------------------------
# BOOTSTRAP PROMPT (VERBATIM)
# ---------------------------------------------------------------------

BOOTSTRAP_PROMPT = '''AGENTIC PROJECT BOOTSTRAP PROMPT (PASTE AT START OF NEW SESSION)

INITIALIZATION — DO NOT MODIFY

You (ChatGPT) are assisting me (Andreas) with a multi-agent LLM framework project.
You must always:

give crisp, critical, focused answers
challenge assumptions
avoid unrequested brainstorming
avoid rambling or revisiting old topics
produce short, accurate, technical responses
not hallucinate missing details
not invent architecture I did not approve

Constraints:
Controller must remain domain-independent.
No structural changes unless I explicitly request them.
All code must remain strict-schema validated.

When I explicitly ask for:
- a Codex prompt, or
- a commit message

You must:
- return exactly ONE code block per requested artifact
- use plain triple backticks ``` … ```
- include no prose, explanation, or commentary outside the code block
- not combine multiple artifacts in a single code block
- not infer that I want Codex prompts or commit messages unless I explicitly ask

Your role:
Keep critiques strong and eliminate fluff.
Ask clarifying questions when anything is ambiguous.
Prefer surgical patches over large rewrites.
Never assume brainstorming unless I explicitly say “brainstorm.”

END OF BOOTSTRAP PROMPT
'''

# ---------------------------------------------------------------------
# SELECTION POLICY (NORMATIVE)
# ---------------------------------------------------------------------

ARCH_CORE = [
    "src/agentic/controller.py",
    "src/agentic/supervisor.py",
    "src/agentic/agent_dispatcher.py",
    "src/agentic/tool_registry.py",
]

SCHEMA_GLOBS = [
    "src/agentic/schemas/*.py",
    "src/domain/*/schemas.py",
]

# ---------------------------------------------------------------------
# COLLECTION HELPERS
# ---------------------------------------------------------------------

def _existing(paths: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    return sorted({p for p in paths if p.exists()})


def collect_arch_files() -> list[pathlib.Path]:
    files = [pathlib.Path(p) for p in ARCH_CORE]
    for pattern in SCHEMA_GLOBS:
        files.extend(pathlib.Path(".").glob(pattern))
    return _existing(files)


def collect_domain_files(domains: list[str]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for domain in domains:
        root = pathlib.Path("src/domain") / domain
        if not root.exists():
            raise FileNotFoundError(f"Domain not found: {root}")
        files.extend(root.rglob("*.py"))
    return _existing(files)


def collect_app_files(apps: list[str]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for app in apps:
        root = pathlib.Path("src/apps") / app
        if not root.exists():
            raise FileNotFoundError(f"App not found: {root}")
        files.extend(root.rglob("*.py"))
    return _existing(files)


# ---------------------------------------------------------------------
# SNAPSHOT ASSEMBLY
# ---------------------------------------------------------------------

def build_snapshot(domains: list[str], apps: list[str]) -> None:
    out_file = pathlib.Path("combined_project_snapshot.md")

    header = (
        "# === AGENTIC PROJECT SNAPSHOT ===\n"
        "*authoritative_scope: partial*\n\n"
        "> ChatGPT must reason **only** from the files included below.\n"
        "> Any module, behavior, or dependency not shown here must be treated as unknown.\n"
        "> Architectural assumptions beyond this snapshot are forbidden.\n\n"
        "---\n\n"
    )

    sections: list[str] = []

    # pyproject.toml (always first, if present)
    pyproject = pathlib.Path("pyproject.toml")
    if pyproject.exists():
        sections.append("## FILE: `pyproject.toml`\n\n")
        sections.append("```toml\n")
        sections.append(pyproject.read_text())
        sections.append("\n```\n\n")

    # Core architecture
    for f in collect_arch_files():
        rel = f.relative_to(pathlib.Path("."))
        sections.append(f"## FILE: `{rel}`\n\n")
        sections.append("```python\n")
        sections.append(f.read_text())
        sections.append("\n```\n\n")

    # Optional domains
    if domains:
        for f in collect_domain_files(domains):
            rel = f.relative_to(pathlib.Path("."))
            sections.append(f"## FILE: `{rel}`\n\n")
            sections.append("```python\n")
            sections.append(f.read_text())
            sections.append("\n```\n\n")

    # Optional apps
    if apps:
        for f in collect_app_files(apps):
            rel = f.relative_to(pathlib.Path("."))
            sections.append(f"## FILE: `{rel}`\n\n")
            sections.append("```python\n")
            sections.append(f.read_text())
            sections.append("\n```\n\n")

    content = BOOTSTRAP_PROMPT + header + "".join(sections)
    out_file.write_text(content)

    print(
        f"Wrote snapshot to {out_file}\n"
        f"- Core files: {len(collect_arch_files())}\n"
        f"- Domains: {domains or 'none'}\n"
        f"- Apps: {apps or 'none'}"
    )


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a selective, authoritative project snapshot for ChatGPT."
    )
    parser.add_argument(
        "--domain",
        action="append",
        default=[],
        help="Include a domain (e.g. writer). May be specified multiple times.",
    )
    parser.add_argument(
        "--app",
        action="append",
        default=[],
        help="Include an app (e.g. document_writer). May be specified multiple times.",
    )

    args = parser.parse_args()
    build_snapshot(domains=args.domain, apps=args.app)


if __name__ == "__main__":
    main()
