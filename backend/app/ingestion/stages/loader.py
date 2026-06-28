from __future__ import annotations

from pathlib import Path

from app.core.exceptions import LoaderError, NonRetryableError
from app.core.logging import get_logger
from app.domain.schemas.ingestion import LoadedDocument
from app.domain.schemas.knowledge_base import DocumentCatalogEntry
from app.knowledge_base.paths import raw_pdf_path
from app.knowledge_base.registry import compute_file_sha256

logger = get_logger(__name__)


class FileSystemLoader:
    """Load PDF bytes from data/raw/ using the manifest filename."""

    stage_name = "loader"

    def load(self, entry: DocumentCatalogEntry) -> LoadedDocument:
        path = raw_pdf_path(entry.filename)
        logger.info("Loading document %s from %s", entry.document_id, path)

        if not path.exists():
            raise LoaderError(
                f"Raw PDF not found: {path}",
                stage=self.stage_name,
            )

        try:
            content_sha256 = entry.content_sha256 or compute_file_sha256(path)
            file_size = path.stat().st_size
        except OSError as exc:
            raise LoaderError(
                f"Cannot read file: {path}",
                stage=self.stage_name,
            ) from exc

        if file_size == 0:
            raise NonRetryableError(f"Empty file: {path}")

        return LoadedDocument(
            catalog=entry,
            source_path=str(path.resolve()),
            content_sha256=content_sha256,
            file_size_bytes=file_size,
        )
