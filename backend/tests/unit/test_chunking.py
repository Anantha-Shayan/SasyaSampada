import pytest

from app.ingestion.stages.chunker.splitters import recursive_character_split


SAMPLE_TEXT = (
    "Chapter 1: Rice Cultivation\n\n"
    "Rice requires adequate water during the kharif season. "
    "Farmers should maintain proper nursery management.\n\n"
    "Chapter 2: Wheat Production\n\n"
    "Wheat is suited for rabi season with moderate irrigation. "
    "Soil pH between 6.0 and 7.5 is ideal for wheat cultivation."
)


def test_recursive_split_respects_chunk_size() -> None:
    chunks = recursive_character_split(SAMPLE_TEXT, chunk_size=120, chunk_overlap=20)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 120


def test_recursive_split_prefers_paragraph_boundaries() -> None:
    chunks = recursive_character_split(SAMPLE_TEXT, chunk_size=200, chunk_overlap=0)
    assert any("Rice requires" in chunk for chunk in chunks)
    assert any("Wheat is suited" in chunk for chunk in chunks)


def test_recursive_split_overlap_creates_shared_context() -> None:
    chunks = recursive_character_split(SAMPLE_TEXT, chunk_size=100, chunk_overlap=30)
    if len(chunks) < 2:
        pytest.skip("text too short for overlap test")
    # Adjacent chunks should share some trailing/leading content
    assert chunks[0][-20:] in chunks[1] or chunks[1][:20] in chunks[0]


def test_recursive_split_empty_input() -> None:
    assert recursive_character_split("", chunk_size=100, chunk_overlap=20) == []


def test_recursive_split_invalid_overlap() -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        recursive_character_split("text", chunk_size=100, chunk_overlap=100)
