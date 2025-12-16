from agentic.supervisor import SupervisorDomainInput, SupervisorRequest, run_supervisor
from agentic.tool_registry import ToolRegistry
from agentic.agent_dispatcher import AgentDispatcher
from domain.sentiment.types import SentimentTask


def run(
    task: SentimentTask,
    *,
    dispatcher: AgentDispatcher,
    tool_registry: ToolRegistry,
):
    supervisor_input = SupervisorRequest(
        domain=SupervisorDomainInput(
            task=task,
        ),
    )
    return run_supervisor(
        supervisor_input,
        dispatcher=dispatcher,
        tool_registry=tool_registry,
    )
