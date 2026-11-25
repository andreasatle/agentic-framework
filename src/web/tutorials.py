"""Tutorials and guides written by AgentSwarm, and essays written for the project, listed on the Writing page
(/blog).

They are static pages under static/agentswarm/ (the blog renders posts without math, and these are full of
it), listed newest first in tutorials.json beside this file; essays (written by Claude for the project, not by the
swarm) are listed the same way in essays.json. They are added by hand: AgentSwarm never
writes to this repository.
"""

import json
from dataclasses import dataclass
from pathlib import Path


STATIC = Path(__file__).with_name("static")


@dataclass(frozen=True)
class Tutorial:
    href: str
    title: str
    date: str  # YYYY-MM-DD
    summary: str

    def beside(self, suffix: str) -> str | None:
        """The page's download in another format (its PDF, its Markdown), when the file is beside the page.
        PDFs are printed by scripts/tutorial-pdfs.sh; the Markdown is the swarm's document, copied as it is."""
        href = self.href.removesuffix(".html") + suffix
        return href if (STATIC / href.removeprefix("/static/")).is_file() else None

    @property
    def pdf(self) -> str | None:
        return self.beside(".pdf")

    @property
    def markdown(self) -> str | None:
        return self.beside(".md")


LISTING = Path(__file__).with_name("tutorials.json")
TUTORIALS: tuple[Tutorial, ...] = tuple(Tutorial(**entry) for entry in json.loads(LISTING.read_text()))
ESSAYS: tuple[Tutorial, ...] = tuple(
    Tutorial(**entry) for entry in json.loads(LISTING.with_name("essays.json").read_text())
)
