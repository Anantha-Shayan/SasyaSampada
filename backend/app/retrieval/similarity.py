from __future__ import annotations

from app.core.exceptions import RetrievalError, VectorStoreError
from app.core.logging import get_logger
from app.domain.schemas.retrieval import RetrievalFilter, RetrievalResult
from app.embeddings.base import EmbeddingProvider
from app.retrieval.filters import build_qdrant_filter
from app.retrieval.mapping import payload_to_retrieved_chunk
from app.vector_db.qdrant.store import QdrantVectorStore

logger = get_logger(__name__)


class SimilarityRetriever:
    """
    Top-K cosine similarity retrieval against Qdrant.

    Baseline retriever (Phase 10 level 1–2): dense search with optional metadata filters.
    """

    def __init__(
        self,
        store: QdrantVectorStore,
        embedder: EmbeddingProvider,
        *,
        top_k: int = 10,
        score_threshold: float = 0.0,
    ) -> None:
        self._store = store
        self._embedder = embedder
        self._top_k = top_k
        self._score_threshold = score_threshold

    def retrieve(
        self,
        query: str,
        *,
        filters: RetrievalFilter | None = None,
    ) -> RetrievalResult:
        normalized = query.strip()
        if not normalized:
            raise RetrievalError("Query must not be empty")

        logger.info("Retrieving top-%d for query (%d chars)", self._top_k, len(normalized))

        try:
            query_vector = self._embedder.embed_query(normalized)
            hits = self._store.search_similar(
                query_vector,
                limit=self._top_k,
                score_threshold=self._score_threshold or None,
                query_filter=build_qdrant_filter(filters),
            )

            chunks = []
            for hit in hits:
                if hit.payload is None:
                    continue
                chunks.append(payload_to_retrieved_chunk(hit.score, hit.payload))

            return RetrievalResult(
                query=normalized,
                chunks=chunks,
                top_k=self._top_k,
                score_threshold=self._score_threshold,
                embedding_model=self._embedder.model_name,
                filters_applied=filters,
            )
        except RetrievalError:
            raise
        except VectorStoreError as exc:
            raise RetrievalError("Vector store search failed") from exc
        except Exception as exc:
            raise RetrievalError("Similarity retrieval failed") from exc
