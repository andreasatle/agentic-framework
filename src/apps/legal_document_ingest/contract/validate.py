from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from apps.legal_document_ingest.output.final import FinalLegalDescription
from apps.legal_document_ingest.output.trace import ExtractionTrace
from apps.legal_document_ingest.uncertainty.gate import ExtractionFailure


class ContractValidationPass(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    status: Literal["PASS"]
    final_description: FinalLegalDescription
    trace: ExtractionTrace


class ContractValidationFailure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    status: Literal["FAIL"]
    final_description: None = None
    trace: None = None
    reason: str


ContractValidationResult = ContractValidationPass | ContractValidationFailure


def _fail(reason: str) -> ContractValidationFailure:
    return ContractValidationFailure(
        status="FAIL",
        final_description=None,
        trace=None,
        reason=reason,
    )


def _validate_corrections(trace: ExtractionTrace) -> None:
    allowed = {"SYMBOL_REPAIR", "HYPHENATION_REPAIR", "LEXICON_FIX"}
    for r in trace.corrections:
        if r.type not in allowed:
            raise ValueError("INVALID_CORRECTION_TYPE")
        if not r.token_ids:
            raise ValueError("MISSING_CORRECTION_TOKENS")


def _validate_uncertainties(trace: ExtractionTrace) -> None:
    for r in trace.uncertainties:
        if not r.token_ids:
            raise ValueError("MISSING_UNCERTAINTY_TOKENS")

def validate_v1_contract(
    *,
    final_description: FinalLegalDescription | None,
    trace: ExtractionTrace | None,
    failure: ExtractionFailure | None,
) -> ContractValidationResult:

    match (final_description, trace, failure):

        # ── invalid combinations
        case (None, None, None):
            return _fail("INVALID_OUTCOME_COMBINATION")

        case (fd, _, f) if fd is not None and f is not None:
            return _fail("INVALID_OUTCOME_COMBINATION")

        # ── PASS shape violations
        case (fd, None, None):
            return _fail("MISSING_TRACE")

        case (fd, tr, None) if not fd.text:
            return _fail("EMPTY_FINAL_TEXT")

        case (fd, tr, None) if not tr.selected_span_token_ids:
            return _fail("MISSING_SELECTED_SPAN_TOKENS")

        case (fd, tr, None) if tr.uncertainties:
            return _fail("UNCERTAINTIES_PRESENT")

        # ── PASS structural OK → deep validation
        case (fd, tr, None):
            _validate_corrections(tr)
            _validate_uncertainties(tr)
            return ContractValidationPass(
                status="PASS",
                final_description=fd,
                trace=tr,
            )

        # ── FAIL shape
        case (None, None, f) if f.status != "FAIL":
            return _fail("INVALID_FAILURE_STATUS")

        case (None, None, f) if not f.reason:
            return _fail("EMPTY_FAILURE_REASON")

        case (None, None, f) if f.uncertainties is None:
            return _fail("MISSING_FAILURE_UNCERTAINTIES")

        case (None, None, f):
            return _fail(f.reason)

        case _:
            return _fail("INVALID_OUTCOME_COMBINATION")
