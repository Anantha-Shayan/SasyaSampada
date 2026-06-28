from __future__ import annotations

import json
from datetime import datetime, timezone

import pymupdf

from app.core.exceptions import NonRetryableError, ParserError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import ParsedDocumentArtifact, ParsedPage, ValidatedDocument
from app.knowledge_base.paths import parsed_json_path

logger = get_logger(__name__)

PARSER_NAME = "pymupdf"
PARSER_VERSION = "1.27.2"


class PyMuPDFParser:
    """Basic PDF text extraction via PyMuPDF. Enhanced in Phase 4."""

    stage_name = "parser"

    def parse(self, document: ValidatedDocument) -> ParsedDocumentArtifact:
        entry = document.loaded.catalog
        source_path = document.loaded.source_path
        logger.info("Parsing %s with PyMuPDF", entry.document_id)

        try:
            pages = self._extract_pages(source_path)
        except Exception as exc:
            raise ParserError(
                f"Failed to parse PDF: {source_path}",
                stage=self.stage_name,
            ) from exc

        if not pages:
            raise NonRetryableError(f"No pages extracted from {source_path}")

        if not any(page.text.strip() for page in pages):
            raise NonRetryableError(
                f"No extractable text in PDF (OCR required): {entry.document_id}",
            )

        artifact = ParsedDocumentArtifact(
            document_id=entry.document_id,
            document_version=entry.version,
            pages=pages,
            page_count=len(pages),
            parser_name=PARSER_NAME,
            parser_version=PARSER_VERSION,
            parsed_at=datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00")),
            source_filename=entry.filename,
            content_sha256=document.loaded.content_sha256,
        )

        self._persist(artifact)
        return artifact

    def _extract_pages(self, source_path: str) -> list[ParsedPage]:
        pages: list[ParsedPage] = []
        with pymupdf.open(source_path) as pdf:
            for page_num, page in enumerate(pdf, start=1):
                text = page.get_text() or ""
                pages.append(
                    ParsedPage(
                        page_number=page_num,
                        text=text,
                        char_count=len(text),
                    )
                )
        return pages

    def _persist(self, artifact: ParsedDocumentArtifact) -> None:
        path = parsed_json_path(artifact.document_id, artifact.document_version)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            artifact.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info("Wrote parsed artifact to %s", path)

    @staticmethod
    def load_cached(document_id: str, version: int) -> ParsedDocumentArtifact | None:
        path = parsed_json_path(document_id, version)
        if not path.exists():
            return None
        return ParsedDocumentArtifact.model_validate_json(path.read_text(encoding="utf-8"))
