from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.domain.schemas.ingestion import (
    ChunkedDocument,
    CleanedDocument,
    EmbeddedChunk,
    EmbeddedDocument,
    IndexedDocument,
    LoadedDocument,
    MetadataBundle,
    ParsedDocumentArtifact,
    ParsedPage,
    TextChunk,
    ValidatedDocument,
)
from app.domain.schemas.knowledge_base import ChunkRecord, IngestionStatus
from app.ingestion.pipeline import context as pipeline_context
from app.ingestion.pipeline.runner import IngestionPipeline
from app.knowledge_base import registry as kb_registry
from app.knowledge_base.paths import DOCUMENTS_MANIFEST


@pytest.fixture()
def isolated_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    manifest = tmp_path / "documents.json"
    registry = tmp_path / "ingestion_registry.json"
    shutil.copy(DOCUMENTS_MANIFEST, manifest)
    registry.write_text('{"runs": []}\n', encoding="utf-8")

    monkeypatch.setattr(kb_registry, "DOCUMENTS_MANIFEST", manifest)
    monkeypatch.setattr(pipeline_context, "DOCUMENTS_MANIFEST", manifest)
    monkeypatch.setattr(pipeline_context, "INGESTION_REGISTRY", registry)

    def _log_path(document_id: str, run_id: str) -> Path:
        return tmp_path / "logs" / document_id / f"{run_id}.jsonl"

    monkeypatch.setattr(pipeline_context, "ingestion_log_path", _log_path)
    monkeypatch.setattr("app.ingestion.pipeline.runner.ingestion_log_path", _log_path)

    return "tnau_crop_production_guide_2020"


def _build_mock_pipeline() -> IngestionPipeline:
    entry = kb_registry.get_document("tnau_crop_production_guide_2020")
    assert entry is not None

    loaded = LoadedDocument(
        catalog=entry,
        source_path="/tmp/sample.pdf",
        content_sha256="a" * 64,
        file_size_bytes=1024,
    )
    validated = ValidatedDocument(loaded=loaded, validated_at=datetime.now(timezone.utc))
    parsed = ParsedDocumentArtifact(
        document_id=entry.document_id,
        document_version=entry.version,
        pages=[ParsedPage(page_number=1, text="sample text", char_count=11)],
        page_count=1,
        parser_name="mock",
        parser_version="0",
        parsed_at=datetime.now(timezone.utc),
        source_filename=entry.filename,
        content_sha256=loaded.content_sha256,
    )
    cleaned = CleanedDocument(
        document_id=entry.document_id,
        document_version=entry.version,
        text="sample text",
        char_count=11,
        cleaner_name="mock",
        cleaned_at=datetime.now(timezone.utc),
    )
    chunked = ChunkedDocument(
        document_id=entry.document_id,
        document_version=entry.version,
        chunks=[TextChunk(chunk_index=0, text="sample text")],
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunk_record = ChunkRecord(
        chunk_id=f"{entry.document_id}::v1::chunk_0000",
        document_id=entry.document_id,
        document_version=entry.version,
        chunk_index=0,
        total_chunks=1,
        text="sample text",
        char_count=11,
        category=entry.category,
        language=entry.language,
        filename=entry.filename,
        content_hash="b" * 64,
        created_at=datetime.now(timezone.utc),
    )
    metadata = MetadataBundle(
        document_id=entry.document_id,
        document_version=entry.version,
        chunks=[chunk_record],
        document_meta={"chunk_count": 1},
    )
    embedded = EmbeddedDocument(
        document_id=entry.document_id,
        document_version=entry.version,
        chunks=[
            EmbeddedChunk(
                chunk=chunk_record,
                vector=[0.0] * 384,
                embedding_model="stub",
            )
        ],
        embedding_model="stub",
        dimension=384,
    )
    indexed = IndexedDocument(
        document_id=entry.document_id,
        document_version=entry.version,
        chunks_indexed=1,
        collection_name="agri_knowledge",
        indexed_at=datetime.now(timezone.utc),
    )

    loader = MagicMock(stage_name="loader", load=MagicMock(return_value=loaded))
    validator = MagicMock(stage_name="validator", validate=MagicMock(return_value=validated))
    parser = MagicMock(stage_name="parser", parse=MagicMock(return_value=parsed))
    cleaner = MagicMock(stage_name="cleaner", clean=MagicMock(return_value=cleaned))
    chunker = MagicMock(stage_name="chunker", chunk=MagicMock(return_value=chunked))
    metadata_generator = MagicMock(
        stage_name="metadata",
        generate=MagicMock(return_value=metadata),
    )
    embedder = MagicMock(stage_name="embedder", embed=MagicMock(return_value=embedded))
    vector_store = MagicMock(stage_name="vector_store", upsert=MagicMock(return_value=indexed))

    return IngestionPipeline(
        loader=loader,
        validator=validator,
        parser=parser,
        cleaner=cleaner,
        chunker=chunker,
        metadata_generator=metadata_generator,
        embedder=embedder,
        vector_store=vector_store,
    )


def test_pipeline_runs_all_stages(isolated_manifest: str) -> None:
    pipeline = _build_mock_pipeline()
    result = pipeline.run(isolated_manifest)

    assert result.success is True
    assert len(result.stages_completed) == 8
    assert result.indexed is not None
    assert result.indexed.chunks_indexed == 1

    entry = kb_registry.get_document(isolated_manifest)
    assert entry is not None
    assert entry.ingestion_status == IngestionStatus.INDEXED
    assert entry.chunk_count == 1


def test_pipeline_rejects_missing_document(isolated_manifest: str) -> None:
    pipeline = _build_mock_pipeline()
    result = pipeline.run("does_not_exist")
    assert result.success is False
    assert "not in catalog" in (result.error or "")
