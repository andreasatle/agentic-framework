from agentic.agent_dispatcher import AgentDispatcher
from agentic.analysis_supervisor import (
    AnalysisSupervisorRequest,
    run_analysis_supervisor,
)
from domain.document.schemas import DocumentPlannerInput
from domain.document.types import DocumentState


def analyze(
    *,
    document_state: DocumentState | None,
    tone: str | None,
    audience: str | None,
    goal: str | None,
    dispatcher: AgentDispatcher,
):
    planner_input = DocumentPlannerInput(
        document_state=document_state,
        tone=tone,
        audience=audience,
        goal=goal,
    )
    supervisor_input = AnalysisSupervisorRequest(task=planner_input)
    return run_analysis_supervisor(
        supervisor_input,
        dispatcher=dispatcher,
    )
