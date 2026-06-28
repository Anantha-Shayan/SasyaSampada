# `app/ingestion/stages/vector_store/`

| Module | Role |
|--------|------|
| `qdrant.py` | `QdrantVectorStoreWriter` — default production indexer |
| `noop.py` | `NoOpVectorStoreWriter` — offline / unit tests |

Delegates Qdrant operations to `app/vector_db/qdrant/`.
