from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from apps.legal_document_ingest.reconstruction.lines import ReconstructedLine
from apps.legal_document_ingest.reconstruction.corrections import (
    CorrectedLine,
    CorrectionRecord,
)
from apps.legal_document_ingest.selection.audit import SelectionAudit
from apps.legal_document_ingest.uncertainty.detect import UncertaintyRecord


class ExtractionTrace(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    selected_span_token_ids: list[str]
    reconstructed_lines: list[ReconstructedLine]
    corrected_lines: list[CorrectedLine]
    corrections: list[CorrectionRecord]
    uncertainties: list[UncertaintyRecord]
    selection_audit: SelectionAudit


def build_extraction_trace(
    audit: SelectionAudit,
    reconstructed_lines: list[ReconstructedLine],
    corrected_lines: list[CorrectedLine],
    uncertainties: list[UncertaintyRecord],
) -> ExtractionTrace:
    selected_span_token_ids: list[str] = []
    if audit.selection_result.selected is not None:
        selected_span_token_ids = list(
            audit.selection_result.selected.validated.span.token_ids
        )

    corrections: list[CorrectionRecord] = []
    for line in corrected_lines:
        corrections.extend(line.corrections)

    return ExtractionTrace(
        selected_span_token_ids=selected_span_token_ids,
        reconstructed_lines=reconstructed_lines,
        corrected_lines=corrected_lines,
        corrections=corrections,
        uncertainties=uncertainties,
        selection_audit=audit,
    )
