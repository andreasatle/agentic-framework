"""Tutorials and guides written by AgentSwarm, listed on the Writing page (/blog).

They are static pages under static/agentswarm/ (the blog renders posts without math, and these are full of
it), listed newest first in tutorials.json beside this file: AgentSwarm's `publish` step adds its entry there.
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
