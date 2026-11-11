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


@dataclass(frozen=True)
class Tutorial:
    href: str
    title: str
    date: str  # YYYY-MM-DD
    summary: str


LISTING = Path(__file__).with_name("tutorials.json")
TUTORIALS: tuple[Tutorial, ...] = tuple(Tutorial(**entry) for entry in json.loads(LISTING.read_text()))
ESSAYS: tuple[Tutorial, ...] = tuple(
    Tutorial(**entry) for entry in json.loads(LISTING.with_name("essays.json").read_text())
)
