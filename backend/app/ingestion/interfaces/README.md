# `app/ingestion/interfaces`

Abstract base classes (Protocols) for each pipeline stage.

**Planned interfaces (Phase 3):**

- `DocumentLoader` — resolve raw bytes/path from storage
- `DocumentValidator` — schema, size, MIME checks
- `DocumentParser` — PDF → structured pages
- `DocumentCleaner` — normalize text
- `DocumentChunker` — split into retrieval units
- `MetadataGenerator` — attach rich metadata
- `EmbeddingGenerator` — vectorize chunks
- `VectorStoreWriter` — upsert to Qdrant

Each interface has a single responsibility. Implementations are swappable via DI.
