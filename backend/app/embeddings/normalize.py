from __future__ import annotations

import math


def l2_normalize(vector: list[float]) -> list[float]:
    """L2-normalize a vector for cosine similarity in Qdrant."""
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]
