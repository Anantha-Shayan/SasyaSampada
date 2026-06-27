# `app/embeddings`

`EmbeddingProvider` protocol: `embed_documents`, `embed_query`, `dimension`.

**Default models:**

- `BAAI/bge-small-en-v1.5` — fast, 384-dim, English-focused
- `BAAI/bge-m3` — multilingual, 1024-dim, denser

Provider selected via `EMBEDDING_MODEL` env var. Normalization applied before Qdrant upsert (Phase 8).
