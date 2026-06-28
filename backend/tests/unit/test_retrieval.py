from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from qdrant_client.models import ScoredPoint

from app.core.exceptions import RetrievalError
from app.domain.schemas.retrieval import RetrievalFilter
from app.retrieval.filters import build_qdrant_filter
from app.retrieval.mapping import payload_to_retrieved_chunk
from app.retrieval.similarity import SimilarityRetriever


def test_build_qdrant_filter_category() -> None:
    qfilter = build_qdrant_filter(RetrievalFilter(category="crop_production"))
    assert qfilter is not None
    assert len(qfilter.must) == 1


def test_payload_to_retrieved_chunk() -> None:
    chunk = payload_to_retrieved_chunk(
        0.92,
        {
            "chunk_id": "doc::v1::chunk_0000",
            "document_id": "doc",
            "document_version": 1,
            "chunk_index": 0,
            "text": "Rice needs water.",
            "category": "crop_production",
            "language": "en",
            "filename": "doc.pdf",
            "page_start": 2,
            "section_title": "Rice",
        },
    )
    assert chunk.score == 0.92
    assert chunk.page_start == 2
    assert chunk.section_title == "Rice"


class _FakeEmbedder:
    model_name = "BAAI/bge-small-en-v1.5"

    def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


def test_similarity_retriever_maps_hits() -> None:
    store = MagicMock()
    store.search_similar.return_value = [
        ScoredPoint(
            id="point-1",
            version=1,
            score=0.88,
            payload={
                "chunk_id": "doc::v1::chunk_0000",
                "document_id": "doc",
                "document_version": 1,
                "chunk_index": 0,
                "text": "PMFBY premium details",
                "category": "crop_insurance",
                "language": "en",
                "filename": "doc.pdf",
            },
            vector=None,
        )
    ]

    result = SimilarityRetriever(
        store,
        _FakeEmbedder(),
        top_k=5,
        score_threshold=0.0,
    ).retrieve("pmfby premium", filters=RetrievalFilter(category="crop_insurance"))

    assert result.embedding_model == "BAAI/bge-small-en-v1.5"
    assert len(result.chunks) == 1
    assert result.chunks[0].text == "PMFBY premium details"
    store.search_similar.assert_called_once()


def test_similarity_retriever_rejects_empty_query() -> None:
    retriever = SimilarityRetriever(MagicMock(), _FakeEmbedder())
    with pytest.raises(RetrievalError):
        retriever.retrieve("   ")
