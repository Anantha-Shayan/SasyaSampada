# 11 — Embeddings

## 1. Purpose

Document how chunk text is vectorized with **BGE embedding models** via `sentence-transformers`, persisted to disk, and passed to the vector store stage.

## 2. Problem Being Solved

Retrieval requires dense vectors aligned with the query embedding space. Stub zero-vectors cannot rank chunks. Farmer questions must match policy paragraphs semantically — e.g. "PMFBY premium rate" → relevant insurance section.

## 3. Engineering Decision

**`HuggingFaceEmbeddingGenerator`** (`app/ingestion/stages/embedding/`) delegates inference to **`HuggingFaceEmbeddingProvider`** (`app/embeddings/providers/`).

| Model | Dimension | Use case |
|-------|-----------|----------|
| `BAAI/bge-small-en-v1.5` | 384 | **Default** — fast English agri PDFs |
| `BAAI/bge-m3` | 1024 | Multilingual / denser retrieval |

**Config (env):**

| Variable | Default | Role |
|----------|---------|------|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | HuggingFace model id |
| `EMBEDDING_BATCH_SIZE` | `32` | Encode batch size |
| `EMBEDDING_DEVICE` | `cpu` | `cpu` or `cuda` |
| `EMBEDDING_NORMALIZE` | `true` | L2-normalize before Qdrant cosine |

**Persistence:** `data/embeddings/{document_id}/v{n}/{model_slug}/vectors.jsonl` + `embedding_meta.json`

**BGE query prefix:** Applied only in `embed_query()` for `bge-small-en-v1.5` at retrieval time (Phase 10). Ingest embeds document passages without prefix.

## 4. Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| OpenAI `text-embedding-3-small` | API cost; network dependency |
| Cohere embed | Same |
| No normalization | Hurts cosine distance in Qdrant |
| Embed in API process only | No disk replay; harder debugging |
| Stub forever | Blocks retrieval quality testing |

## 5. Why Alternative Was Not Selected

Local BGE models are **free at ingest scale** (6 PDFs), run offline, and are the standard baseline for English RAG benchmarks. Disk cache enables Qdrant rebuild without re-running the neural encoder.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Production-quality vectors | ~90 MB model download (bge-small) |
| Swappable via `EMBEDDING_MODEL` | CPU ingest slower than GPU |
| Inspectable JSONL cache | Large vector files per document |
| `StubEmbeddingGenerator` for tests | Two code paths to maintain |

## 7. Performance Implications

| Setting | bge-small-en-v1.5 (CPU) | bge-m3 (CPU) |
|---------|-------------------------|--------------|
| ~1000-char chunk | ~20–80 ms | ~50–150 ms |
| 120 chunks / doc | ~3–10 s | ~8–20 s |
| Batch size 32 | Amortizes model forward pass | Same |

GPU (`EMBEDDING_DEVICE=cuda`) reduces ingest time 5–10× when available.

## 8. Scaling Considerations

- Lazy model load — first document pays download + init cost
- Single process model singleton per worker (future: dedicated embedding service)
- Re-embed on model change via new `embeddings/{model_slug}/` directory — manifest tracks `embedding_model`
- Batch size tunable for memory vs throughput

## 9. Production Considerations

- Vectors L2-normalized when `EMBEDDING_NORMALIZE=true` (Qdrant cosine)
- `EmbeddingError` wraps stage failures; embedder stage uses `tenacity` retry
- `vectors.jsonl` is rebuildable from `chunks.jsonl` + model
- Catalog `embedding_model` updated after successful embed stage

## 10. Failure Cases

| Case | Behavior |
|------|------|
| Model download fails | `EmbeddingError`; manifest `failed` |
| OOM on large batch | Lower `EMBEDDING_BATCH_SIZE` |
| Vector count mismatch | `EmbeddingError` (non-retryable) |
| Missing sentence-transformers | Import error at first embed |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| Empty chunk list | Returns empty `EmbeddedDocument` |
| Zero-norm vector | `l2_normalize` returns unchanged |
| Switch bge-small → bge-m3 | New slug dir; re-index Qdrant (Phase 9) |

## 12. Security Concerns

- Models loaded from HuggingFace Hub — pin version in production
- No user text leaves machine (unlike cloud embed APIs)
- Vector files contain chunk text indirectly via separate metadata — not duplicated in JSONL (chunk_id only)

## 13. Cost Considerations

- **$0** API cost for local BGE
- One-time disk: ~90 MB (small) or ~2 GB (m3)
- Electricity / GPU optional

## 14. Common Interview Questions

**Q: Why BGE over OpenAI embeddings?**  
A: Offline, no per-token cost, strong English retrieval baseline, full control for agri corpus.

**Q: Why normalize embeddings?**  
A: Qdrant cosine similarity assumes unit vectors; normalization makes dot product equivalent to cosine.

## 15. Deep Interview Questions

**Q: Why different handling for query vs document?**  
A: BGE v1.5 is trained with an instruction prefix at query time; passages are embedded as-is.

**Q: How swap models without re-parsing PDFs?**  
A: Replay from `chunks.jsonl` → embedder only → new `embeddings/{slug}/` → re-upsert Qdrant.

## 16. Best Possible Answers

Name both models, dimensions, env vars, disk layout, normalization, query prefix rule, and stub for tests.

## 17. Diagrams

```
MetadataBundle (ChunkRecord[])
        │
        ▼
HuggingFaceEmbeddingGenerator
        │
        ├── HuggingFaceEmbeddingProvider.embed_documents()
        ├── l2_normalize (optional)
        └── persist → vectors.jsonl + embedding_meta.json
        │
        ▼
EmbeddedDocument → NoOpVectorStoreWriter (Phase 9: Qdrant)
```

## 18. References

- `backend/app/embeddings/providers/huggingface.py`
- `backend/app/ingestion/stages/embedding/generator.py`
- `data/README.md` — embeddings directory layout
- `docs/10_metadata.md` — chunk records fed to embedder
