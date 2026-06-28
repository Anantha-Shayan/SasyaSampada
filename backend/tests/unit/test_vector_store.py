from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.domain.schemas.ingestion import EmbeddedChunk, EmbeddedDocument
from app.domain.schemas.knowledge_base import ChunkRecord
from app.ingestion.stages.vector_store.qdrant import QdrantVectorStoreWriter
from app.vector_db.qdrant.payload import chunk_record_to_payload
from app.vector_db.qdrant.point_ids import chunk_id_to_point_id
from app.vector_db.qdrant.store import QdrantVectorStore


def test_chunk_id_to_point_id_is_stable() -> None:
    chunk_id = "tnau_crop_production_guide_2020::v1::chunk_0001"
    first = chunk_id_to_point_id(chunk_id)
    second = chunk_id_to_point_id(chunk_id)
    assert first == second
    assert len(first) == 36


def test_chunk_record_to_payload_includes_filters() -> None:
    now = datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)
    record = ChunkRecord(
        chunk_id="test_doc::v1::chunk_0000",
        document_id="test_doc",
        document_version=1,
        chunk_index=0,
        total_chunks=1,
        text="Rice needs water.",
        category="crop_production",
        language="en",
        filename="test_doc.pdf",
        content_hash="a" * 64,
        page_start=3,
        section_title="Rice",
        year=2025,
        created_at=now,
    )

    payload = chunk_record_to_payload(record, embedding_model="BAAI/bge-small-en-v1.5")

    assert payload["document_id"] == "test_doc"
    assert payload["category"] == "crop_production"
    assert payload["page_start"] == 3
    assert payload["text"] == "Rice needs water."
    assert payload["embedding_model"] == "BAAI/bge-small-en-v1.5"


def _embedded_document() -> EmbeddedDocument:
    now = datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)
    record = ChunkRecord(
        chunk_id="test_doc::v1::chunk_0000",
        document_id="test_doc",
        document_version=1,
        chunk_index=0,
        total_chunks=1,
        text="Rice needs water.",
        category="crop_production",
        language="en",
        filename="test_doc.pdf",
        content_hash="a" * 64,
        created_at=now,
    )
    return EmbeddedDocument(
        document_id="test_doc",
        document_version=1,
        chunks=[
            EmbeddedChunk(
                chunk=record,
                vector=[0.1, 0.2, 0.3],
                embedding_model="BAAI/bge-small-en-v1.5",
            )
        ],
        embedding_model="BAAI/bge-small-en-v1.5",
        dimension=3,
    )


def test_qdrant_vector_store_upsert_batches() -> None:
    client = MagicMock()
    client.collection_exists.return_value = False

    store = QdrantVectorStore(client, "agri_knowledge", upsert_batch_size=1)
    count = store.upsert_document(_embedded_document())

    assert count == 1
    client.create_collection.assert_called_once()
    client.delete.assert_called_once()
    client.upsert.assert_called_once()
    point = client.upsert.call_args.kwargs["points"][0]
    assert point.id == chunk_id_to_point_id("test_doc::v1::chunk_0000")
    assert point.payload["document_id"] == "test_doc"


def test_qdrant_vector_store_writer_delegates_to_store() -> None:
    store = MagicMock()
    store.collection_name = "agri_knowledge"
    store.upsert_document.return_value = 1

    indexed = QdrantVectorStoreWriter(store=store).upsert(_embedded_document())

    assert indexed.chunks_indexed == 1
    assert indexed.collection_name == "agri_knowledge"
    store.upsert_document.assert_called_once()
