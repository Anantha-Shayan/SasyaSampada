# 07 — PDF Parsing

## 1. Purpose

Document the **implemented** multi-backend PDF parsing layer (`app/ingestion/stages/parser/`) that handles text PDFs, scanned PDFs (OCR-ready), tables, headers, and footers.

## 2. Problem Being Solved

Agricultural PDFs mix born-digital text, government tables, repeating headers/footers, and scanned annex pages. A single `page.get_text()` call loses table structure, pollutes chunks with page numbers, and fails silently on image-only pages.

## 3. Engineering Decision

**Composite parser** orchestrating specialized backends:

| Backend | Library | Responsibility |
|---------|---------|----------------|
| Layout + text | **PyMuPDF** | Block extraction, raw text, page rasterization |
| Tables | **pdfplumber** | `extract_tables()` → markdown |
| Scanned pages | **Tesseract** (optional) | OCR via `OcrEngine` protocol |
| Classification | Internal | `text` / `scanned` / `mixed` per page |
| Headers/footers | Internal | Vertical band heuristic on PyMuPDF blocks |

Entry point: `CompositePdfParser` (factory default). `PyMuPDFParser` is a backward-compatible alias.

**Unstructured** evaluated but not selected — see §5.

## 4. Alternatives Considered

| Tool | Strengths | Why not default |
|------|-----------|-----------------|
| **PyMuPDF only** | Fast, already in stack | Poor tables; no OCR path |
| **pdfplumber only** | Excellent tables | Slower; weaker layout blocks |
| **Unstructured** | Auto partition PDF/HTML | Heavy deps; opaque pipeline; overkill for 6 PDFs |
| **Amazon Textract** | High OCR quality | Cost; cloud lock-in |
| **pdfminer.six** | Pure Python | Slower than PyMuPDF; dated ergonomics |

## 5. Why Alternative Was Not Selected

- **PyMuPDF + pdfplumber** covers 90% of agri PDFs with minimal dependencies and full control per page.
- **Unstructured** hides partitioning decisions — harder to defend in interview and tune for ICAR tables.
- **Cloud OCR** deferred; `OcrEngine` protocol allows swap later.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Best-of-breed per task | Two PDF libraries in memory |
| OCR optional via env flag | Tesseract system dependency when enabled |
| Rich `ParsedPage` metadata | Larger JSON artifacts |
| Header/footer pre-split for Phase 5 | Heuristic bands ≠ perfect on all layouts |

## 7. Performance Implications

- PyMuPDF block pass: O(pages) — fastest path for text PDFs
- pdfplumber second pass: adds ~0.5–2× parse time on table-heavy docs
- OCR: 1–5 s/page at 200 DPI — only on low-text pages when enabled
- Table markdown appended to `page.text` — improves retrieval vs. lost grid data

## 8. Scaling Considerations

- Parser is CPU-bound — horizontal ingest workers
- OCR pages routed only when `char_count < PDF_MIN_TEXT_CHARS`
- Future: GPU OCR (PaddleOCR), async page pool

## 9. Production Considerations

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OCR_ENABLED` | `false` | Enable Tesseract on scanned pages |
| `PDF_MIN_TEXT_CHARS` | `30` | Text vs scanned threshold |
| `PDF_HEADER_FRACTION` | `0.12` | Top band for headers |
| `PDF_FOOTER_FRACTION` | `0.12` | Bottom band for footers |

### ParsedPage fields

| Field | Purpose |
|-------|---------|
| `page_type` | `text`, `scanned`, `mixed` |
| `body_text` | Content excluding header/footer bands |
| `header_text` / `footer_text` | For Phase 5 cleaner |
| `tables` | Structured `ParsedTable` list |
| `text` | Full assembled content (body + table markdown) |
| `needs_ocr` | True if scanned but OCR not applied |
| `extraction_methods` | Audit: `pymupdf`, `pdfplumber`, `ocr:tesseract` |

### OCR setup (optional)

```bash
# Windows: install Tesseract binary, then:
pip install pytesseract pillow
# .env
OCR_ENABLED=true
```

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| Encrypted PDF | `ParserError` from PyMuPDF |
| Zero pages | `NonRetryableError` |
| All pages scanned, OCR off | `NonRetryableError` with enable-OCR hint |
| pdfplumber table fail | Warning log; page continues without tables |
| OCR exception | Warning log; page flagged `needs_ocr` |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| Table spans pages | pdfplumber per-page tables (may split — future merge) |
| Multi-column layout | Header/footer bands still apply; body may need semantic chunking |
| Hindi scanned pages | Tesseract `lang` config (future) |
| Empty table cells | Normalized to `""` in markdown |

## 12. Security Concerns

- PyMuPDF does not execute JavaScript on open (unlike some browser PDF viewers)
- OCR renders to PNG in memory only — no temp files by default
- Parser runs offline — no document content sent to cloud

## 13. Cost Considerations

- Self-hosted PyMuPDF + pdfplumber: zero marginal cost
- Tesseract: free; CPU cost per OCR page
- Unstructured/Textract avoided: no per-page API fees

## 14. Common Interview Questions

**Q: Why PyMuPDF?**  
A: Fast C-backed extraction, block geometry for headers/footers, pixmap render for OCR.

**Q: Why pdfplumber for tables?**  
A: Purpose-built table detection; converts grids to markdown for LLM retrieval.

**Q: How do you handle scanned PDFs?**  
A: Classify page → rasterize via PyMuPDF → optional Tesseract via `OcrEngine` protocol.

## 15. Deep Interview Questions

**Q: Why not Unstructured?**  
A: Black-box partitioning, heavy install, harder to debug per-page failures in production.

**Q: How would you add PaddleOCR?**  
A: Implement `OcrEngine` with `name = "paddleocr"`; inject into `CompositePdfParser(ocr_engine=...)`.

**Q: Header/footer heuristic failures?**  
A: Phase 5 cleaner adds content rules; future ML layout model; store raw blocks for replay.

## 16. Best Possible Answers

Describe the **per-page pipeline**: classify → split bands → OCR if needed → extract tables → assemble `text`. Name all three libraries and when each runs.

## 17. Diagrams

### Per-page parse flow

```
PDF page
   │
   ▼
PyMuPDF: blocks + raw_text + image_coverage
   │
   ▼
classify_page() ──► text | scanned | mixed
   │
   ▼
split_header_footer() ──► header, body, footer
   │
   ├──► (scanned + OCR_ENABLED) ──► render PNG ──► TesseractOcrEngine
   │
   ▼
pdfplumber: extract_tables() ──► ParsedTable[]
   │
   ▼
assemble_page_text(body, tables) ──► ParsedPage.text
```

### Backend selection matrix

```
                Text PDF    Tables    Scanned
PyMuPDF           ✓          ○          ○ (render only)
pdfplumber        ○          ✓          ○
Tesseract         ○          ○          ✓ (optional)
Unstructured      ✓*         ✓*         ✓*   (* not chosen)
```

## 18. References

- `backend/app/ingestion/stages/parser/composite.py`
- PyMuPDF docs: https://pymupdf.readthedocs.io/
- pdfplumber: https://github.com/jsvine/pdfplumber
- Unstructured.io PDF partition docs
- `docs/08_cleaning.md` (planned Phase 5)
