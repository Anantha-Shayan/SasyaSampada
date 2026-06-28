from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

from app.domain.schemas.ingestion import MetadataBundle
from app.domain.schemas.knowledge_base import ChunkRecord
from app.embeddings.normalize import l2_normalize
from app.embeddings.registry import get_model_dimension, prepare_query_text, uses_bge_query_prefix
from app.ingestion.stages.embedding.generator import HuggingFaceEmbeddingGenerator


class _FakeProvider:
    model_name = "BAAI/bge-small-en-v1.5"

    @property
    def dimension(self) -> int:
        return 3

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), 1.0, 0.0] for index, _ in enumerate(texts)]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def test_l2_normalize_unit_vector() -> None:
    normalized = l2_normalize([3.0, 4.0])
    assert math.isclose(normalized[0], 0.6)
    assert math.isclose(normalized[1], 0.8)


def test_known_model_dimensions() -> None:
    assert get_model_dimension("BAAI/bge-small-en-v1.5") == 384
    assert get_model_dimension("BAAI/bge-m3") == 1024


def test_bge_query_prefix_flag() -> None:
    assert uses_bge_query_prefix("BAAI/bge-small-en-v1.5") is True
    assert uses_bge_query_prefix("BAAI/bge-m3") is False


def _chunk_record(text: str) -> ChunkRecord:
    now = datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)
    return ChunkRecord(
        chunk_id="test_doc::v1::chunk_0000",
        document_id="test_doc",
        document_version=1,
        chunk_index=0,
        total_chunks=1,
        text=text,
        char_count=len(text),
        category="crop_production",
        language="en",
        filename="test_doc.pdf",
        content_hash="a" * 64,
        created_at=now,
    )


def test_huggingface_embedding_generator_with_provider(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.ingestion.stages.embedding.generator.persist_embeddings",
        lambda **kwargs: None,
    )

    metadata = MetadataBundle(
        document_id="test_doc",
        document_version=1,
        chunks=[_chunk_record("Rice needs water.")],
        document_meta={"chunk_count": 1},
    )

    embedded = HuggingFaceEmbeddingGenerator(provider=_FakeProvider()).embed(metadata)

    assert embedded.embedding_model == "BAAI/bge-small-en-v1.5"
    assert embedded.dimension == 3
    assert len(embedded.chunks) == 1
    assert embedded.chunks[0].vector == [0.0, 1.0, 0.0]


def test_prepare_query_text_bge_prefix() -> None:
    prepared = prepare_query_text("BAAI/bge-small-en-v1.5", "pmfby premium")
    assert prepared.startswith(
        "Represent this sentence for searching relevant passages:"
    )
    assert prepared.endswith("pmfby premium")


def test_prepare_query_text_m3_no_prefix() -> None:
    assert prepare_query_text("BAAI/bge-m3", "pmfby premium") == "pmfby premium"
