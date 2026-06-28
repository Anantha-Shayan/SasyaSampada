from __future__ import annotations

from app.domain.schemas.ingestion import PageType
from app.ingestion.stages.parser.constants import DEFAULT_MIN_TEXT_CHARS
from app.ingestion.stages.parser.models import PageLayout


def classify_page(layout: PageLayout, min_text_chars: int = DEFAULT_MIN_TEXT_CHARS) -> PageType:
    """Classify page as text, scanned, or mixed based on extractable text and images."""
    stripped = layout.raw_text.strip()
    char_count = len(stripped)

    if char_count >= min_text_chars and layout.image_coverage < 0.45:
        return PageType.TEXT

    if char_count < min_text_chars and layout.image_coverage >= 0.25:
        return PageType.SCANNED

    if char_count < min_text_chars:
        return PageType.SCANNED

    return PageType.MIXED


def compute_text_density(char_count: int, page_width: float, page_height: float) -> float:
    area = max(page_width * page_height, 1.0)
    return char_count / area
