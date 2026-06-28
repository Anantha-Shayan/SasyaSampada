from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import CleanerError, NonRetryableError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import CleanedDocument, ParsedDocumentArtifact
from app.knowledge_base.paths import cleaned_text_path

logger = get_logger(__name__)

CLEANER_NAME = "passthrough"


class PassthroughCleaner:
    """
    Minimal cleaner: join page text with double newlines.

    Header/footer removal and encoding fixes are implemented in Phase 5.
    """

    stage_name = "cleaner"

    def clean(self, parsed: ParsedDocumentArtifact) -> CleanedDocument:
        logger.info("Cleaning %s (passthrough)", parsed.document_id)

        try:
            text = "\n\n".join(page.text for page in parsed.pages).strip()
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
        logger.info("Wrote cleaned text to %s", path)
        return document
