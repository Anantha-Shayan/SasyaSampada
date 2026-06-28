from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

from app.core.exceptions import IngestionError, NonRetryableError, SasyaSampadaError
from app.core.logging import IngestionLogWriter, get_logger
from app.domain.schemas.knowledge_base import IngestionStatus, LifecycleStatus
from app.ingestion.interfaces import (
    DocumentChunker,
    DocumentCleaner,
    DocumentLoader,
    DocumentParser,
    DocumentValidator,
    EmbeddingGenerator,
    MetadataGenerator,
    VectorStoreWriter,
)
from app.ingestion.pipeline.context import (
    IngestionContext,
    IngestionResult,
    _append_registry_run,
    _update_catalog_entry,
)
from app.ingestion.retry import with_ingestion_retry
from app.knowledge_base.paths import ingestion_log_path
from app.knowledge_base.registry import get_document, iter_active_documents

logger = get_logger(__name__)

T = TypeVar("T")
R = TypeVar("R")

STAGE_STATUS_MAP = {
    "loader": IngestionStatus.PENDING,
    "validator": IngestionStatus.PENDING,
    "parser": IngestionStatus.PARSING,
    "cleaner": IngestionStatus.CLEANING,
    "chunker": IngestionStatus.CHUNKING,
    "metadata": IngestionStatus.CHUNKING,
    "embedder": IngestionStatus.EMBEDDING,
    "vector_store": IngestionStatus.INDEXING,
}


