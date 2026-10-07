"""Project registry for the public site.

One entry per project page under /work/<slug>. The template for each page is
templates/work/<slug>.html; the fields here feed the cards on / and /work.
Order here is display order.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    summary: str
    period: str
    status: str  # "active" | "complete" | "paused" | "archived"
    tags: tuple[str, ...] = field(default_factory=tuple)
    stat: str = ""
    stat_label: str = ""
    media: str = ""  # "video:<path>", "img:<path>", "canvas:<viz>", or ""
    poster: str = ""
    featured: bool = True


PROJECTS: tuple[Project, ...] = (
    Project(
        slug="agentswarm",
        title="AgentSwarm: teams of small agents, gated by a calibrated judge",
        summary=(
            "Independent teams of agents (executor, tester, red team, planner) move "
            "work up maturity levels on git branches, through gates. Teams never call "
            "each other, so nothing can deadlock. Language models produce, a calibrated "
            "judge decides, plain code controls."
        ),
        period="Oct 2026 – now",
        status="active",
        tags=("agents", "blackboard", "calibration", "LangChain", "Pydantic"),
        stat="0 / 16",
        stat_label="false promotions by the active gate, held-out tasks",
        media="html:swarm",
    ),
    Project(
        slug="jepa-ball-in-cup",
        title="Planning through a learned world model",
        summary=(
            "A JEPA world model trained from pixels on dm_control's ball-in-cup, "
            "driven by a CEM/MPC planner. Built from scratch to learn the whole "
            "loop: self-supervised pretraining, probing what the latent actually "
            "knows, and planning through it."
        ),
        period="Aug – Sep 2026",
        status="complete",
        tags=("JEPA", "world models", "CEM / MPC", "PyTorch"),
        stat="60% → 97%",
        stat_label="task success, random starts (n=30)",
        media="video:/static/img/work/ball-in-cup-solve.mp4",
        poster="/static/img/work/ball-in-cup-poster.jpg",
    ),
    Project(
        slug="hyperbolic-jepa",
        title="Hyperbolic latents for branching futures",
        summary=(
            "Does hyperbolic geometry help a predictor represent futures that fork? "
            "Tested on a grid maze against an identical Euclidean baseline. "
            "Answer so far: yes at low latent dimension, and it reverses at high dimension."
        ),
        period="Sep 2026 – now",
        status="active",
        tags=("JEPA", "hyperbolic geometry", "Poincaré ball", "research"),
        stat="41–55 / 70",
        stat_label="maze junctions favour hyperbolic at dim 8",
        media="canvas:maze",
    ),
    Project(
        slug="title-ocr",
        title="Multi-engine OCR for title documents",
        summary=(
            "Verbatim text from scanned deeds, mortgages and plats. LLM vision for "
            "prose and layout, pixel OCR for numbers, and a reconcile step checked "
            "by domain verifiers."
        ),
        period="Sep 2026 – now",
        status="active",
        tags=("OCR", "Claude / GPT vision", "Tesseract", "Textract"),
        stat="4 engines",
        stat_label="reconciled per page",
        media="html:ocr",
    ),
    Project(
        slug="i-jepa-pathology",
        title="I-JEPA on histology images",
        summary=(
            "Image JEPA (ViT, block masking) pretrained on PathMNIST at 224px on a "
            "24 GB Mac, then frozen-feature probes against a random-init encoder "
            "to measure what self-supervision actually buys."
        ),
        period="Sep 2026",
        status="paused",
        tags=("I-JEPA", "ViT", "self-supervised", "medical imaging"),
        stat="78.6%",
        stat_label="best linear probe (random-init encoder: 74.3%)",
        media="img:/static/img/work/ijepa-masks.jpg",
    ),
    Project(
        slug="governed-agents",
        title="Governed agent systems",
        summary=(
            "Years of building LLM agents that can be audited: typed state, "
            "planner–worker–critic loops, adversarial review. What worked, what "
            "didn't, and what carried over."
        ),
        period="2021 – 2026",
        status="archived",
        tags=("agents", "state machines", "Pydantic", "Rust"),
        stat="",
        stat_label="",
        media="html:fsm",
        featured=False,
    ),
)


def get_project(slug: str) -> Project | None:
    return next((p for p in PROJECTS if p.slug == slug), None)
