from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from apps.legal_document_ingest.scoring.heuristic import ScoredSpan
from apps.legal_document_ingest.selection.simple import SelectionResult


class SelectionAudit(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    all_scored_spans: list[ScoredSpan]
    selection_result: SelectionResult
    decision_rule: str


def build_selection_audit(
    spans: list[ScoredSpan],
    result: SelectionResult,
) -> SelectionAudit:
    decision_rule = result.failure_reason or result.reason
    if decision_rule not in {
        "NO_VALID_SPANS",
        "SCORE_TOO_LOW",
        "AMBIGUOUS_TOP_SCORE",
        "SINGLE_TOP_SCORE",
    }:
        raise ValueError(f"Invalid decision rule: {decision_rule}")
    return SelectionAudit(
        all_scored_spans=spans,
        selection_result=result,
        decision_rule=decision_rule,
    )
