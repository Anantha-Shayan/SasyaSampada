from __future__ import annotations

from app.core.exceptions import ChunkerError, NonRetryableError
from app.core.logging import get_logger
from app.domain.schemas.ingestion import ChunkedDocument, CleanedDocument, TextChunk

logger = get_logger(__name__)

CHUNKER_NAME = "fixed_size"


class FixedSizeChunker:
    """Legacy fixed-window chunker — retained for tests and comparison."""

    stage_name = "chunker"

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: CleanedDocument) -> ChunkedDocument:
        logger.info("Chunking %s (fixed_size)", document.document_id)

        try:
            chunks = self._split_text(document.text)
        except Exception as exc:
            raise ChunkerError(
                f"Failed to chunk document {document.document_id}",
                stage=self.stage_name,
            ) from exc

        if not chunks:
            raise NonRetryableError(f"No chunks produced for {document.document_id}")

        return ChunkedDocument(
            document_id=document.document_id,
            document_version=document.document_version,
            chunks=chunks,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            chunker_name=CHUNKER_NAME,
        )

    def _split_text(self, text: str) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        start = 0
        index = 0
        text_len = len(text)
        step = self.chunk_size - self.chunk_overlap

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(TextChunk(chunk_index=index, text=chunk_text))
                index += 1
            if end >= text_len:
                break
            start += step

        return chunks
