from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import CleanerError, NonRetryableError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import CleanedDocument, ParsedDocumentArtifact
from app.ingestion.stages.cleaner.text_utils import clean_document_pages
from app.knowledge_base.paths import cleaned_text_path

logger = get_logger(__name__)

CLEANER_NAME = "agricultural_text"


class AgriculturalTextCleaner:
    """
    Production text cleaner for parsed agricultural PDFs.

    Removes headers, footers, page numbers, duplicate whitespace,
    hyphenation breaks, and encoding artifacts.
    """

    stage_name = "cleaner"

    def clean(self, parsed: ParsedDocumentArtifact) -> CleanedDocument:
        logger.info("Cleaning %s with %s", parsed.document_id, CLEANER_NAME)

        try:
            text = clean_document_pages(parsed.pages)
        except Exception as exc:
            raise CleanerError(
                f"Failed to clean document {parsed.document_id}",
                stage=self.stage_name,
            ) from exc

        if not text:
            raise NonRetryableError(f"Empty text after cleaning: {parsed.document_id}")

        document = CleanedDocument(
            document_id=parsed.document_id,
            document_version=parsed.document_version,
            text=text,
            char_count=len(text),
            cleaner_name=CLEANER_NAME,
            cleaned_at=datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00")),
        )

        path = cleaned_text_path(document.document_id, document.document_version)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document.text, encoding="utf-8")
        logger.info("Wrote cleaned text to %s (%d chars)", path, document.char_count)
        return document
