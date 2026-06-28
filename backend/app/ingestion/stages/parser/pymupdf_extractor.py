from __future__ import annotations

import pymupdf

from app.ingestion.stages.parser.models import PageLayout, TextBlock


class PyMuPdfExtractor:
    """Extract text blocks, layout metrics, and page images via PyMuPDF."""

    def extract_layouts(self, source_path: str) -> list[PageLayout]:
        layouts: list[PageLayout] = []
        with pymupdf.open(source_path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                layouts.append(self._extract_page(page, page_number))
        return layouts

    def render_page_image(self, source_path: str, page_number: int, dpi: int = 200) -> bytes:
        with pymupdf.open(source_path) as pdf:
            page = pdf[page_number - 1]
            pixmap = page.get_pixmap(dpi=dpi)
            return pixmap.tobytes("png")

    def _extract_page(self, page: pymupdf.Page, page_number: int) -> PageLayout:
        raw_text = page.get_text() or ""
        rect = page.rect
        blocks = self._parse_blocks(page)
        image_coverage = self._image_coverage(page, rect)
        return PageLayout(
            page_number=page_number,
            width=float(rect.width),
            height=float(rect.height),
            blocks=blocks,
            raw_text=raw_text,
            image_coverage=image_coverage,
        )

    def _parse_blocks(self, page: pymupdf.Page) -> list[TextBlock]:
        blocks: list[TextBlock] = []
        block_data = page.get_text("blocks") or []
        for item in block_data:
            if len(item) < 5:
                continue
            x0, y0, x1, y1, text = item[0], item[1], item[2], item[3], item[4]
            cleaned = (text or "").strip()
            if cleaned:
                blocks.append(TextBlock(text=cleaned, x0=x0, y0=y0, x1=x1, y1=y1))
        return blocks

    def _image_coverage(self, page: pymupdf.Page, rect: pymupdf.Rect) -> float:
        page_area = max(float(rect.width * rect.height), 1.0)
        image_area = 0.0
        for image in page.get_images(full=True):
            try:
                bbox = page.get_image_bbox(image)
                image_area += float(bbox.width * bbox.height)
            except Exception:
                continue
        return min(image_area / page_area, 1.0)
