"""Phase 3.1 legal pattern predicates."""

from __future__ import annotations

import re

from apps.legal_document_ingest.ocr.models import OcrToken


def contains_degree_symbol(tokens: list[OcrToken]) -> bool:
    for token in tokens:
        if any(symbol in token.text for symbol in ("°", "º", "′", "″")):
            return True
    return False


def contains_bearing_letter_sequence(tokens: list[OcrToken]) -> bool:
    for i in range(len(tokens)):
        if tokens[i].text not in {"N", "S"}:
            continue
        for j in range(i + 1, len(tokens)):
            if tokens[j].text in {"E", "W"}:
                return True
    return False


def contains_thence_keyword(tokens: list[OcrToken]) -> bool:
    for token in tokens:
        if token.text == "THENCE":
            return True
    return False


def contains_beginning_at_phrase(tokens: list[OcrToken]) -> bool:
    for i in range(len(tokens) - 1):
        if tokens[i].text == "BEGINNING" and tokens[i + 1].text == "AT":
            return True
    return False


def contains_numbered_calls(tokens: list[OcrToken]) -> bool:
    for token in tokens:
        if re.match(r"^\d+\.$", token.text) or re.match(r"^\(\d+\)$", token.text):
            return True
    return False


def has_legal_pattern_signal(tokens: list[OcrToken]) -> bool:
    return (
        contains_degree_symbol(tokens)
        or contains_bearing_letter_sequence(tokens)
        or contains_thence_keyword(tokens)
        or contains_beginning_at_phrase(tokens)
        or contains_numbered_calls(tokens)
    )
