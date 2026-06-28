from __future__ import annotations

from datetime import datetime, timezone

from app.config import (
    OCR_ENABLED,
    PDF_FOOTER_FRACTION,
    PDF_HEADER_FRACTION,
    PDF_MIN_TEXT_CHARS,
)
from app.core.exceptions import NonRetryableError, ParserError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import (
    PageType,
    ParsedDocumentArtifact,
    ParsedPage,
    ParsedTable,
    ValidatedDocument,
)
from app.ingestion.stages.parser.constants import OCR_RENDER_DPI, PARSER_NAME, PARSER_VERSION
from app.ingestion.stages.parser.headers_footers import split_header_footer
from app.ingestion.stages.parser.ocr import NoOpOcrEngine, OcrEngine, TesseractOcrEngine
from app.ingestion.stages.parser.page_classifier import classify_page, compute_text_density
from app.ingestion.stages.parser.pdfplumber_extractor import PdfPlumberTableExtractor
from app.ingestion.stages.parser.pymupdf_extractor import PyMuPdfExtractor
from app.knowledge_base.paths import parsed_json_path

logger = get_logger(__name__)


def assemble_page_text(body: str, tables: list[ParsedTable]) -> str:
    parts: list[str] = []
    if body.strip():
        parts.append(body.strip())
    for table in tables:
        parts.append(f"[TABLE {table.table_index + 1}]\n{table.markdown}")
    return "\n\n".join(parts)


class CompositePdfParser:
    """
    Multi-backend PDF parser:

    - PyMuPDF: text PDFs, layout blocks, header/footer bands, page images for OCR
    - pdfplumber: table extraction
    - Tesseract (optional): scanned pages when OCR_ENABLED=true
    """

    stage_name = "parser"

    def __init__(
        self,
        *,
        pymupdf_extractor: PyMuPdfExtractor | None = None,
        table_extractor: PdfPlumberTableExtractor | None = None,
        ocr_engine: OcrEngine | None = None,
        min_text_chars: int = PDF_MIN_TEXT_CHARS,
        header_fraction: float = PDF_HEADER_FRACTION,
        footer_fraction: float = PDF_FOOTER_FRACTION,
        ocr_enabled: bool = OCR_ENABLED,
    ) -> None:
        self._pymupdf = pymupdf_extractor or PyMuPdfExtractor()
        self._tables = table_extractor or PdfPlumberTableExtractor()
        self._min_text_chars = min_text_chars
        self._header_fraction = header_fraction
        self._footer_fraction = footer_fraction
        self._ocr_enabled = ocr_enabled
        self._ocr = ocr_engine or self._default_ocr_engine(ocr_enabled)

    def parse(self, document: ValidatedDocument) -> ParsedDocumentArtifact:
        entry = document.loaded.catalog
        source_path = document.loaded.source_path
        logger.info("Parsing %s with composite parser", entry.document_id)

        try:
            layouts = self._pymupdf.extract_layouts(source_path)
            tables_by_page = self._tables.extract_tables_by_page(source_path)
            pages = [
                self._build_page(layout, tables_by_page.get(layout.page_number, []), source_path)
                for layout in layouts
            ]
        except (NonRetryableError, ParserError):
            raise
        except Exception as exc:
            raise ParserError(
                f"Failed to parse PDF: {source_path}",
                stage=self.stage_name,
            ) from exc

        if not pages:
            raise NonRetryableError(f"No pages extracted from {source_path}")

        self._validate_extracted_text(pages, entry.document_id)

        scanned_count = sum(1 for p in pages if p.page_type in {PageType.SCANNED, PageType.MIXED})
        table_count = sum(1 for p in pages if p.has_tables)

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
            scanned_page_count=scanned_count,
            table_page_count=table_count,
            ocr_engine=self._ocr.name if self._ocr_enabled else None,
        )

        self._persist(artifact)
        return artifact

    def _build_page(
        self,
        layout,
        tables: list[ParsedTable],
        source_path: str,
    ) -> ParsedPage:
        page_type = classify_page(layout, self._min_text_chars)
        header, body, footer = split_header_footer(
            layout,
            self._header_fraction,
            self._footer_fraction,
        )

        methods = ["pymupdf"]
        ocr_applied = False
        needs_ocr = page_type in {PageType.SCANNED, PageType.MIXED}

        if needs_ocr and len(body.strip()) < self._min_text_chars:
            if self._ocr_enabled:
                try:
                    image_bytes = self._pymupdf.render_page_image(
                        source_path,
                        layout.page_number,
                        dpi=OCR_RENDER_DPI,
                    )
                    ocr_text = self._ocr.extract_text(
                        image_bytes,
                        page_number=layout.page_number,
                    ).strip()
                    if ocr_text:
                        body = ocr_text
                        ocr_applied = True
                        methods.append(f"ocr:{self._ocr.name}")
                except Exception as exc:
                    logger.warning(
                        "OCR failed on page %d: %s",
                        layout.page_number,
                        exc,
                    )
            else:
                needs_ocr = True

        if tables:
            methods.append("pdfplumber")

        final_text = assemble_page_text(body, tables)
        density = compute_text_density(len(final_text), layout.width, layout.height)

        return ParsedPage(
            page_number=layout.page_number,
            page_type=page_type,
            text=final_text,
            body_text=body,
            header_text=header,
            footer_text=footer,
            tables=tables,
            has_tables=bool(tables),
            ocr_applied=ocr_applied,
            needs_ocr=needs_ocr and not ocr_applied,
            char_count=len(final_text),
            text_density=density,
            extraction_methods=methods,
        )

    def _validate_extracted_text(self, pages: list[ParsedPage], document_id: str) -> None:
        if any(page.text.strip() for page in pages):
            return

        needs_ocr_pages = [p.page_number for p in pages if p.needs_ocr]
        if needs_ocr_pages:
            raise NonRetryableError(
                f"No extractable text in {document_id}. "
                f"Pages {needs_ocr_pages} appear scanned — set OCR_ENABLED=true "
                f"and install tesseract + pytesseract.",
            )
        raise NonRetryableError(f"No extractable text in PDF: {document_id}")

    def _persist(self, artifact: ParsedDocumentArtifact) -> None:
        path = parsed_json_path(artifact.document_id, artifact.document_version)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            artifact.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info("Wrote parsed artifact to %s", path)

    @staticmethod
    def _default_ocr_engine(ocr_enabled: bool) -> OcrEngine:
        if ocr_enabled:
            return TesseractOcrEngine()
        return NoOpOcrEngine()

    @staticmethod
    def load_cached(document_id: str, version: int) -> ParsedDocumentArtifact | None:
        path = parsed_json_path(document_id, version)
        if not path.exists():
            return None
        return ParsedDocumentArtifact.model_validate_json(path.read_text(encoding="utf-8"))
