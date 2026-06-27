# `app/api/v1/endpoints`

Thin HTTP handlers. Each file maps to one resource domain.

**Current:** Legacy routes live in `app/api/routes.py` (unchanged until Phase 13).

**Planned split (Phase 13):**

| Module | Endpoints |
|--------|-----------|
| `health.py` | `/health`, `/metrics` |
| `documents.py` | Upload, delete, list PDFs |
| `rag.py` | `/ask`, `/search` |
| `advisory.py` | Crop advisory (existing ML) |
| `chat.py` | Legacy chat (migrated to RAG) |

Handlers validate input, call services, map exceptions to HTTP status codes.
