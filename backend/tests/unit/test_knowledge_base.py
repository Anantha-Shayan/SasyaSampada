import pytest

from app.knowledge_base.paths import (
    chunks_jsonl_path,
    cleaned_text_path,
    embedding_model_slug,
    make_chunk_id,
    parse_chunk_id,
    parsed_json_path,
    raw_pdf_path,
)
from app.knowledge_base.registry import load_catalog


def test_make_and_parse_chunk_id() -> None:
    chunk_id = make_chunk_id("tnau_crop_production_guide_2020", 2, 15)
    assert chunk_id == "tnau_crop_production_guide_2020::v2::chunk_0015"
    doc_id, version, index = parse_chunk_id(chunk_id)
    assert doc_id == "tnau_crop_production_guide_2020"
    assert version == 2
    assert index == 15


def test_versioned_paths() -> None:
    raw = raw_pdf_path("guide.pdf")
    assert raw.name == "guide.pdf"
    assert raw.parent.name == "raw"

    parsed = parsed_json_path("doc_a", 3)
    assert parsed.parts[-3:] == ("doc_a", "v3", "parsed.json")
    assert cleaned_text_path("doc_a", 3).name == "cleaned.txt"
    assert chunks_jsonl_path("doc_a", 3).name == "chunks.jsonl"


def test_embedding_model_slug() -> None:
    assert embedding_model_slug("BAAI/bge-small-en-v1.5") == "BAAI_bge_small_en_v1_5"


def test_load_catalog_validates_manifest() -> None:
    catalog = load_catalog()
    assert len(catalog) >= 1
    assert catalog[0].document_id
    assert catalog[0].ingestion_status.value == "pending"
