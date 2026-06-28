# 13 — Retrieval

## 1. Purpose

Document **query-time chunk retrieval** — embedding the farmer question, searching Qdrant, and returning scored `RetrievedChunk` objects for the RAG layer (Phase 11+).

## 2. Problem Being Solved

Ingestion indexes vectors; farmers ask natural-language questions at runtime. The system must map "What is the PMFBY premium rate?" to the correct policy paragraphs quickly, with optional filters (e.g. `category=crop_insurance`) and citation-ready metadata.

## 3. Engineering Decision

**`SimilarityRetriever`** (`app/retrieval/`) implements baseline **top-K cosine search**:

```
Question → embed_query (BGE prefix) → Qdrant search → RetrievedChunk[]
```

| Component | Role |
|-----------|------|
| `SimilarityRetriever` | Orchestrates embed + search |
| `build_qdrant_filter` | `RetrievalFilter` → Qdrant payload filter |
| `payload_to_retrieved_chunk` | Typed hit mapping |
| `QdrantVectorStore.search_similar` | Cosine search with payload |
| `build_similarity_retriever()` | Wire from env |

**Config (env):**

| Variable | Default | Role |
|----------|---------|------|
| `RETRIEVAL_TOP_K` | `10` | Max chunks returned |
| `RETRIEVAL_SCORE_THRESHOLD` | `0.0` | Minimum cosine score |
| `EMBEDDING_MODEL` | `bge-small-en-v1.5` | Must match indexed collection |
| `QDRANT_COLLECTION` | `agri_knowledge` | Search target |

**Schemas:** `RetrievalFilter`, `RetrievedChunk`, `RetrievalResult` in `domain/schemas/retrieval.py`.

## 4. Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| Brute-force over JSONL vectors | No scale; no filters |
| LangChain VectorStoreRetriever | Opaque; weak tuning narrative |
| MMR / hybrid first | Higher latency; defer to Phase 18 |
| Embed in RAG service inline | Violates package boundary |

## 5. Why Alternative Was Not Selected

Dedicated `retrieval/` package keeps **dependency direction** clean (`rag → retrieval → vector_db + embeddings`). Top-K cosine is the measurable baseline before MMR/rerank enhancements.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Sub-100ms search at MVP scale | May return near-duplicate chunks |
| Metadata filters at query time | Requires indexed payload fields |
| Testable with mocked Qdrant | CPU embed per question |
| No LLM in retrieval layer | No semantic reranking yet |

## 7. Performance Implications

| Step | Typical latency |
|------|-----------------|
| `embed_query` (CPU) | 20–150 ms |
| Qdrant top-10 | 5–30 ms |
| Payload mapping | < 1 ms |
| **Total** | ~30–200 ms |

## 8. Scaling Considerations

- Cache query embeddings (Redis, Phase 18)
- Reduce `RETRIEVAL_TOP_K` under load
- Qdrant read replicas (Phase 16)
- MMR / rerank when precision plateaus

### Progressive improvements (from `docs/05_rag_pipeline.md`)

| Level | Technique | Status |
|-------|-----------|--------|
| 1 | Top-K cosine | Phase 10 ✓ |
| 2 | Metadata filter | Phase 10 ✓ |
| 3 | MMR | Planned |
| 4 | Hybrid BM25 | Planned |
| 5+ | Multi-query, rerank | Phase 18 |

## 9. Production Considerations

- Empty query → `RetrievalError` (API returns 400 in Phase 13)
- `score_threshold` tunable per category
- `embedding_model` in result for observability
- BGE query prefix applied in `embed_query` only

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| Qdrant down | `RetrievalError` wraps `VectorStoreError` |
| Collection missing | Returns empty `chunks` |
| Malformed payload | `RetrievalError` on mapping |
| Model dimension mismatch | Qdrant error at search |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| No hits above threshold | Empty list; RAG says "don't know" (Phase 11) |
| Filter too narrow | Empty list |
| Hindi question, English docs | Use `bge-m3` or translate (future) |

## 12. Security Concerns

- Query text logged — avoid PII in questions
- Retrieved `text` passed to LLM — sanitize control chars in Phase 11
- Qdrant API key for production clusters

## 13. Cost Considerations

- Local embed: no API cost
- Qdrant self-hosted: free at MVP point counts

## 14. Common Interview Questions

**Q: Why separate retrieval from RAG?**  
A: Test search without LLM; swap rankers; clear latency attribution.

**Q: Why cosine with normalized vectors?**  
A: Dot product equals cosine; Qdrant `Distance.COSINE` matches L2-normalized BGE outputs.

## 15. Deep Interview Questions

**Q: How improve recall without reranker?**  
A: Increase K, lower threshold, multi-query paraphrases, hybrid BM25, better chunking.

**Q: How filter PMFBY-only answers?**  
A: `RetrievalFilter(category="crop_insurance")` at Qdrant query time.

## 16. Best Possible Answers

Walk through embed → filter → search → map payload, cite env vars, and name Phase 18 upgrades (MMR, rerank).

## 17. Diagrams

```
Farmer question
      │
      ▼
SimilarityRetriever
      ├── EmbeddingProvider.embed_query()
      ├── build_qdrant_filter()
      ├── QdrantVectorStore.search_similar()
      └── payload_to_retrieved_chunk()
      │
      ▼
RetrievalResult → RAG context builder (Phase 11)
```

## 18. References

- `backend/app/retrieval/similarity.py`
- `backend/app/vector_db/qdrant/store.py`
- `docs/05_rag_pipeline.md`
- `docs/12_vector_db.md`
