from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.schemas.ingestion import (
    ChunkedDocument,
    CleanedDocument,
    EmbeddedDocument,
    IndexedDocument,
    LoadedDocument,
    MetadataBundle,
    ParsedDocumentArtifact,
    ValidatedDocument,
)
from app.domain.schemas.knowledge_base import DocumentCatalogEntry


@runtime_checkable
class DocumentLoader(Protocol):
    stage_name: str

    def load(self, entry: DocumentCatalogEntry) -> LoadedDocument: ...


@runtime_checkable
class DocumentValidator(Protocol):
    stage_name: str

    def validate(self, document: LoadedDocument) -> ValidatedDocument: ...


@runtime_checkable
class DocumentParser(Protocol):
    stage_name: str

    def parse(self, document: ValidatedDocument) -> ParsedDocumentArtifact: ...


@runtime_checkable
class DocumentCleaner(Protocol):
    stage_name: str

    def clean(self, parsed: ParsedDocumentArtifact) -> CleanedDocument: ...


@runtime_checkable
class DocumentChunker(Protocol):
    stage_name: str

    def chunk(self, document: CleanedDocument) -> ChunkedDocument: ...


@runtime_checkable
class MetadataGenerator(Protocol):
    stage_name: str

    def generate(
        self,
        chunked: ChunkedDocument,
        catalog: DocumentCatalogEntry,
    ) -> MetadataBundle: ...


@runtime_checkable
class EmbeddingGenerator(Protocol):
    stage_name: str

    def embed(self, metadata: MetadataBundle) -> EmbeddedDocument: ...


@runtime_checkable
class VectorStoreWriter(Protocol):
    stage_name: str

    def upsert(self, embedded: EmbeddedDocument) -> IndexedDocument: ...
