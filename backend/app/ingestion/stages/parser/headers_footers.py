from __future__ import annotations

from app.ingestion.stages.parser.models import PageLayout, TextBlock


def split_header_footer(
    layout: PageLayout,
    header_fraction: float,
    footer_fraction: float,
) -> tuple[str | None, str, str | None]:
    """
    Split page blocks into header, body, and footer using vertical bands.

    Returns (header_text, body_text, footer_text).
    """
    if not layout.blocks:
        raw = layout.raw_text.strip()
        return None, raw, None

    page_height = max(layout.height, 1.0)
    header_limit = page_height * header_fraction
    footer_start = page_height * (1.0 - footer_fraction)

    header_parts: list[str] = []
    body_parts: list[str] = []
    footer_parts: list[str] = []

    for block in layout.blocks:
        text = block.text.strip()
        if not text:
            continue
        y_mid = (block.y0 + block.y1) / 2.0
        if y_mid <= header_limit:
            header_parts.append(text)
        elif y_mid >= footer_start:
            footer_parts.append(text)
        else:
            body_parts.append(text)

    header = "\n".join(header_parts).strip() or None
    body = "\n".join(body_parts).strip()
    footer = "\n".join(footer_parts).strip() or None

    if not body:
        body = layout.raw_text.strip()

    return header, body, footer
