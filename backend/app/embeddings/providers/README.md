# `app/embeddings/providers`

| Provider | Status |
|----------|--------|
| `HuggingFaceEmbeddingProvider` | Phase 8 ✓ — `sentence-transformers`, BGE models |
| `OpenAIEmbeddingProvider` | Planned — cloud fallback |
| `CachedEmbeddingProvider` | Planned — dedup decorator |

Configured via `EMBEDDING_MODEL`, `EMBEDDING_DEVICE`, `EMBEDDING_BATCH_SIZE` in `app/config.py`.
