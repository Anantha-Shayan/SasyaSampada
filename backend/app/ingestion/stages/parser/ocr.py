from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class OcrEngine(Protocol):
    name: str

    def extract_text(self, image_bytes: bytes, *, page_number: int) -> str: ...


class NoOpOcrEngine:
    """OCR disabled — scanned pages are flagged with needs_ocr=True."""

    name = "none"

    def extract_text(self, image_bytes: bytes, *, page_number: int) -> str:
        return ""


class TesseractOcrEngine:
    """
    Optional Tesseract backend via pytesseract.

    Requires system tesseract binary and: pip install pytesseract pillow
    Not used unless OCR_ENABLED=true in environment.
    """

    name = "tesseract"

    def extract_text(self, image_bytes: bytes, *, page_number: int) -> str:
        try:
            import pytesseract
            from PIL import Image
            import io
        except ImportError as exc:
            raise RuntimeError(
                "pytesseract and Pillow required for OCR. "
                "Install with: pip install pytesseract pillow"
            ) from exc

        image = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(image) or ""
