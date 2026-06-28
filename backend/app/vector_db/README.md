# `app/vector_db`

`VectorStore` protocol: upsert, delete by document version (search in Phase 10).

| Package | Role |
|---------|------|
| `qdrant/` | Qdrant client, collection setup, payload mapping |

Ingestion writes via `QdrantVectorStoreWriter`; retrieval reads via `QdrantVectorStore` (Phase 10).
