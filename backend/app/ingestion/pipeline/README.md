# `app/ingestion/pipeline`

Orchestrates stage execution: ordering, retries, logging, failure handling.

**Planned (Phase 3):**

- `IngestionPipeline` — runs stages sequentially with typed context object
- `IngestionResult` — summary (document_id, chunk_count, duration)
- Stage-level retry via `tenacity` (already in requirements)

Pipeline is invoked by CLI script and `/documents/upload` API (Phase 13).
