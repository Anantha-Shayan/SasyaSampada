from __future__ import annotations

from app.domain.schemas.ingestion import ParsedDocumentArtifact


def _page_search_text(page) -> str:
    body = getattr(page, "body_text", "") or ""
    if body.strip():
        return body
    return page.text or ""


def map_chunk_to_pages(
    chunk_text: str,
    parsed: ParsedDocumentArtifact | None,
    *,
    probe_length: int = 200,
) -> tuple[int | None, int | None]:
    """
    Map a chunk to page numbers by substring overlap with parsed page text.

    Uses the first `probe_length` characters as a fingerprint against each page.
    """
    if not parsed or not chunk_text.strip():
        return None, None

    probe = chunk_text[:probe_length].strip()
    if len(probe) < 20:
        probe = chunk_text.strip()

    matched: list[int] = []
    for page in parsed.pages:
        haystack = _page_search_text(page)
        if not haystack:
            continue
        if probe in haystack or (len(probe) >= 40 and probe[:40] in haystack):
            matched.append(page.page_number)

    if not matched:
        return None, None

    return min(matched), max(matched)
