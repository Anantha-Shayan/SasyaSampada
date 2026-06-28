from __future__ import annotations

from app.embeddings.normalize import l2_normalize
from app.embeddings.registry import (
    get_model_dimension,
    prepare_query_text,
)


class HuggingFaceEmbeddingProvider:
    """Local inference via sentence-transformers (BGE models)."""

    def __init__(
        self,
        model_name: str,
        *,
        device: str = "cpu",
        batch_size: int = 32,
        normalize: bool = True,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.normalize = normalize
        self._model = None
        self._dimension: int | None = get_model_dimension(model_name)

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = int(self._get_model().get_sentence_embedding_dimension())
        return self._dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._encode(texts)
        if self.normalize:
            return [l2_normalize(vector) for vector in vectors]
        return vectors

    def embed_query(self, text: str) -> list[float]:
        query = prepare_query_text(self.model_name, text)
        vector = self._encode([query])[0]
        return l2_normalize(vector) if self.normalize else vector

    def _encode(self, texts: list[str]) -> list[list[float]]:
        encoded = self._get_model().encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=False,
        )
        return [row.tolist() for row in encoded]

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model
