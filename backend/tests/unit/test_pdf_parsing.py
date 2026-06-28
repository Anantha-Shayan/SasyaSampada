import pytest

from app.domain.schemas.ingestion import PageType
from app.ingestion.stages.parser.headers_footers import split_header_footer
from app.ingestion.stages.parser.models import PageLayout, TextBlock
from app.ingestion.stages.parser.page_classifier import classify_page, compute_text_density
from app.ingestion.stages.parser.composite import assemble_page_text
from app.ingestion.stages.parser.tables import parse_tables_from_rows, table_rows_to_markdown


def test_classify_text_page() -> None:
    layout = PageLayout(
        page_number=1,
        width=595.0,
        height=842.0,
        blocks=[],
        raw_text="A" * 100,
        image_coverage=0.05,
    )
    assert classify_page(layout, min_text_chars=30) == PageType.TEXT


def test_classify_scanned_page() -> None:
    layout = PageLayout(
        page_number=1,
        width=595.0,
        height=842.0,
        blocks=[],
        raw_text="",
        image_coverage=0.8,
    )
    assert classify_page(layout, min_text_chars=30) == PageType.SCANNED


def test_split_header_footer() -> None:
    layout = PageLayout(
        page_number=1,
        width=100.0,
        height=1000.0,
        blocks=[
            TextBlock(text="Header line", x0=0, y0=10, x1=100, y1=30),
            TextBlock(text="Body paragraph", x0=0, y0=400, x1=100, y1=450),
            TextBlock(text="Footer line", x0=0, y0=950, x1=100, y1=980),
        ],
        raw_text="Header\nBody\nFooter",
        image_coverage=0.0,
    )
    header, body, footer = split_header_footer(layout, 0.12, 0.12)
    assert header == "Header line"
    assert "Body paragraph" in body
    assert footer == "Footer line"


def test_table_markdown() -> None:
    rows = [["Crop", "Season"], ["Rice", "Kharif"]]
    md = table_rows_to_markdown(rows)
    assert "| Crop | Season |" in md
    assert "| Rice | Kharif |" in md


def test_parse_tables_from_rows() -> None:
    tables = parse_tables_from_rows([[["A", "B"], ["1", "2"]]])
    assert len(tables) == 1
    assert tables[0].row_count == 2
    assert tables[0].col_count == 2


def test_assemble_page_text_includes_tables() -> None:
    from app.domain.schemas.ingestion import ParsedTable

    tables = [
        ParsedTable(
            table_index=0,
            rows=[["X", "Y"]],
            markdown="| X | Y |",
            row_count=1,
            col_count=2,
        )
    ]
    text = assemble_page_text("Body content", tables)
    assert "Body content" in text
    assert "[TABLE 1]" in text
    assert "| X | Y |" in text


def test_compute_text_density() -> None:
    density = compute_text_density(100, 10.0, 10.0)
    assert density == 1.0
