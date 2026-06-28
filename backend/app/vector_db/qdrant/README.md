# `app/vector_db/qdrant`

Qdrant implementation (Phase 9).

| Module | Role |
|--------|------|
| `client_factory.py` | `create_qdrant_client` from `QDRANT_URL` |
| `collection.py` | Cosine collection + payload indexes |
| `payload.py` | `ChunkRecord` → filterable payload |
| `point_ids.py` | UUID5 ids from `chunk_id` |
| `store.py` | `QdrantVectorStore` upsert/delete |

Configured via `QDRANT_URL`, `QDRANT_COLLECTION`, `QDRANT_UPSERT_BATCH_SIZE`.

Local dev: `docker run -p 6333:6333 qdrant/qdrant`
