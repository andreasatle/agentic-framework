# apps/legal_document_ingest/ocr/models.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class EvidenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    path: str
    sha256: str
    page_count: int


class BBox(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    x0: float
    y0: float
    x1: float
    y1: float


class OcrToken(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    token_id: str
    text: str
    bbox: BBox
    confidence: float | None
    level: Literal["symbol", "word", "line"]
    engine_metadata: dict[str, Any]


class OcrBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    block_id: str
    type: Literal["line", "paragraph", "table", "unknown"]
    token_ids: list[str]
    bbox: BBox


class OcrPage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    page_number: int
    width_px: int
    height_px: int
    resolution_dpi: int | None
    tokens: list[OcrToken]
    blocks: list[OcrBlock] | None = None


class OcrRun(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    engine: str
    engine_version: str
    run_id: str
    parameters: dict[str, Any]
    pages: list[OcrPage]
    raw_artifact: bytes | None
    created_at: datetime


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    document_id: str
    source: EvidenceSource
    ocr_runs: list[OcrRun]
    created_at: datetime
