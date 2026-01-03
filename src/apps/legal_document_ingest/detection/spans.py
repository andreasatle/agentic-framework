from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from apps.legal_document_ingest.detection.anchors import AnchorRecord
from apps.legal_document_ingest.ocr.models import EvidenceBundle, OcrToken


class CandidateSpan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    anchor: AnchorRecord
    start_token_id: str
    end_token_id: str
    token_ids: list[str]
    page_start: int
    page_end: int


@dataclass(frozen=True)
class _PageStats:
    median_token_height: float
    median_char_width: float


def expand_candidate_spans(
    bundle: EvidenceBundle,
    ordered_token_ids: list[str],
    anchors: list[AnchorRecord],
) -> list[CandidateSpan]:
    token_index, page_stats = _index_tokens(bundle)
    ordered_index = {token_id: idx for idx, token_id in enumerate(ordered_token_ids)}
    anchor_starts = {anchor.token_ids[0] for anchor in anchors if anchor.token_ids}

    spans: list[CandidateSpan] = []

    for anchor in anchors:
        if not anchor.token_ids:
            continue
        last_anchor_id = anchor.token_ids[-1]
        if last_anchor_id not in ordered_index:
            raise KeyError(f"Anchor token id not found in ordered list: {last_anchor_id}")
        anchor_entry = token_index.get(last_anchor_id)
        if anchor_entry is None:
            raise KeyError(f"Anchor token id not found in EvidenceBundle: {last_anchor_id}")
        _, anchor_page = anchor_entry

        start_idx = ordered_index[last_anchor_id] + 1
        if start_idx >= len(ordered_token_ids):
            continue

        span_token_ids: list[str] = []
        window: deque[bool] = deque()

        pending: list[OcrToken] = []
        pending_page: int | None = None
        pending_t0_y0: float | None = None
        pending_prev: OcrToken | None = None

        last_page_seen = anchor_page
        stop_without_pending = False

        i = start_idx
        while i < len(ordered_token_ids):
            token_id = ordered_token_ids[i]
            if token_id in anchor_starts:
                stop_without_pending = True
                break

            entry = token_index.get(token_id)
            if entry is None:
                raise KeyError(f"Token id not found in EvidenceBundle: {token_id}")
            token, page_number = entry

            if page_number < last_page_seen:
                stop_without_pending = True
                break
            last_page_seen = page_number

            if page_number > anchor_page + 3:
                stop_without_pending = True
                break

            if _is_heading_candidate(token):
                stats = page_stats.get(page_number)
                if stats is None:
                    if not _flush_pending(pending, span_token_ids, window):
                        break
                    pending = []
                    pending_page = None
                    pending_t0_y0 = None
                    pending_prev = None
                    if not _append_with_confidence_check(span_token_ids, token, window):
                        break
                    i += 1
                    continue
                if pending and pending_page != page_number:
                    if not _flush_pending(pending, span_token_ids, window):
                        break
                    pending = []
                    pending_page = None
                    pending_t0_y0 = None
                    pending_prev = None

                if not pending:
                    pending = [token]
                    pending_page = page_number
                    pending_t0_y0 = token.bbox.y0
                    pending_prev = token
                    i += 1
                    continue

                vertical_tol = max(3.0, 0.25 * stats.median_token_height)
                horizontal_tol = max(1.5 * stats.median_char_width, 15.0)

                if (
                    pending_t0_y0 is not None
                    and pending_prev is not None
                    and abs(token.bbox.y0 - pending_t0_y0) <= vertical_tol
                    and (token.bbox.x0 - pending_prev.bbox.x1) <= horizontal_tol
                ):
                    pending.append(token)
                    pending_prev = token
                    if len(pending) >= 2:
                        stop_without_pending = True
                        break
                    i += 1
                    continue

                if not _flush_pending(pending, span_token_ids, window):
                    break
                pending = [token]
                pending_page = page_number
                pending_t0_y0 = token.bbox.y0
                pending_prev = token
                i += 1
                continue

            if not _flush_pending(pending, span_token_ids, window):
                break
            pending = []
            pending_page = None
            pending_t0_y0 = None
            pending_prev = None

            if not _append_with_confidence_check(span_token_ids, token, window):
                break

            i += 1

        if pending:
            if not stop_without_pending:
                _flush_pending(pending, span_token_ids, window)

        if span_token_ids:
            start_token_id = span_token_ids[0]
            end_token_id = span_token_ids[-1]
            start_entry = token_index[start_token_id]
            end_entry = token_index[end_token_id]
            spans.append(
                CandidateSpan(
                    anchor=anchor,
                    start_token_id=start_token_id,
                    end_token_id=end_token_id,
                    token_ids=span_token_ids,
                    page_start=start_entry[1],
                    page_end=end_entry[1],
                )
            )

    return spans


def _index_tokens(
    bundle: EvidenceBundle,
) -> tuple[dict[str, tuple[OcrToken, int]], dict[int, _PageStats]]:
    token_index: dict[str, tuple[OcrToken, int]] = {}
    page_heights: dict[int, list[float]] = {}
    page_char_widths: dict[int, list[float]] = {}

    for run in bundle.ocr_runs:
        for page in run.pages:
            for token in page.tokens:
                token_index[token.token_id] = (token, page.page_number)
                if token.level != "word":
                    continue
                height = float(token.bbox.y1 - token.bbox.y0)
                page_heights.setdefault(page.page_number, []).append(height)
                if token.text:
                    width = float(token.bbox.x1 - token.bbox.x0)
                    page_char_widths.setdefault(page.page_number, []).append(
                        width / max(len(token.text), 1)
                    )

    page_stats: dict[int, _PageStats] = {}
    for page_number, heights in page_heights.items():
        median_height = float(statistics.median(heights)) if heights else 0.0
        widths = page_char_widths.get(page_number, [])
        median_width = float(statistics.median(widths)) if widths else 0.0
        page_stats[page_number] = _PageStats(
            median_token_height=median_height,
            median_char_width=median_width,
        )

    return token_index, page_stats


def _is_heading_candidate(token: OcrToken) -> bool:
    return token.level == "word" and token.text.strip() != "" and token.text.isupper()


def _append_with_confidence_check(
    span_token_ids: list[str],
    token: OcrToken,
    window: deque[bool],
) -> bool:
    window.append(token.confidence is None)
    if len(window) > 20:
        window.popleft()
    if len(window) == 20 and (sum(1 for value in window if value) / len(window)) > 0.3:
        return False
    span_token_ids.append(token.token_id)
    return True


def _flush_pending(
    pending: list[OcrToken],
    span_token_ids: list[str],
    window: deque[bool],
) -> bool:
    for token in pending:
        if not _append_with_confidence_check(span_token_ids, token, window):
            return False
    return True
