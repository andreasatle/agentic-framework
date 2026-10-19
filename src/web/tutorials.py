"""Tutorials written by AgentSwarm, listed on the Writing page (/blog).

They are static pages under static/agentswarm/ (the blog renders posts without math, and these are full of
it). Newest first.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tutorial:
    href: str
    title: str
    date: str  # YYYY-MM-DD
    summary: str


TUTORIALS: tuple[Tutorial, ...] = (
    Tutorial(
        href="/static/agentswarm/mech-interp-tutorial.html",
        title="Mechanistic Interpretability of Transformer Language Models",
        date="2026-10-19",
        summary="From superposition and sparse autoencoders to circuits, activation patching and attribution graphs; fact-reviewed.",
    ),
    Tutorial(
        href="/static/agentswarm/test-time-compute-tutorial.html",
        title="Why Thinking Longer Helps an LLM Reason, and Where It Stops",
        date="2026-10-18",
        summary="Search, verification and reinforcement learning for reasoning, from five papers the swarm chose itself.",
    ),
    Tutorial(
        href="/static/agentswarm/jepa-tutorial.html",
        title="From Energy-Based Learning to V-JEPA 2.1",
        date="2026-10-18",
        summary="How joint-embedding predictive architectures developed, from five papers, fact-reviewed.",
    ),
)
