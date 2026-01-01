from abc import ABC, abstractmethod
from pathlib import Path
from apps.legal_document_ingest.ocr.models import OcrEvidence

class OcrAdapter(ABC):
    engine: str

    @abstractmethod
    def run(self, pdf_path: Path) -> OcrEvidence:
        """Run OCR on a full PDF and return verbatim evidence."""
        ...