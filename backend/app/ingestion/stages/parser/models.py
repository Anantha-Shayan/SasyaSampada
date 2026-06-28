from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextBlock:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True)
class PageLayout:
    page_number: int
    width: float
    height: float
    blocks: list[TextBlock]
    raw_text: str
    image_coverage: float
