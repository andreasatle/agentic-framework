from agentic.agent_dispatcher import AgentDispatcher
from agentic.analysis_controller import (
    AnalysisControllerRequest,
    run_analysis_controller,
)
from domain.document.schemas import DocumentPlannerInput
from domain.document.types import DocumentTree


def analyze(
    *,
    document_tree: DocumentTree | None,
    tone: str | None,
    audience: str | None,
    goal: str | None,
    dispatcher: AgentDispatcher,
):
    planner_input = DocumentPlannerInput(
        document_tree=document_tree,
        tone=tone,
        audience=audience,
        goal=goal,
    )
    controller_input = AnalysisControllerRequest(planner_input=planner_input)
    return run_analysis_controller(
        controller_input,
        dispatcher=dispatcher,
    )
