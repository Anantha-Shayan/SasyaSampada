from __future__ import annotations

KNOWN_EMBEDDING_DIMENSIONS: dict[str, int] = {
    "BAAI/bge-small-en-v1.5": 384,
    "BAAI/bge-m3": 1024,
}

BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def get_model_dimension(model_name: str) -> int | None:
    return KNOWN_EMBEDDING_DIMENSIONS.get(model_name)


def uses_bge_query_prefix(model_name: str) -> bool:
    """BGE English v1.5 expects an instruction prefix at query time."""
    return model_name == "BAAI/bge-small-en-v1.5"


def prepare_query_text(model_name: str, text: str) -> str:
    if uses_bge_query_prefix(model_name):
        return f"{BGE_QUERY_PREFIX}{text}"
    return text
