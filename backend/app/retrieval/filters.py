from __future__ import annotations

from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.domain.schemas.retrieval import RetrievalFilter


def build_qdrant_filter(filters: RetrievalFilter | None) -> Filter | None:
    """Translate retrieval filters to a Qdrant payload filter."""
    if filters is None:
        return None

    conditions: list[FieldCondition] = []
    if filters.document_id:
        conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchValue(value=filters.document_id),
            )
        )
    if filters.category:
        conditions.append(
            FieldCondition(
                key="category",
                match=MatchValue(value=filters.category),
            )
        )
    if filters.language:
        conditions.append(
            FieldCondition(
                key="language",
                match=MatchValue(value=filters.language),
            )
        )
    if filters.year is not None:
        conditions.append(
            FieldCondition(
                key="year",
                match=MatchValue(value=filters.year),
            )
        )

    if not conditions:
        return None
    return Filter(must=conditions)
