# `app/vector_db/qdrant`

Qdrant-specific client wrapper (Phase 9).

- Collection management (create, configure HNSW)
- Payload indexing for metadata filters
- Batch upsert with idempotency keys (`document_id` + `chunk_id`)
- Docker Compose service (Phase 17)
