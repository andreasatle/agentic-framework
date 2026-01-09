from agentic_framework.agent_dispatcher import AgentDispatcher
from agentic_framework.analysis_controller import (
    AnalysisControllerRequest,
    run_analysis_controller,
)
from document_writer.domain.document.schemas import DocumentPlannerInput
from document_writer.domain.intent.types import IntentEnvelope
from dataclasses import dataclass
from typing import Any


@dataclass
class DocumentAnalysisResult:
    """Domain-owned wrapper adding intent observability; behavior is unchanged and delegated."""

    controller_response: Any
    intent_observation: str

    def __getattr__(self, item: str) -> Any:
        return getattr(self.controller_response, item)


def analyze(
    *,
    intent: IntentEnvelope,
    dispatcher: AgentDispatcher,
):
    intent_observation = "intent_advisory_available"

    planner_input = DocumentPlannerInput(
        intent=intent,
    )
    controller_input = AnalysisControllerRequest(planner_input=planner_input)
    controller_response = run_analysis_controller(
        controller_input,
        dispatcher=dispatcher,
    )
    return DocumentAnalysisResult(
        controller_response=controller_response,
        intent_observation=intent_observation,
    )
