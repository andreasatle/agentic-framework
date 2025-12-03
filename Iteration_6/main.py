from __future__ import annotations

from openai import OpenAI
from dotenv import load_dotenv
from .agents import make_planner, make_worker, make_critic
from .compute import compute
from .supervisor import Supervisor
from .logging_config import get_logger
from .tool_registry import ToolRegistry
from .schemas import Compute

load_dotenv(override=True)
logger = get_logger("agentic.iteration6.main")

registry = ToolRegistry()
registry.register("compute", "A deterministic arithmetic tool.", compute, Compute)

def run_demo(runs: int = 5) -> None:
    client = OpenAI()

    planner = make_planner(client, model="gpt-4.1-mini")
    worker = make_worker(client, model="gpt-4.1-mini")
    critic = make_critic(client, model="gpt-4.1-mini")

    supervisor = Supervisor(
        planner=planner,
        worker=worker,
        critic=critic,
        tool_registry=registry,
        max_retries=3,
        max_loops=5,
    )

    for i in range(1, runs + 1):
        response = supervisor()
        plan = response["plan"]
        result = response["result"]
        decision = response["decision"]
        loops_used = response["loops_used"]

        print(f"Run {i}:")
        print(f"  Plan: {plan.model_dump()}")
        print(f"  Result: {result.model_dump()}")
        print(f"  Decision: {decision.model_dump()}")
        print(f"  Loops used: {loops_used}")
        print("-" * 40)


if __name__ == "__main__":
    run_demo()
