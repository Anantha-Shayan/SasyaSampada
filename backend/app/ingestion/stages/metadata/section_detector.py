from __future__ import annotations

import re

CHAPTER_PATTERN = re.compile(
    r"^(?:chapter|section|part)\s+[\divxlc]+\s*[:.\-–—]?\s*(.+)$",
    re.IGNORECASE,
)
NUMBERED_HEADING = re.compile(r"^\d+(?:\.\d+)*\s+([A-Z][^\n]{3,80})$")
TABLE_MARKER = re.compile(r"^\[TABLE\s+(\d+)\]", re.IGNORECASE)
ALL_CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9 ,\-]{4,80}$")


def detect_section_title(chunk_text: str) -> str | None:
    """Infer section title from the opening lines of a chunk."""
    if not chunk_text.strip():
        return None

    first_line = chunk_text.strip().splitlines()[0].strip()

    table_match = TABLE_MARKER.match(first_line)
    if table_match:
        return f"Table {table_match.group(1)}"

    chapter_match = CHAPTER_PATTERN.match(first_line)
    if chapter_match:
        return chapter_match.group(1).strip() or first_line

    numbered_match = NUMBERED_HEADING.match(first_line)
    if numbered_match:
        return numbered_match.group(1).strip()

    if ALL_CAPS_HEADING.match(first_line) and len(first_line.split()) <= 12:
        return first_line.title()

    if len(first_line) <= 80 and first_line.endswith(":"):
        return first_line.rstrip(":").strip()

    return None


def estimate_token_count(text: str) -> int:
    """Rough token estimate without a tokenizer (≈ whitespace-delimited words)."""
    return len(text.split())
