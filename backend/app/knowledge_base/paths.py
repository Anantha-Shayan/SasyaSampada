from __future__ import annotations

import re
from pathlib import Path

from app.config import DATA_DIR

RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
LOGS_DIR = DATA_DIR / "logs"
MANIFESTS_DIR = DATA_DIR / "manifests"

DOCUMENTS_MANIFEST = MANIFESTS_DIR / "documents.json"
INGESTION_REGISTRY = MANIFESTS_DIR / "ingestion_registry.json"
CATEGORIES_FILE = MANIFESTS_DIR / "categories.json"

CHUNK_ID_PATTERN = re.compile(
    r"^(?P<document_id>[a-z0-9][a-z0-9_]{2,127})::v(?P<version>\d+)::chunk_(?P<index>\d{4})$"
)


def embedding_model_slug(model_name: str) -> str:
    """Convert HuggingFace model id to safe directory name."""
    return model_name.replace("/", "_").replace("-", "_").replace(".", "_")


def raw_pdf_path(filename: str) -> Path:
    return RAW_DIR / filename


def parsed_json_path(document_id: str, version: int) -> Path:
    return PARSED_DIR / document_id / f"v{version}" / "parsed.json"


def cleaned_text_path(document_id: str, version: int) -> Path:
    return PROCESSED_DIR / document_id / f"v{version}" / "cleaned.txt"


def chunks_jsonl_path(document_id: str, version: int) -> Path:
    return METADATA_DIR / document_id / f"v{version}" / "chunks.jsonl"


def document_meta_path(document_id: str, version: int) -> Path:
    return METADATA_DIR / document_id / f"v{version}" / "document_meta.json"


def embeddings_dir(document_id: str, version: int, embedding_model: str) -> Path:
    return EMBEDDINGS_DIR / document_id / f"v{version}" / embedding_model_slug(embedding_model)


def ingestion_log_path(document_id: str, run_id: str) -> Path:
    return LOGS_DIR / document_id / f"{run_id}.jsonl"


def make_chunk_id(document_id: str, version: int, chunk_index: int) -> str:
    return f"{document_id}::v{version}::chunk_{chunk_index:04d}"


def parse_chunk_id(chunk_id: str) -> tuple[str, int, int]:
    match = CHUNK_ID_PATTERN.match(chunk_id)
    if not match:
        raise ValueError(f"Invalid chunk_id format: {chunk_id}")
    return (
        match.group("document_id"),
        int(match.group("version")),
        int(match.group("index")),
    )
