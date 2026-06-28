"""PDF parsing: PyMuPDF text, pdfplumber tables, OCR-ready pipeline."""

from app.ingestion.stages.parser.composite import CompositePdfParser

# Backward-compatible alias used in tests and imports
PyMuPDFParser = CompositePdfParser

__all__ = ["CompositePdfParser", "PyMuPDFParser"]
