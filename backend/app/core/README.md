# `app/core`

Cross-cutting infrastructure shared by API, ingestion, retrieval, and RAG layers.

**Planned modules (Phase 15):**

- `config.py` — typed settings from environment variables
- `logging.py` — structured logging with request IDs
- `exceptions.py` — domain exception hierarchy
- `dependencies.py` — FastAPI dependency injection providers

**Rule:** No business logic. No PDF parsing, embedding, or LLM calls.
