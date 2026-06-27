# `app/retrieval`

Query-time document retrieval. No LLM calls here.

**Planned (Phase 10):**

- `Retriever` protocol
- `SimilarityRetriever` — top-K cosine search in Qdrant
- `MMRRetriever` — diversity-aware selection
- `HybridRetriever` — dense + sparse (future BM25)
- `Reranker` — cross-encoder hook (future)

Retrieval returns `RetrievedChunk` objects with scores and metadata for the RAG layer.
