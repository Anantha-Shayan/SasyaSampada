# `app/embeddings`

`EmbeddingProvider` protocol: `embed_documents`, `embed_query`, `dimension`.

**Default models:**

- `BAAI/bge-small-en-v1.5` — fast, 384-dim, English-focused (default)
- `BAAI/bge-m3` — multilingual, 1024-dim

Provider selected via `EMBEDDING_MODEL`. L2 normalization applied before Qdrant upsert (Phase 9).
Ingestion stage: `app/ingestion/stages/embedding/`.
