# `app/embeddings/providers`

Concrete embedding backends:

- `HuggingFaceEmbeddingProvider` — local inference via `sentence-transformers`
- `OpenAIEmbeddingProvider` — optional cloud fallback
- `CachedEmbeddingProvider` — decorator for dedup/cache (future)

Batch size and rate limits configured in `core.config`.
