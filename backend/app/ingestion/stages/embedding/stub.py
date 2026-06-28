from __future__ import annotations

from app.core.logging import get_logger
from app.domain.schemas.ingestion import EmbeddedChunk, EmbeddedDocument, MetadataBundle

logger = get_logger(__name__)

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
STUB_DIMENSION = 384


class StubEmbeddingGenerator:
    """
    Placeholder embedding stage — produces zero vectors of correct dimension.

    Retained for pipeline tests and environments without sentence-transformers.
    """

    stage_name = "embedder"

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        dimension: int = STUB_DIMENSION,
    ) -> None:
        self.model_name = model_name
        self.dimension = dimension

    def embed(self, metadata: MetadataBundle) -> EmbeddedDocument:
        logger.info(
            "Embedding %d chunks for %s (stub)",
            len(metadata.chunks),
            metadata.document_id,
        )

        embedded_chunks = [
            EmbeddedChunk(
                chunk=record,
                vector=[0.0] * self.dimension,
                embedding_model=self.model_name,
            )
            for record in metadata.chunks
        ]

        return EmbeddedDocument(
            document_id=metadata.document_id,
            document_version=metadata.document_version,
            chunks=embedded_chunks,
            embedding_model=self.model_name,
            dimension=self.dimension,
        )
