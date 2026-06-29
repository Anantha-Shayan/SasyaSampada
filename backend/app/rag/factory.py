from __future__ import annotations

from functools import lru_cache

from app.core.exceptions import LLMError
from app.llm.providers import GroqLLMProvider
from app.rag.context import ContextBuilder
from app.rag.pipeline import RAGService
from app.rag.prompts import PromptTemplates
from app.retrieval.factory import build_similarity_retriever


@lru_cache(maxsize=1)
def build_rag_service() -> RAGService:
    from app.config import (
        GROQ_API_KEY,
        GROQ_MODEL,
        LLM_MAX_TOKENS,
        LLM_TEMPERATURE,
        PROMPT_CONFIG_PATH,
        RAG_CONTEXT_CHUNK_MAX_CHARS,
        RAG_CONTEXT_MAX_CHARS,
    )

    if not GROQ_API_KEY:
        raise LLMError("GROQ_API_KEY is not configured")

    templates = PromptTemplates.from_config_path(PROMPT_CONFIG_PATH)
    return RAGService(
        retriever=build_similarity_retriever(),
        llm=GroqLLMProvider(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        ),
        templates=templates,
        context_builder=ContextBuilder(
            templates,
            max_context_chars=RAG_CONTEXT_MAX_CHARS,
            max_chunk_chars=RAG_CONTEXT_CHUNK_MAX_CHARS,
        ),
    )
