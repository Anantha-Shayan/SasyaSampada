import pytest

from app.domain.schemas.ingestion import PageType, ParsedPage, ParsedTable
from app.ingestion.stages.cleaner.text_utils import (
    clean_page_text,
    fix_hyphenated_line_breaks,
    normalize_encoding,
    remove_duplicate_whitespace,
    remove_page_numbers,
    strip_header_footer_leaks,
)


def test_normalize_encoding_removes_control_chars() -> None:
    text = "Crop\x07 advice"
    assert "\x07" not in normalize_encoding(text)
    assert "Crop" in normalize_encoding(text)


def test_fix_hyphenated_line_breaks() -> None:
    text = "agricul-\nture"
    assert fix_hyphenated_line_breaks(text) == "agriculture"


def test_remove_page_numbers() -> None:
    text = "Rice cultivation guide\nPage 12\nMore content\n- 5 -"
    cleaned = remove_page_numbers(text)
    assert "Page 12" not in cleaned
    assert "- 5 -" not in cleaned
    assert "Rice cultivation guide" in cleaned
    assert "More content" in cleaned


def test_remove_duplicate_whitespace() -> None:
    text = "Too   many    spaces\n\n\n\nextra gaps"
    cleaned = remove_duplicate_whitespace(text)
    assert "Too many spaces" in cleaned
    assert "\n\n\n" not in cleaned


def test_strip_header_footer_leaks() -> None:
    text = "Ministry Report\nActual content here\nPage footer"
    cleaned = strip_header_footer_leaks(
        text,
        header="Ministry Report",
        footer="Page footer",
    )
    assert "Ministry Report" not in cleaned
    assert "Page footer" not in cleaned
    assert "Actual content here" in cleaned


def test_clean_page_text_full_pipeline() -> None:
    cleaned = clean_page_text(
        "agricul-\nture practices\nPage 2",
        header="ICAR Advisory",
        footer="Page 2",
    )
    assert "agriculture practices" in cleaned
    assert "Page 2" not in cleaned


def test_clean_page_preserves_table_markdown() -> None:
    from app.ingestion.stages.cleaner.text_utils import build_page_source_text

    page = ParsedPage(
        page_number=1,
        page_type=PageType.TEXT,
        text="full",
        body_text="Crop data",
        tables=[
            ParsedTable(
                table_index=0,
                rows=[["Crop", "Season"], ["Rice", "Kharif"]],
                markdown="| Crop | Season |",
                row_count=2,
                col_count=2,
            )
        ],
        has_tables=True,
        char_count=0,
    )
    source = build_page_source_text(page)
    assert "[TABLE 1]" in source
    assert "| Crop | Season |" in source
