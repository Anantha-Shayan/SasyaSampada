# `app/ingestion/stages/parser/`

Multi-backend PDF parsing (Phase 4).

| Module | Backend | Role |
|--------|---------|------|
| `composite.py` | — | Orchestrates all backends |
| `pymupdf_extractor.py` | PyMuPDF | Text, blocks, layout, page images |
| `pdfplumber_extractor.py` | pdfplumber | Table extraction |
| `ocr.py` | Tesseract (optional) | Scanned page OCR |
| `page_classifier.py` | — | text / scanned / mixed |
| `headers_footers.py` | — | Band-based header/footer split |
| `tables.py` | — | Markdown table formatting |

Default entry: `CompositePdfParser` (aliased as `PyMuPDFParser` for compatibility).
