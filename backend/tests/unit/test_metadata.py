from datetime import datetime, timezone

import pytest

from app.domain.schemas.ingestion import PageType, ParsedDocumentArtifact, ParsedPage
from app.domain.schemas.knowledge_base import DocumentCatalogEntry, IngestionStatus, LifecycleStatus
from app.ingestion.stages.metadata.page_mapper import map_chunk_to_pages
from app.ingestion.stages.metadata.section_detector import (
    detect_section_title,
    estimate_token_count,
)
from app.ingestion.stages.metadata.generator import RichMetadataGenerator
from app.domain.schemas.ingestion import ChunkedDocument, TextChunk


def test_detect_chapter_section_title() -> None:
    text = "Chapter 3: Rice Cultivation\n\nRice requires water..."
    assert detect_section_title(text) == "Rice Cultivation"


def test_detect_table_section_title() -> None:
    text = "[TABLE 1]\n| Crop | Season |"
    assert detect_section_title(text) == "Table 1"


def test_estimate_token_count() -> None:
    assert estimate_token_count("one two three four") == 4


def test_map_chunk_to_pages() -> None:
    parsed = ParsedDocumentArtifact(
        document_id="doc",
        document_version=1,
        pages=[
            ParsedPage(
                page_number=1,
                page_type=PageType.TEXT,
                text="Intro content only on page one",
                body_text="Intro content only on page one",
                char_count=30,
            ),
            ParsedPage(
                page_number=2,
                page_type=PageType.TEXT,
                text="Wheat chapter details on page two",
                body_text="Wheat chapter details on page two",
                char_count=34,
            ),
        ],
        page_count=2,
        parser_name="test",
        parser_version="0",
        parsed_at=datetime.now(timezone.utc),
        source_filename="doc.pdf",
        content_sha256="a" * 64,
    )
    start, end = map_chunk_to_pages("Wheat chapter details on page two", parsed)
    assert start == 2
    assert end == 2


def _catalog() -> DocumentCatalogEntry:
    now = datetime(2026, 6, 27, 8, 0, tzinfo=timezone.utc)
    return DocumentCatalogEntry(
        document_id="test_doc",
        title="Test Guide",
        category="crop_production",
        organization="ICAR",
        source="ICAR",
        language="en",
        year=2025,
        filename="test_doc.pdf",
        version=1,
        ingestion_status=IngestionStatus.PENDING,
        created_at=now,
        updated_at=now,
    )


def test_rich_metadata_generator_fields() -> None:
    chunked = ChunkedDocument(
        document_id="test_doc",
        document_version=1,
        chunks=[
            TextChunk(
                chunk_index=0,
                text="Chapter 1: Rice\n\nRice needs water.",
            )
        ],
        chunk_size=1000,
        chunk_overlap=200,
    )

    generator = RichMetadataGenerator(parsed_loader=lambda _d, _v: None)
    generator._persist = lambda bundle: None  # noqa: SLF001

    bundle = generator.generate(chunked, _catalog())
    record = bundle.chunks[0]

    assert record.chunk_id == "test_doc::v1::chunk_0000"
    assert record.document_id == "test_doc"
    assert record.chunk_index == 0
    assert record.filename == "test_doc.pdf"
    assert record.language == "en"
    assert record.source == "ICAR"
    assert record.title == "Test Guide"
    assert record.section_title == "Rice"
    assert record.metadata_schema_version == "1.0"
    assert bundle.document_meta["schema_version"] == "1.0"
    assert "ext" in bundle.document_meta
