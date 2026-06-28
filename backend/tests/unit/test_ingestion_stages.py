from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.core.exceptions import NonRetryableError
from app.domain.schemas.ingestion import LoadedDocument
from app.domain.schemas.knowledge_base import DocumentCatalogEntry, IngestionStatus, LifecycleStatus
from app.ingestion.stages.validator import PdfValidator


def _catalog_entry(filename: str) -> DocumentCatalogEntry:
    now = datetime(2026, 6, 27, 8, 0, tzinfo=timezone.utc)
    return DocumentCatalogEntry(
        document_id="test_doc",
        title="Test",
        category="crop_production",
        filename=filename,
        version=1,
        ingestion_status=IngestionStatus.PENDING,
        lifecycle_status=LifecycleStatus.ACTIVE,
        language="en",
        created_at=now,
        updated_at=now,
    )


def test_validator_rejects_non_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "test_doc.pdf"
    pdf_path.write_bytes(b"NOT_A_PDF")

    entry = _catalog_entry("test_doc.pdf")
    loaded = LoadedDocument(
        catalog=entry,
        source_path=str(pdf_path),
        content_sha256="c" * 64,
        file_size_bytes=pdf_path.stat().st_size,
    )

    with pytest.raises(NonRetryableError):
        PdfValidator().validate(loaded)


def test_validator_accepts_pdf_header(tmp_path: Path) -> None:
    pdf_path = tmp_path / "test_doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 minimal")

    entry = _catalog_entry("test_doc.pdf")
    loaded = LoadedDocument(
        catalog=entry,
        source_path=str(pdf_path),
        content_sha256="d" * 64,
        file_size_bytes=pdf_path.stat().st_size,
    )

    validated = PdfValidator().validate(loaded)
    assert validated.mime_type == "application/pdf"
