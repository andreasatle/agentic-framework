from __future__ import annotations

from apps.legal_document_ingest.ocr.models import EvidenceBundle, OcrToken


def token_filter_view(bundle: EvidenceBundle) -> list[OcrToken]:
    tokens: list[OcrToken] = []
    for run in bundle.ocr_runs:
        for page in run.pages:
            for token in page.tokens:
                if token.level == "word" and token.confidence is not None:
                    tokens.append(token)
    return tokens


def spatial_ordered_token_ids(bundle: EvidenceBundle) -> list[str]:
    ordered: list[tuple[int, float, float, int, str]] = []
    seq = 0
    for run in bundle.ocr_runs:
        for page in run.pages:
            for token in page.tokens:
                if token.level == "word" and token.confidence is not None:
                    ordered.append(
                        (
                            page.page_number,
                            token.bbox.y0,
                            token.bbox.x0,
                            seq,
                            token.token_id,
                        )
                    )
                    seq += 1
    ordered.sort(key=lambda item: (item[0], item[1], item[2], item[3]))
    return [item[4] for item in ordered]
