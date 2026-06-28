from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import NonRetryableError, ValidationError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import LoadedDocument, ValidatedDocument

logger = get_logger(__name__)

PDF_MAGIC = b"%PDF"
MAX_PDF_BYTES = 100 * 1024 * 1024  # 100 MB


class PdfValidator:
    """Validate PDF magic bytes, size limits, and manifest consistency."""

    stage_name = "validator"

    def validate(self, document: LoadedDocument) -> ValidatedDocument:
        path = document.source_path
        logger.info("Validating %s", document.catalog.document_id)

        try:
            with open(path, "rb") as handle:
                header = handle.read(8)
        except OSError as exc:
            raise ValidationError(
                f"Cannot read file for validation: {path}",
                stage=self.stage_name,
            ) from exc

        if not header.startswith(PDF_MAGIC):
            raise NonRetryableError(
                f"Not a PDF file (missing %PDF header): {path}",
            )

        if document.file_size_bytes > MAX_PDF_BYTES:
            raise NonRetryableError(
                f"PDF exceeds size limit ({MAX_PDF_BYTES} bytes): {path}",
            )

        expected_name = document.catalog.filename
        if not path.replace("\\", "/").endswith(expected_name):
            raise ValidationError(
                f"Filename mismatch: expected {expected_name}",
                stage=self.stage_name,
            )

        return ValidatedDocument(
            loaded=document,
            validated_at=datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00")),
        )
