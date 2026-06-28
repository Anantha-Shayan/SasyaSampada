from __future__ import annotations

from app.embeddings.providers import HuggingFaceEmbeddingProvider
from app.retrieval.similarity import SimilarityRetriever
from app.vector_db.qdrant import QdrantVectorStore, create_qdrant_client


def build_similarity_retriever(
    *,
    top_k: int | None = None,
    score_threshold: float | None = None,
) -> SimilarityRetriever:
    """Construct the default similarity retriever from environment settings."""
    from app.config import (
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_DEVICE,
        EMBEDDING_MODEL,
        EMBEDDING_NORMALIZE,
        QDRANT_API_KEY,
        QDRANT_COLLECTION,
        QDRANT_URL,
        RETRIEVAL_SCORE_THRESHOLD,
        RETRIEVAL_TOP_K,
    )

    client = create_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
    store = QdrantVectorStore(client, QDRANT_COLLECTION)
    embedder = HuggingFaceEmbeddingProvider(
        EMBEDDING_MODEL,
        device=EMBEDDING_DEVICE,
        batch_size=EMBEDDING_BATCH_SIZE,
        normalize=EMBEDDING_NORMALIZE,
    )

    return SimilarityRetriever(
        store,
        embedder,
        top_k=top_k if top_k is not None else RETRIEVAL_TOP_K,
        score_threshold=(
            score_threshold
            if score_threshold is not None
            else RETRIEVAL_SCORE_THRESHOLD
        ),
    )
