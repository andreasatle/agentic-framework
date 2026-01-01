from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from apps.legal_document_ingest.ocr.models import EvidenceBundle
from apps.legal_document_ingest.validation.structural import ValidatedSpan


class ScoredSpan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    validated: ValidatedSpan
    score: float
    score_breakdown: dict[str, float]


def score_validated_spans(
    bundle: EvidenceBundle,
    spans: list[ValidatedSpan],
) -> list[ScoredSpan]:
    token_index = _index_tokens(bundle)
    scored: list[ScoredSpan] = []

    for validated in spans:
        token_ids = validated.span.token_ids
        length_score = min(1.0, len(token_ids) / 200) if token_ids else 0.0
        confidence_score = _confidence_fraction(token_ids, token_index)
        density_score = (
            0.0
            if "LOW_CONFIDENCE_DENSITY" in validated.validation_failures
            else 1.0
        )
        structural_score = 1.0 if validated.is_valid else 0.0

        breakdown = {
            "LENGTH_SCORE": 0.30 * length_score,
            "CONFIDENCE_SCORE": 0.30 * confidence_score,
            "DENSITY_SCORE": 0.20 * density_score,
            "STRUCTURAL_SCORE": 0.20 * structural_score,
        }
        score = _clamp(sum(breakdown.values()))

        scored.append(
            ScoredSpan(
                validated=validated,
                score=score,
                score_breakdown=breakdown,
            )
        )

    return scored


def _index_tokens(bundle: EvidenceBundle) -> dict[str, float | None]:
    token_index: dict[str, float | None] = {}
    for run in bundle.ocr_runs:
        for page in run.pages:
            for token in page.tokens:
                token_index[token.token_id] = token.confidence
    return token_index


def _confidence_fraction(
    token_ids: list[str], token_index: dict[str, float | None]
) -> float:
    if not token_ids:
        return 0.0
    present = 0
    for token_id in token_ids:
        if token_id not in token_index:
            raise KeyError(f"Token id not found in EvidenceBundle: {token_id}")
        if token_index[token_id] is not None:
            present += 1
    return present / len(token_ids)


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
