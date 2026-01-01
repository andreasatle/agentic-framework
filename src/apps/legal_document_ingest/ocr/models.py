# apps/legal_document_ingest/ocr/models.py

from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class OcrWord(BaseModel):
    text: str
    confidence: float | None
    bbox: dict  # {x, y, w, h} in image pixel space
    line_num: int | None
    block_num: int | None
    word_num: int | None


class PageEvidence(BaseModel):
    page_number: int
    words: list[OcrWord]
    image: str  # rendered page image filename


class OcrEvidence(BaseModel):
    engine: Literal["textract", "tesseract"]
    raw: dict            # verbatim-ish structured OCR output
    pages: list[PageEvidence]
    metadata: dict       # provenance only
