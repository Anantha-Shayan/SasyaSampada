# `app/ingestion/stages/embedding/`

| Module | Role |
|--------|------|
| `generator.py` | `HuggingFaceEmbeddingGenerator` — default ingest embedder |
| `stub.py` | `StubEmbeddingGenerator` — zero vectors for tests |
| `persist.py` | Write `vectors.jsonl` + `embedding_meta.json` |

Delegates model inference to `app/embeddings/providers/`.
