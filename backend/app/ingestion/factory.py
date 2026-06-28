from __future__ import annotations

from app.ingestion.pipeline.runner import IngestionPipeline
from app.ingestion.stages import (
    CompositePdfParser,
    DefaultMetadataGenerator,
    FileSystemLoader,
    FixedSizeChunker,
    NoOpVectorStoreWriter,
    PassthroughCleaner,
    PyMuPDFParser,
    PdfValidator,
    StubEmbeddingGenerator,
)


def build_default_pipeline(
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> IngestionPipeline:
    """Construct the default ingestion pipeline with stub embedder and vector store."""
    return IngestionPipeline(
        loader=FileSystemLoader(),
        validator=PdfValidator(),
        parser=CompositePdfParser(),
        cleaner=PassthroughCleaner(),
        chunker=FixedSizeChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap),
        metadata_generator=DefaultMetadataGenerator(),
        embedder=StubEmbeddingGenerator(),
        vector_store=NoOpVectorStoreWriter(),
    )
