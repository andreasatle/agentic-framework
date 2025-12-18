from agentic.controller import ControllerDomainInput, ControllerRequest, run_controller
from agentic.tool_registry import ToolRegistry
from agentic.agent_dispatcher import AgentDispatcher
from domain.writer.types import DraftSectionTask, RefineSectionTask, WriterTask


def run(
    task: WriterTask,
    *,
    dispatcher: AgentDispatcher,
    tool_registry: ToolRegistry,
):
    """Execute exactly one writer task; writer does not manage documents or persistence."""
    if not isinstance(task, (DraftSectionTask, RefineSectionTask)):
        raise TypeError("Writer requires a DraftSectionTask or RefineSectionTask.")
    if not task.section_name:
        raise ValueError("Writer task must include section_name.")
    if not task.requirements:
        raise ValueError("Writer task must include explicit requirements.")

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
