from __future__ import annotations

import re

from app.domain.schemas.rag import Citation
from app.domain.schemas.retrieval import RetrievedChunk
from app.rag.prompts import PromptTemplates

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_PROMPT_INJECTION_HINTS = re.compile(
    r"(ignore previous instructions|system prompt|developer message)",
    flags=re.IGNORECASE,
)


class ContextBuilder:
    """Build citation-tagged, sanitized context for prompt assembly."""

    def __init__(
        self,
        templates: PromptTemplates,
        *,
        max_context_chars: int = 6000,
        max_chunk_chars: int = 1200,
    ) -> None:
        self._templates = templates
        self._max_context_chars = max_context_chars
        self._max_chunk_chars = max_chunk_chars

    def build(self, chunks: list[RetrievedChunk], citations: list[Citation]) -> str:
        citation_by_chunk = {
            chunk.chunk_id: citation
            for chunk, citation in zip(chunks, citations, strict=False)
        }
        parts: list[str] = []
        current_size = 0

        for chunk in chunks:
            citation = citation_by_chunk.get(chunk.chunk_id)
            if citation is None:
                continue
            text = self._sanitize(chunk.text)
            if len(text) > self._max_chunk_chars:
                text = text[: self._max_chunk_chars].rstrip() + "..."
            rendered = self._templates.render_context_item(citation=citation, text=text)
            if current_size + len(rendered) > self._max_context_chars:
                break
            parts.append(rendered)
            current_size += len(rendered)

        return "\n\n".join(parts)

    @staticmethod
    def _sanitize(text: str) -> str:
        cleaned = _CONTROL_CHARS.sub(" ", text)
        cleaned = _PROMPT_INJECTION_HINTS.sub("[redacted instruction-like text]", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()
