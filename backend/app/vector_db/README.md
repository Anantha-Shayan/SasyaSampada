# `app/vector_db`

`VectorStore` protocol: upsert, delete, search, filter by metadata.

Implementation details live in subpackages (`qdrant/`).

Ingestion writes; retrieval reads. Both use the same interface.
