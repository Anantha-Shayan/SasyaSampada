from __future__ import annotations

from app.core.exceptions import ChunkerError, NonRetryableError
from app.core.logging import get_logger
from app.domain.schemas.ingestion import ChunkedDocument, CleanedDocument, TextChunk
from app.ingestion.stages.chunker.splitters import recursive_character_split

logger = get_logger(__name__)

CHUNKER_NAME = "recursive_character"


class RecursiveCharacterChunker:
    """
    Recursive character text splitter — respects paragraph, line, and sentence boundaries.

    Same algorithm as LangChain RecursiveCharacterTextSplitter; implemented natively
    to keep the chunker testable without framework coupling.
    """

    stage_name = "chunker"

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: CleanedDocument) -> ChunkedDocument:
        logger.info(
            "Chunking %s with %s (size=%d overlap=%d)",
            document.document_id,
            CHUNKER_NAME,
            self.chunk_size,
            self.chunk_overlap,
        )

        try:
            pieces = recursive_character_split(
                document.text,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            chunks = [
                TextChunk(chunk_index=index, text=piece)
                for index, piece in enumerate(pieces)
            ]
        except Exception as exc:
            raise ChunkerError(
                f"Failed to chunk document {document.document_id}",
                stage=self.stage_name,
            ) from exc

        if not chunks:
            raise NonRetryableError(f"No chunks produced for {document.document_id}")

        logger.info("Produced %d chunks for %s", len(chunks), document.document_id)

        return ChunkedDocument(
            document_id=document.document_id,
            document_version=document.document_version,
            chunks=chunks,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            chunker_name=CHUNKER_NAME,
        )
