# apps/legal_document_ingest/ocr/tesseract_adapter.py

from pathlib import Path
from datetime import datetime, timezone
import subprocess
import tempfile
import shutil
import csv
import io

from apps.legal_document_ingest.ocr.base import OcrAdapter
from apps.legal_document_ingest.ocr.models import OcrEvidence, PageEvidence, OcrWord


class TesseractAdapter(OcrAdapter):
    engine = "tesseract"

    def run(self, pdf_path: Path) -> OcrEvidence:
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        pages: list[PageEvidence] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            images = self._render_pdf(pdf_path, out_dir)

            for page_num, img_path in enumerate(images, start=1):
                words = self._ocr_page(img_path)
                pages.append(
                    PageEvidence(
                        page_number=page_num,
                        image=img_path.name,
                        words=words,
                    )
                )

        return OcrEvidence(
            engine=self.engine,
            raw={
                "renderer": "pdftoppm",
                "ocr_engine": "tesseract",
                "page_count": len(pages),
            },
            pages=pages,
            metadata={
                "source_file": str(pdf_path),
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _ocr_page(self, img_path: Path) -> list[OcrWord]:
        proc = subprocess.run(
            ["tesseract", str(img_path), "stdout", "-l", "eng", "tsv"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))

        tsv = proc.stdout.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")

        words: list[OcrWord] = []

        for row in reader:
            # Tesseract convention: word-level rows have a non-empty "text"
            if not row.get("text"):
                continue

            try:
                words.append(
                    OcrWord(
                        text=row["text"],
                        confidence=float(row["conf"]) if row["conf"] != "-1" else None,
                        bbox={
                            "x": int(row["left"]),
                            "y": int(row["top"]),
                            "w": int(row["width"]),
                            "h": int(row["height"]),
                        },
                        block_num=int(row["block_num"]) if row["block_num"] else None,
                        line_num=int(row["line_num"]) if row["line_num"] else None,
                        word_num=int(row["word_num"]) if row["word_num"] else None,
                    )
                )
            except Exception:
                # Skip malformed rows without failing the page
                continue

        return words

    def _render_pdf(self, pdf_path: Path, out_dir: Path) -> list[Path]:
        if not shutil.which("pdftoppm"):
            raise RuntimeError("pdftoppm not found. Install poppler (brew install poppler).")

        prefix = out_dir / "page"

        subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-r",
                "300",
                "-gray",
                str(pdf_path),
                str(prefix),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        images = sorted(out_dir.glob("page-*.png"))
        if not images:
            raise RuntimeError("No images rendered from PDF")

        return images
