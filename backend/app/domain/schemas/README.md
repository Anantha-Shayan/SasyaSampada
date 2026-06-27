# `app/domain/schemas`

Pydantic models grouped by bounded context.

**Migration plan:** Split `app/models/schemas.py` into:

- `advisory.py` — soil, location, advisory requests
- `chat.py` — chat request/response
- `documents.py` — document metadata, chunks
- `rag.py` — ask/search request/response with citations

Existing `app/models/` remains until Phase 13 refactor to avoid breaking imports.
