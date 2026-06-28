# 12 — Vector Database (Qdrant)

## 1. Purpose

Document how embedded chunks are **indexed in Qdrant** for similarity search, metadata filtering, and idempotent re-ingestion.

## 2. Problem Being Solved

Disk JSONL embeddings are not queryable at retrieval latency. Farmers need sub-second answers; brute-force cosine over files does not scale. Qdrant provides HNSW-indexed cosine search with payload filters (`category`, `document_id`, `year`).

## 3. Engineering Decision

**`QdrantVectorStoreWriter`** (`app/ingestion/stages/vector_store/`) delegates to **`QdrantVectorStore`** (`app/vector_db/qdrant/`).

| Component | Role |
|-----------|------|
| `client_factory.py` | Build `QdrantClient` from env |
| `collection.py` | Create collection + payload indexes |
| `payload.py` | Map `ChunkRecord` → Qdrant payload |
| `point_ids.py` | UUID5 from `chunk_id` (idempotent upsert) |
| `store.py` | Delete-then-upsert per document version |

**Config (env):**

| Variable | Default | Role |
|----------|---------|------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant HTTP API |
| `QDRANT_API_KEY` | _(empty)_ | Cloud / secured instances |
| `QDRANT_COLLECTION` | `agri_knowledge` | Collection name |
| `QDRANT_UPSERT_BATCH_SIZE` | `64` | Batch upsert size |

**Collection:** cosine distance, vector size from `EmbeddedDocument.dimension` (384 or 1024).

**Point ID:** `uuid5(chunk_id)` — stable across re-runs.

**Upsert flow:**
1. `ensure_collection` (create if missing + payload indexes)
2. `delete` points where `document_id` + `document_version` match
3. Batch `upsert` new points with vector + payload

## 4. Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| Pinecone | SaaS cost; less on-prem control |
| FAISS in-process | No payload filters; not shared across API replicas |
| Chroma | Weaker production ops story |
| Upsert without delete | Stale chunks if chunk count shrinks |
| Integer hash IDs | Collision risk vs UUID5 |

## 5. Why Alternative Was Not Selected

Qdrant was chosen in ADR-002 for **metadata filters**, Docker/self-host path, and HNSW performance. Delete-before-upsert keeps document versions consistent without orphan points.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Fast filtered search | Operate Qdrant service |
| Idempotent chunk IDs | Must run Qdrant for full ingest |
| Shared store for API replicas | Network dependency at index time |
| `NoOpVectorStoreWriter` for tests | Two writer implementations |

## 7. Performance Implications

| Operation | Typical latency |
|-----------|-----------------|
| Collection create (once) | ~50–200 ms |
| Delete by filter (120 chunks) | ~10–50 ms |
| Batch upsert 64 points | ~20–100 ms |
| HNSW search top-10 (Phase 10) | ~5–30 ms |

`wait=True` on upsert/delete ensures manifest `indexed` reflects committed points.

## 8. Scaling Considerations

- Payload indexes on `document_id`, `category`, `language`, `year`
- Separate `QDRANT_COLLECTION` per embedding model when dimension changes
- Horizontal Qdrant replicas (Phase 16)
- Increase `QDRANT_UPSERT_BATCH_SIZE` on LAN to Qdrant

## 9. Production Considerations

- `VectorStoreError` on dimension mismatch — use new collection for new model
- `RetryableIngestionError` on connection timeouts (tenacity on vector_store stage)
- Payload includes chunk `text` for retrieval without disk read
- `NoOpVectorStoreWriter` for CI without Qdrant

### Run Qdrant locally

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| Qdrant down | Retry then `failed` manifest status |
| Wrong vector dimension | `VectorStoreError` with collection hint |
| Empty embedded doc | Returns 0 indexed, no Qdrant calls |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| Re-ingest same version | Delete + upsert replaces all points |
| New document version | Old version points remain until deleted explicitly |
| Collection already exists | Skip create; validate dimension |

## 12. Security Concerns

- `QDRANT_API_KEY` for production clusters
- Payload may contain public agri policy text — no farmer PII
- Do not expose Qdrant port publicly without auth

## 13. Cost Considerations

- Self-hosted Qdrant: free for MVP corpus (~10⁴ points)
- Qdrant Cloud: usage-based at scale

## 14. Common Interview Questions

**Q: Why Qdrant over Pinecone?**  
A: Self-host for rural/on-prem; rich payload filters; no per-query SaaS lock-in at MVP scale.

**Q: Why delete before upsert?**  
A: Handles chunk count changes and guarantees no stale points for that document version.

## 15. Deep Interview Questions

**Q: How rebuild Qdrant from scratch?**  
A: Replay `metadata/chunks.jsonl` + `embeddings/vectors.jsonl` (or re-embed) → upsert stage only.

**Q: How migrate embedding models?**  
A: New collection with matching dimension; dual-write; switch retrieval alias; drop old collection.

## 16. Best Possible Answers

Explain cosine + L2-normalized vectors, UUID5 point IDs, payload indexes, delete-then-upsert, env config, and hybrid disk+Qdrant from ADR-006.

## 17. Diagrams

```
EmbeddedDocument
      │
      ▼
QdrantVectorStoreWriter
      │
      ▼
QdrantVectorStore
      ├── ensure_collection (COSINE, dim)
      ├── delete(document_id, document_version)
      └── upsert(points[])
              │
              ▼
     Qdrant "agri_knowledge"
     (vector + payload per chunk)
```

## 18. References

- `backend/app/vector_db/qdrant/store.py`
- `backend/app/ingestion/stages/vector_store/qdrant.py`
- `docs/04_data_flow.md`
- `docs/23_engineering_decisions.md` (ADR-002, ADR-006)
