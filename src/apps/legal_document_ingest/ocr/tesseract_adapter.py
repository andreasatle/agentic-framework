# apps/legal_document_ingest/ocr/tesseract_adapter.py

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import subprocess
import tempfile
import shutil
import csv
import io

from apps.legal_document_ingest.ocr.base import OcrAdapter
from apps.legal_document_ingest.ocr.models import (
    EvidenceBundle,
    EvidenceSource,
    OcrRun,
    OcrPage,
    OcrToken,
    BBox,
)


class TesseractAdapter(OcrAdapter):
    engine = "tesseract"

    def run(self, pdf_path: Path) -> EvidenceBundle:
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        document_id = self._hash_file(pdf_path)
        pages: list[OcrPage] = []
        raw_artifacts: list[bytes] = []
        created_at = datetime.now(timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            images = self._render_pdf(pdf_path, out_dir)

            for page_num, img_path in enumerate(images, start=1):
                page_tokens, raw_artifact, width_px, height_px = self._ocr_page(img_path)
                raw_artifacts.append(raw_artifact)
                pages.append(
                    OcrPage(
                        page_number=page_num,
                        width_px=width_px,
                        height_px=height_px,
                        resolution_dpi=300,
                        tokens=page_tokens,
                        blocks=None,
                    )
                )

        return EvidenceBundle(
            document_id=document_id,
            source=EvidenceSource(
                path=str(pdf_path),
                sha256=document_id,
                page_count=len(images),
            ),
            ocr_runs=[
                OcrRun(
                    engine=self.engine,
                    engine_version="unknown",
                    run_id=f"{document_id}:tesseract",
                    parameters={
                        "lang": "eng",
                        "output_format": "tsv",
                    },
                    pages=pages,
                    raw_artifact=b"".join(raw_artifacts),
                    created_at=created_at,
                )
            ],
            created_at=created_at,
        )

    def _ocr_page(self, img_path: Path) -> tuple[list[OcrToken], bytes, int, int]:
        proc = subprocess.run(
            ["tesseract", str(img_path), "stdout", "-l", "eng", "tsv"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))

        raw_artifact = proc.stdout
        tsv = raw_artifact.decode("utf-8", errors="surrogateescape")
        reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")

        tokens: list[OcrToken] = []
        max_x = 0
        max_y = 0

        for row in reader:
            left = _safe_int(row.get("left", "0"))
            top = _safe_int(row.get("top", "0"))
            width = _safe_int(row.get("width", "0"))
            height = _safe_int(row.get("height", "0"))
            max_x = max(max_x, left + width)
            max_y = max(max_y, top + height)

            level = _safe_int(row.get("level", "0"))
            if level != 5:
                continue

            page_num = _safe_int(row.get("page_num", "0"))
            block_num = _safe_int(row.get("block_num", "0"))
            par_num = _safe_int(row.get("par_num", "0"))
            line_num = _safe_int(row.get("line_num", "0"))
            word_num = _safe_int(row.get("word_num", "0"))
            conf_raw = row.get("conf", "")

            if conf_raw == "" or conf_raw == "-1":
                conf = None
            else:
                try:
                    conf = float(conf_raw)
                except ValueError:
                    conf = None

            tokens.append(
                OcrToken(
                    token_id=f"p{page_num}-b{block_num}-l{line_num}-w{word_num}",
                    text=row.get("text", ""),
                    bbox=BBox(
                        x0=float(left),
                        y0=float(top),
                        x1=float(left + width),
                        y1=float(top + height),
                    ),
                    confidence=conf,
                    level="word",
                    engine_metadata={
                        "page_num": page_num,
                        "block_num": block_num,
                        "par_num": par_num,
                        "line_num": line_num,
                        "word_num": word_num,
                        "tsv_level": level,
                    },
                )
            )

        return tokens, raw_artifact, max_x, max_y

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

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


def _safe_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
