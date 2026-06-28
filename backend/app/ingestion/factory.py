from __future__ import annotations

from app.ingestion.pipeline.runner import IngestionPipeline
from app.config import CHUNK_OVERLAP, CHUNK_SIZE
from app.ingestion.stages import (
    AgriculturalTextCleaner,
    CompositePdfParser,
    DefaultMetadataGenerator,
    FileSystemLoader,
    RecursiveCharacterChunker,
    NoOpVectorStoreWriter,
    PassthroughCleaner,
    PyMuPDFParser,
    PdfValidator,
    StubEmbeddingGenerator,
)


def build_default_pipeline(
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> IngestionPipeline:
    """Construct the default ingestion pipeline with stub embedder and vector store."""
    return IngestionPipeline(
        loader=FileSystemLoader(),
        validator=PdfValidator(),
        parser=CompositePdfParser(),
        cleaner=AgriculturalTextCleaner(),
        chunker=RecursiveCharacterChunker(
            chunk_size=chunk_size or CHUNK_SIZE,
            chunk_overlap=chunk_overlap or CHUNK_OVERLAP,
        ),
        metadata_generator=DefaultMetadataGenerator(),
        embedder=StubEmbeddingGenerator(),
        vector_store=NoOpVectorStoreWriter(),
    )
