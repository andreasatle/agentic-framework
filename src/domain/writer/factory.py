from agentic.tool_registry import ToolRegistry
from domain.writer.dispatcher import WriterDispatcher
from domain.writer.planner import make_planner
from domain.writer.worker import make_worker
from domain.writer.critic import make_critic


def make_agent_dispatcher(
    model: str = "gpt-4.1-mini",
    max_retries: int = 3,
) -> WriterDispatcher:
    planner = make_planner(model=model)
    worker = make_worker(model=model)
    critic = make_critic(model=model)
    return WriterDispatcher(
        max_retries=max_retries,
        planner=planner,
        workers={"writer-worker": worker},
        critic=critic,
    )


def make_tool_registry() -> ToolRegistry:
    # Writer domain uses no tools in the MVP.
    return ToolRegistry()
