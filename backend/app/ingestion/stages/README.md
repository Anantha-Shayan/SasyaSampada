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
├── metadata.py      # Phase 7
└── embedding.py     # Phase 8 (delegates to app/embeddings)
```

`parser.py` at package root is a scratch script; will be replaced in Phase 4.
