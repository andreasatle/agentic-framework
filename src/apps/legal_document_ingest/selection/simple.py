from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from apps.legal_document_ingest.scoring.heuristic import ScoredSpan


class SelectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    selected: ScoredSpan | None
    reason: str | None = None
    failure_reason: str | None = None


def select_span(spans: list[ScoredSpan]) -> SelectionResult:
    valid_spans = [span for span in spans if span.validated.is_valid]
    if not valid_spans:
        return SelectionResult(selected=None, failure_reason="NO_VALID_SPANS")

    max_score = max(span.score for span in valid_spans)
    top_spans = [span for span in valid_spans if span.score == max_score]

    if max_score < 0.60:
        return SelectionResult(selected=None, failure_reason="SCORE_TOO_LOW")

    if len(top_spans) != 1:
        return SelectionResult(selected=None, failure_reason="AMBIGUOUS_TOP_SCORE")

    return SelectionResult(selected=top_spans[0], reason="SINGLE_TOP_SCORE")
