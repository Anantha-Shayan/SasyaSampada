# `app/knowledge_base`

Catalog and path conventions for the on-disk knowledge base (Phase 2).

| Module | Role |
|--------|------|
| `paths.py` | Resolve versioned artifact paths; chunk id format |
| `registry.py` | Load/save `documents.json`; dedup by SHA-256 |

No PDF parsing or embedding — consumed by ingestion pipeline (Phase 3).
