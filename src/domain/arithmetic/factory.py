from agentic.tool_registry import ToolRegistry
from domain.arithmetic.types import (
    ArithmeticDispatcher,
    WORKER_CAPABILITIES,
    AddArgs,
    SubArgs,
    MulArgs,
)
from domain.arithmetic.planner import make_planner
from domain.arithmetic.worker import make_worker
from domain.arithmetic.critic import make_critic
from domain.arithmetic.tools import add, sub, mul
def make_agent_dispatcher(
    model: str = "gpt-4.1-mini",
    max_retries: int = 3,
) -> ArithmeticDispatcher:
    planner = make_planner(model=model)
    workers = {worker_id: make_worker(worker_id=worker_id, model=model) for worker_id in WORKER_CAPABILITIES}
    critic = make_critic(model=model)
    return ArithmeticDispatcher(
        max_retries=max_retries,
        planner=planner,
        workers=workers,
        critic=critic,
    )


def make_tool_registry() -> ToolRegistry:
    tool_registry = ToolRegistry()
    tool_registry.register("add", "Deterministic addition tool.", add, AddArgs)
    tool_registry.register("sub", "Deterministic subtraction tool.", sub, SubArgs)
    tool_registry.register("mul", "Deterministic multiplication tool.", mul, MulArgs)
    return tool_registry
