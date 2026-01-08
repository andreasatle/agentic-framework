from agentic_framework.controller import ControllerDomainInput, ControllerRequest, run_controller
from agentic_framework.tool_registry import ToolRegistry
from agentic_framework.agent_dispatcher import AgentDispatcher
from experiments.arithmetic.types import ArithmeticTask


def run(
    task: ArithmeticTask,
    *,
    dispatcher: AgentDispatcher,
    tool_registry: ToolRegistry,
):
    controller_input = ControllerRequest(
        domain=ControllerDomainInput(
            task=task,
        ),
    )
    return run_controller(
        controller_input,
        dispatcher=dispatcher,
        tool_registry=tool_registry,
    )
