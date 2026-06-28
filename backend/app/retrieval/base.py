from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.schemas.retrieval import RetrievalFilter, RetrievalResult


@runtime_checkable
class Retriever(Protocol):
    """Query-time chunk retrieval for the RAG layer."""

    def retrieve(
        self,
        query: str,
        *,
        filters: RetrievalFilter | None = None,
    ) -> RetrievalResult: ...
