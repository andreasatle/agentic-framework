# apps/legal_document_ingest/ocr/textract_adapter.py

from pathlib import Path
from datetime import datetime
import time
import hashlib

import boto3

from apps.legal_document_ingest.ocr.base import OcrAdapter
from apps.legal_document_ingest.ocr.models import OcrEvidence


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

    def run(self, pdf_path: Path) -> OcrEvidence:
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        document_id = self._hash_file(pdf_path)
        s3_key = f"{self.s3_prefix}/{document_id}.pdf"

        # 1. Upload to S3
        self.s3.upload_file(
            Filename=str(pdf_path),
            Bucket=self.s3_bucket,
            Key=s3_key,
        )

        # 2. Start Textract job
        response = self.textract.start_document_analysis(
            DocumentLocation={
                "S3Object": {
                    "Bucket": self.s3_bucket,
                    "Name": s3_key,
                }
            },
            FeatureTypes=["TABLES", "FORMS"],
        )

        job_id = response["JobId"]

        # 3. Poll until completion
        pages: list[dict] = []
        next_token: str | None = None

        while True:
            kwargs = {"JobId": job_id}
            if next_token:
                kwargs["NextToken"] = next_token

            result = self.textract.get_document_analysis(**kwargs)

            status = result["JobStatus"]
            if status == "FAILED":
                raise RuntimeError(f"Textract job failed: {result}")

            if status == "SUCCEEDED":
                pages.append(result)

                next_token = result.get("NextToken")
                if not next_token:
                    break
            else:
                time.sleep(self.poll_interval_seconds)

        # 4. Optional convenience text extraction
        text = self._extract_text(pages)

        return OcrEvidence(
            engine="textract",
            raw={
                "job_id": job_id,
                "pages": pages,
            },
            text=text,
            confidence=None,  # Textract does not provide doc-level confidence
            metadata={
                "s3_bucket": self.s3_bucket,
                "s3_key": s3_key,
                "feature_types": ["TABLES", "FORMS"],
                "created_at": datetime.utcnow().isoformat(),
            },
        )

    @staticmethod
    def _extract_text(pages: list[dict]) -> str:
        """Best-effort linearized text. NOT canonical."""
        lines: list[str] = []
        for page in pages:
            for block in page.get("Blocks", []):
                if block.get("BlockType") == "LINE":
                    text = block.get("Text")
                    if text:
                        lines.append(text)
        return "\n".join(lines)

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
