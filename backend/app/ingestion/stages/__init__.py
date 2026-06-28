"""Ingestion stage implementations — lazy exports to avoid heavy import side effects."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ingestion.stages.chunker import FixedSizeChunker, RecursiveCharacterChunker
    from app.ingestion.stages.cleaner import AgriculturalTextCleaner, PassthroughCleaner
    from app.ingestion.stages.embedding import StubEmbeddingGenerator
    from app.ingestion.stages.loader import FileSystemLoader
    from app.ingestion.stages.metadata import DefaultMetadataGenerator, RichMetadataGenerator
    from app.ingestion.stages.parser import CompositePdfParser, PyMuPDFParser
    from app.ingestion.stages.validator import PdfValidator
    from app.ingestion.stages.vector_store import NoOpVectorStoreWriter

__all__ = [
    "FileSystemLoader",
    "PdfValidator",
    "CompositePdfParser",
    "PyMuPDFParser",
    "AgriculturalTextCleaner",
    "PassthroughCleaner",
    "RecursiveCharacterChunker",
    "FixedSizeChunker",
    "DefaultMetadataGenerator",
    "RichMetadataGenerator",
    "StubEmbeddingGenerator",
    "NoOpVectorStoreWriter",
]

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "FileSystemLoader": ("app.ingestion.stages.loader", "FileSystemLoader"),
    "PdfValidator": ("app.ingestion.stages.validator", "PdfValidator"),
    "CompositePdfParser": ("app.ingestion.stages.parser", "CompositePdfParser"),
    "PyMuPDFParser": ("app.ingestion.stages.parser", "PyMuPDFParser"),
    "AgriculturalTextCleaner": ("app.ingestion.stages.cleaner", "AgriculturalTextCleaner"),
    "PassthroughCleaner": ("app.ingestion.stages.cleaner", "PassthroughCleaner"),
    "RecursiveCharacterChunker": (
        "app.ingestion.stages.chunker",
        "RecursiveCharacterChunker",
    ),
    "FixedSizeChunker": ("app.ingestion.stages.chunker", "FixedSizeChunker"),
    "DefaultMetadataGenerator": (
        "app.ingestion.stages.metadata",
        "DefaultMetadataGenerator",
    ),
    "RichMetadataGenerator": ("app.ingestion.stages.metadata", "RichMetadataGenerator"),
    "StubEmbeddingGenerator": ("app.ingestion.stages.embedding", "StubEmbeddingGenerator"),
    "NoOpVectorStoreWriter": (
        "app.ingestion.stages.vector_store",
        "NoOpVectorStoreWriter",
    ),
}


def __getattr__(name: str) -> object:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = _LAZY_EXPORTS[name]
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, attr)
