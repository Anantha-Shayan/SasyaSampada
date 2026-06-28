# `app/ingestion/stages`

Concrete implementations of ingestion interfaces.

**Planned layout:**

```
stages/
├── loader.py
├── validator.py
├── parser/          # Phase 4: PyMuPDF, pdfplumber, OCR
├── cleaner.py       # Phase 5
├── chunker.py       # Phase 6
├── metadata/          # Phase 7 ✓
├── embedding/         # Phase 8 ✓ (delegates to app/embeddings)
└── vector_store/      # Phase 9 ✓ (delegates to app/vector_db/qdrant)
```

`parser.py` at package root is a scratch script; will be replaced in Phase 4.
