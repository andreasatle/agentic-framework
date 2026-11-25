"""A tutorial's Markdown for download, from the swarm's document.md: its footnotes made plain, since many
Markdown viewers (VS Code's preview among them) don't know footnotes and showed "[^1]" and one run-on paragraph
of references. Citations become "[1]", a run of them "[1, 2]", and the footnote entries a numbered list. Only
the form changes: the text is the swarm's, word for word.

    uv run python scripts/tutorial-markdown.py <document.md> <out.md>
"""

import re
import sys
from pathlib import Path

RUN = re.compile(r"(?:\[\^(\d+)\])+")
ENTRY = re.compile(r"^\[\^(\d+)\]:\s*(.*)$")


def portable(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        entry = ENTRY.match(line)
        if entry:
            lines.append(f"{entry.group(1)}. {entry.group(2)}")
            continue
        lines.append(RUN.sub(lambda m: "[" + ", ".join(re.findall(r"\d+", m.group(0))) + "]", line))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    source, out = (Path(p) for p in sys.argv[1:3])
    out.write_text(portable(source.read_text()))
