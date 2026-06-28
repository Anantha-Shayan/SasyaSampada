# `app/retrieval`

Query-time document retrieval. No LLM calls here.

| Module | Role |
|--------|------|
| `base.py` | `Retriever` protocol |
| `similarity.py` | `SimilarityRetriever` — top-K cosine + metadata filters |
| `filters.py` | `RetrievalFilter` → Qdrant `Filter` |
| `mapping.py` | Qdrant payload → `RetrievedChunk` |
| `factory.py` | `build_similarity_retriever()` from env |

**Planned (later phases):** MMR, hybrid BM25+dense, cross-encoder rerank (Phase 18).

Schemas: `app/domain/schemas/retrieval.py`.