class IngestionPipeline:
    """Orchestrates independent ingestion stages with logging and manifest updates."""

    def __init__(
        self,
        loader: DocumentLoader,
        validator: DocumentValidator,
        parser: DocumentParser,
        cleaner: DocumentCleaner,
        chunker: DocumentChunker,
        metadata_generator: MetadataGenerator,
        embedder: EmbeddingGenerator,
        vector_store: VectorStoreWriter,
    ) -> None:
        self._loader = loader
        self._validator = validator
        self._parser = parser
        self._cleaner = cleaner
        self._chunker = chunker
        self._metadata_generator = metadata_generator
        self._embedder = embedder
        self._vector_store = vector_store

        self._stages: list[tuple[str, Callable[[IngestionContext, Any], Any]]] = [
            ("loader", self._run_loader),
            ("validator", self._run_validator),
            ("parser", self._run_parser),
            ("cleaner", self._run_cleaner),
            ("chunker", self._run_chunker),
            ("metadata", self._run_metadata),
            ("embedder", self._run_embedder),
            ("vector_store", self._run_vector_store),
        ]

    def run(self, document_id: str) -> IngestionResult:
        started = time.perf_counter()
        entry = get_document(document_id)

        if entry is None:
            return IngestionResult(
                success=False,
                document_id=document_id,
                run_id="",
                stages_completed=[],
                error=f"Document not in catalog: {document_id}",
            )

        if entry.lifecycle_status == LifecycleStatus.DELETED:
            return IngestionResult(
                success=False,
                document_id=document_id,
                run_id="",
                stages_completed=[],
                error=f"Document is deleted: {document_id}",
            )

        if entry.duplicate_of:
            return IngestionResult(
                success=False,
                document_id=document_id,
                run_id="",
                stages_completed=[],
                error=f"Document is duplicate of {entry.duplicate_of}",
            )

        ctx = IngestionContext(document_id=document_id, catalog_entry=entry)
        ctx.log_writer = IngestionLogWriter(ingestion_log_path(document_id, ctx.run_id))
        ctx.log_writer.write("run_started", document_version=entry.version)

        current: Any = entry

        try:
            for stage_name, stage_fn in self._stages:
                status = STAGE_STATUS_MAP.get(stage_name)
                if status:
                    entry = _update_catalog_entry(document_id, ingestion_status=status)
                    ctx.catalog_entry = entry

                ctx.log_writer.write("stage_started", stage=stage_name)
                stage_started = time.perf_counter()
                current = self._execute_stage(stage_name, stage_fn, ctx, current)
                duration_ms = int((time.perf_counter() - stage_started) * 1000)
                ctx.stages_completed.append(stage_name)
                ctx.log_writer.write(
                    "stage_completed",
                    stage=stage_name,
                    duration_ms=duration_ms,
                )
                logger.info(
                    "Stage %s completed for %s in %dms",
                    stage_name,
                    document_id,
                    duration_ms,
                )

            indexed = current
            current_entry = get_document(document_id)
            _update_catalog_entry(
                document_id,
                ingestion_status=IngestionStatus.INDEXED,
                page_count=current_entry.page_count if current_entry else None,
                chunk_count=indexed.chunks_indexed,
                embedding_model=current_entry.embedding_model if current_entry else None,
                indexed=True,
            )

            _append_registry_run(
                document_id,
                entry.version,
                ctx.run_id,
                "success",
                ctx.stages_completed,
            )
            ctx.log_writer.write("run_completed", success=True)

            return IngestionResult(
                success=True,
                document_id=document_id,
                run_id=ctx.run_id,
                stages_completed=ctx.stages_completed,
                indexed=indexed,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )

        except (IngestionError, NonRetryableError, SasyaSampadaError) as exc:
            error_message = str(exc)
            stage = getattr(exc, "stage", None)
            logger.exception("Ingestion failed for %s at stage %s", document_id, stage)
            _update_catalog_entry(
                document_id,
                ingestion_status=IngestionStatus.FAILED,
                last_error=error_message,
            )
            _append_registry_run(
                document_id,
                entry.version,
                ctx.run_id,
                "failed",
                ctx.stages_completed,
                error=error_message,
            )
            if ctx.log_writer:
                ctx.log_writer.write("run_failed", error=error_message, stage=stage)
            return IngestionResult(
                success=False,
                document_id=document_id,
                run_id=ctx.run_id,
                stages_completed=ctx.stages_completed,
                error=error_message,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )

    def run_all_active(self) -> list[IngestionResult]:
        return [self.run(entry.document_id) for entry in iter_active_documents()]

    def _execute_stage(
        self,
        stage_name: str,
        stage_fn: Callable[[IngestionContext, Any], R],
        ctx: IngestionContext,
        current: Any,
    ) -> R:
        if stage_name in {"embedder", "vector_store"}:
            wrapped = with_ingestion_retry(stage_fn)
            return wrapped(ctx, current)
        return stage_fn(ctx, current)

    def _run_loader(self, ctx: IngestionContext, entry: Any) -> Any:
        loaded = self._loader.load(entry)
        _update_catalog_entry(
            entry.document_id,
            content_sha256=loaded.content_sha256,
            file_size_bytes=loaded.file_size_bytes,
        )
        return loaded

    def _run_validator(self, ctx: IngestionContext, loaded: Any) -> Any:
        return self._validator.validate(loaded)

    def _run_parser(self, ctx: IngestionContext, validated: Any) -> Any:
        parsed = self._parser.parse(validated)
        _update_catalog_entry(ctx.document_id, page_count=parsed.page_count)
        return parsed

    def _run_cleaner(self, ctx: IngestionContext, parsed: Any) -> Any:
        return self._cleaner.clean(parsed)

    def _run_chunker(self, ctx: IngestionContext, cleaned: Any) -> Any:
        return self._chunker.chunk(cleaned)

    def _run_metadata(self, ctx: IngestionContext, chunked: Any) -> Any:
        assert ctx.catalog_entry is not None
        bundle = self._metadata_generator.generate(chunked, ctx.catalog_entry)
        _update_catalog_entry(ctx.document_id, chunk_count=len(bundle.chunks))
        return bundle

    def _run_embedder(self, ctx: IngestionContext, metadata: Any) -> Any:
        embedded = self._embedder.embed(metadata)
        _update_catalog_entry(ctx.document_id, embedding_model=embedded.embedding_model)
        return embedded

    def _run_vector_store(self, ctx: IngestionContext, embedded: Any) -> Any:
        return self._vector_store.upsert(embedded)
