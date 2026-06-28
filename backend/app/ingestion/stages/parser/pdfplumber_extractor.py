from __future__ import annotations

import logging

import pdfplumber

from app.domain.schemas.ingestion import ParsedTable
from app.ingestion.stages.parser.tables import parse_tables_from_rows

logger = logging.getLogger(__name__)


class PdfPlumberTableExtractor:
    """Extract tables per page using pdfplumber."""

    def extract_tables_by_page(self, source_path: str) -> dict[int, list[ParsedTable]]:
        tables_by_page: dict[int, list[ParsedTable]] = {}
        try:
            with pdfplumber.open(source_path) as pdf:
                for page_index, page in enumerate(pdf.pages):
                    page_number = page_index + 1
                    raw_tables = page.extract_tables() or []
                    parsed = parse_tables_from_rows(raw_tables)
                    if parsed:
                        tables_by_page[page_number] = parsed
        except Exception as exc:
            logger.warning("pdfplumber table extraction failed for %s: %s", source_path, exc)
        return tables_by_page
