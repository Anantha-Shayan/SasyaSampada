from __future__ import annotations

import unicodedata

from app.domain.schemas.ingestion import ParsedPage
from app.ingestion.stages.cleaner.rules import (
    CONTROL_CHARS,
    EXCESS_NEWLINES,
    HORIZONTAL_WHITESPACE,
    HYPHENATED_LINE_BREAK,
    INLINE_PAGE_PATTERN,
    PAGE_NUMBER_LINE_PATTERNS,
)


def normalize_encoding(text: str) -> str:
    """Unicode NFKC normalization and removal of control characters."""
    normalized = unicodedata.normalize("NFKC", text)
    return CONTROL_CHARS.sub("", normalized)


def fix_hyphenated_line_breaks(text: str) -> str:
    """Join words split across lines with a hyphen."""
    return HYPHENATED_LINE_BREAK.sub(r"\1\2", text)


def remove_page_numbers(text: str) -> str:
    """Remove standalone and inline page number artifacts."""
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and any(pattern.match(stripped) for pattern in PAGE_NUMBER_LINE_PATTERNS):
            continue
        cleaned_line = INLINE_PAGE_PATTERN.sub("", line).rstrip()
        lines.append(cleaned_line)
    return "\n".join(lines)


def remove_duplicate_whitespace(text: str) -> str:
    """Collapse horizontal whitespace and excess blank lines."""
    lines = [HORIZONTAL_WHITESPACE.sub(" ", line).strip() for line in text.splitlines()]
    collapsed = "\n".join(lines)
    return EXCESS_NEWLINES.sub("\n\n", collapsed).strip()


def strip_header_footer_leaks(text: str, header: str | None, footer: str | None) -> str:
    """Remove header/footer strings if they appear inside body text."""
    result = text
    if header and header.strip():
        result = result.replace(header.strip(), "")
    if footer and footer.strip():
        result = result.replace(footer.strip(), "")
    return result


def build_page_source_text(page: ParsedPage) -> str:
    """Prefer parser body_text; re-attach table markdown when needed."""
    content = page.body_text.strip() if page.body_text.strip() else page.text.strip()
    if page.tables and "[TABLE" not in content:
        for table in page.tables:
            content += f"\n\n[TABLE {table.table_index + 1}]\n{table.markdown}"
    return content


def clean_page_text(
    text: str,
    *,
    header: str | None = None,
    footer: str | None = None,
) -> str:
    """Apply full cleaning pipeline to a single text block."""
    cleaned = text
    cleaned = strip_header_footer_leaks(cleaned, header, footer)
    cleaned = normalize_encoding(cleaned)
    cleaned = fix_hyphenated_line_breaks(cleaned)
    cleaned = remove_page_numbers(cleaned)
    cleaned = remove_duplicate_whitespace(cleaned)
    return cleaned.strip()


def clean_document_pages(pages: list[ParsedPage]) -> str:
    """Clean each page and join with double newlines."""
    cleaned_pages: list[str] = []
    for page in pages:
        raw = build_page_source_text(page)
        cleaned = clean_page_text(
            raw,
            header=page.header_text,
            footer=page.footer_text,
        )
        if cleaned:
            cleaned_pages.append(cleaned)
    return "\n\n".join(cleaned_pages).strip()
