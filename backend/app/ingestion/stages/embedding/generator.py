from __future__ import annotations

from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger
from app.domain.schemas.ingestion import EmbeddedChunk, EmbeddedDocument, MetadataBundle
from app.embeddings.base import EmbeddingProvider
from app.embeddings.providers import HuggingFaceEmbeddingProvider
from app.ingestion.stages.embedding.persist import persist_embeddings

logger = get_logger(__name__)

EMBEDDING_GENERATOR_NAME = "huggingface_bge"


class HuggingFaceEmbeddingGenerator:
    """
    Ingestion embedder stage — delegates to app/embeddings and persists vectors.

    Document passages are embedded without query prefixes; BGE query prefixes
    are applied only in embed_query() at retrieval time (Phase 10).
    """

    stage_name = "embedder"

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
        *,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        normalize: bool | None = None,
    ) -> None:
        from app.config import (
            EMBEDDING_BATCH_SIZE,
            EMBEDDING_DEVICE,
            EMBEDDING_MODEL,
            EMBEDDING_NORMALIZE,
        )

        resolved_model = model_name or EMBEDDING_MODEL
        resolved_device = device or EMBEDDING_DEVICE
        resolved_batch_size = batch_size if batch_size is not None else EMBEDDING_BATCH_SIZE
        resolved_normalize = (
            EMBEDDING_NORMALIZE if normalize is None else normalize
        )

        self._batch_size = resolved_batch_size
        self._normalize = resolved_normalize
        self._provider = provider or HuggingFaceEmbeddingProvider(
            resolved_model,
            device=resolved_device,
            batch_size=resolved_batch_size,
            normalize=resolved_normalize,
        )

    @property
    def model_name(self) -> str:
        return self._provider.model_name

    def embed(self, metadata: MetadataBundle) -> EmbeddedDocument:
        logger.info(
            "Embedding %d chunks for %s with %s",
            len(metadata.chunks),
            metadata.document_id,
            self.model_name,
        )

        try:
            texts = [record.text for record in metadata.chunks]
            vectors = self._provider.embed_documents(texts)
            dimension = self._provider.dimension

            if len(vectors) != len(metadata.chunks):
                raise EmbeddingError(
                    f"Vector count mismatch for {metadata.document_id}: "
                    f"expected {len(metadata.chunks)}, got {len(vectors)}",
                    stage=self.stage_name,
                )

            embedded_chunks = [
                EmbeddedChunk(
                    chunk=record,
                    vector=vector,
                    embedding_model=self.model_name,
                )
                for record, vector in zip(metadata.chunks, vectors, strict=True)
            ]

            persist_embeddings(
                document_id=metadata.document_id,
                document_version=metadata.document_version,
                embedding_model=self.model_name,
                dimension=dimension,
                vectors=[(record.chunk_id, vector) for record, vector in zip(
                    metadata.chunks, vectors, strict=True
                )],
                batch_size=self._batch_size,
                normalize=self._normalize,
            )

            return EmbeddedDocument(
                document_id=metadata.document_id,
                document_version=metadata.document_version,
                chunks=embedded_chunks,
                embedding_model=self.model_name,
                dimension=dimension,
            )
        except EmbeddingError:
            raise
        except Exception as exc:
            raise EmbeddingError(
                f"Failed to embed document {metadata.document_id}",
                stage=self.stage_name,
            ) from exc
