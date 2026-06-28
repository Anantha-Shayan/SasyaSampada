"""Domain exception hierarchy for the RAG subsystem."""


class SasyaSampadaError(Exception):
    """Base exception for all application errors."""


class RetryableError(SasyaSampadaError):
    """Transient failure — safe to retry with backoff."""


class NonRetryableError(SasyaSampadaError):
    """Permanent failure — do not retry."""


class IngestionError(SasyaSampadaError):
    """Base for ingestion pipeline failures."""

    def __init__(self, message: str, *, stage: str | None = None) -> None:
        super().__init__(message)
        self.stage = stage


class LoaderError(IngestionError):
    """Failed to load raw document bytes."""


class ValidationError(IngestionError):
    """Document failed validation checks."""


class ParserError(IngestionError):
    """PDF parsing failed."""


class CleanerError(IngestionError):
    """Text cleaning failed."""


class ChunkerError(IngestionError):
    """Chunking failed."""


class MetadataError(IngestionError):
    """Metadata generation failed."""


class EmbeddingError(IngestionError):
    """Embedding generation failed."""


class VectorStoreError(IngestionError):
    """Vector database write failed."""


class RetryableIngestionError(RetryableError, IngestionError):
    """Ingestion stage failed transiently (network, rate limit)."""
