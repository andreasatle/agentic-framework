from pathlib import Path

from apps.legal_document_ingest.pipeline.v1 import run_extraction_v1
from apps.legal_document_ingest.ocr.tesseract_adapter import TesseractAdapter


PASS_PDF = Path("tests/fixtures/pass_clean_legal_description.pdf")
FAIL_PDF = Path("tests/fixtures/fail_conflicting_bearings.pdf")


def run_extraction(pdf_path: Path):
    adapter = TesseractAdapter()
    bundle = adapter.run(pdf_path)
    return run_extraction_v1(bundle)


# ─────────────────────────────────────────────
# I-1 / I-10 — Outcome exclusivity
# ─────────────────────────────────────────────

def test_pass_outcome():
    result = run_extraction(PASS_PDF)
    assert result.status == "PASS"


def test_fail_outcome():
    result = run_extraction(FAIL_PDF)
    assert result.status == "FAIL"


# ─────────────────────────────────────────────
# I-10 — FAIL has no output
# ─────────────────────────────────────────────

def test_fail_has_no_output():
    result = run_extraction(FAIL_PDF)
    assert result.final_description is None
    assert result.trace is None
    assert isinstance(result.reason, str)
    assert result.reason


# ─────────────────────────────────────────────
# I-3 / I-5 — PASS output shape and cleanliness
# ─────────────────────────────────────────────

def test_pass_has_output():
    result = run_extraction(PASS_PDF)
    assert result.final_description is not None
    assert result.trace is not None
    assert result.reason is None


def test_pass_text_is_clean():
    text = run_extraction(PASS_PDF).final_description.text
    assert text.strip()
    assert "[" not in text
    assert "?" not in text
    assert "(?)" not in text
    assert "sic" not in text.lower()


# ─────────────────────────────────────────────
# I-4 — Uncertainty handling
# ─────────────────────────────────────────────

def test_pass_has_empty_uncertainties():
    result = run_extraction(PASS_PDF)
    assert result.trace.uncertainties == []


# ─────────────────────────────────────────────
# I-5 — Text fidelity (bearings preserved)
# ─────────────────────────────────────────────

def test_bearing_symbols_preserved():
    text = run_extraction(PASS_PDF).final_description.text
    assert "°" in text
    assert "'" in text or "′" in text
    assert '"' in text or "″" in text


# ─────────────────────────────────────────────
# I-9 — Determinism
# ─────────────────────────────────────────────

def test_pass_determinism():
    a = run_extraction(PASS_PDF).model_dump()
    b = run_extraction(PASS_PDF).model_dump()
    assert a == b


def test_fail_determinism():
    a = run_extraction(FAIL_PDF).model_dump()
    b = run_extraction(FAIL_PDF).model_dump()
    assert a == b


# ─────────────────────────────────────────────
# I-8 — Evidence preservation
# ─────────────────────────────────────────────

def test_ocr_evidence_is_preserved():
    adapter = TesseractAdapter()
    bundle = adapter.run(PASS_PDF)

    assert len(bundle.ocr_runs) >= 1
    assert bundle.ocr_runs[0].text is not None
