# apps/legal_document_ingest/ocr/textract_adapter.py

from pathlib import Path
import hashlib

import boto3

from apps.legal_document_ingest.ocr.base import OcrAdapter
from apps.legal_document_ingest.ocr.models import EvidenceBundle


class TextractAdapter(OcrAdapter):
    engine = "textract"

    def __init__(
        self,
        *,
        s3_bucket: str,
        s3_prefix: str = "textract-input",
        region_name: str | None = None,
        poll_interval_seconds: int = 5,
    ):
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.poll_interval_seconds = poll_interval_seconds

        self.s3 = boto3.client("s3", region_name=region_name)
        self.textract = boto3.client("textract", region_name=region_name)

    def run(self, pdf_path: Path) -> EvidenceBundle:
        raise NotImplementedError(
            "Textract is disabled for Evidence v1; use Tesseract-only ingestion."
        )

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
