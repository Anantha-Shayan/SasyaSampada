"""Text cleaning rules and regex patterns for agricultural PDFs."""

from __future__ import annotations

import re

# Standalone page number lines (footer style)
PAGE_NUMBER_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*page\s+\d+\s*(?:of\s+\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*-\s*\d+\s*-\s*$"),
    re.compile(r"^\s*\d+\s*/\s*\d+\s*$"),
    re.compile(r"^\s*page\s*:\s*\d+\s*$", re.IGNORECASE),
)

# Inline page references at end of line
INLINE_PAGE_PATTERN = re.compile(
    r"\s+(?:page|p\.?)\s+\d+\s*$",
    re.IGNORECASE,
)

# Hyphenation across line breaks: "culti-\nvation" -> "cultivation"
HYPHENATED_LINE_BREAK = re.compile(r"(\w)-\n(\w)")

# Multiple spaces or tabs
HORIZONTAL_WHITESPACE = re.compile(r"[ \t]+")

# Three or more blank lines
EXCESS_NEWLINES = re.compile(r"\n{3,}")

# Control characters except newline
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
