from __future__ import annotations

import time
from datetime import datetime, timezone

from app.core.exceptions import LLMError, RAGError, RetrievalError
from app.core.logging import get_logger
from app.core.observability import current_request_id, metrics_registry
from app.domain.schemas.rag import AskRequest, AskResponse, RAGTimings, SearchRequest, SearchResponse
from app.llm.base import LLMMessage, LLMProvider
from app.rag.citations import citations_from_chunks
from app.rag.context import ContextBuilder
from app.rag.prompts import PromptTemplates
from app.retrieval.base import Retriever

logger = get_logger(__name__)


class RAGService:
    """End-to-end query orchestration: retrieve, build prompt, call LLM, cite."""

    def __init__(
        self,
        *,
        retriever: Retriever,
        llm: LLMProvider,
        templates: PromptTemplates,
        context_builder: ContextBuilder,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._templates = templates
        self._context_builder = context_builder

    def search(self, request: SearchRequest) -> SearchResponse:
        started = time.perf_counter()
        try:
            retrieval = self._retriever.retrieve(request.query, filters=request.filters)
            chunks = retrieval.chunks
            if request.top_k is not None:
                chunks = chunks[: request.top_k]
            if request.score_threshold is not None:
                chunks = [
                    chunk for chunk in chunks if chunk.score >= request.score_threshold
                ]
            citations = citations_from_chunks(chunks)
            latency_ms = (time.perf_counter() - started) * 1000
            metrics_registry.increment("rag_search_total")
            metrics_registry.observe_latency("retrieval_total_ms", latency_ms)
            return SearchResponse(
                query=retrieval.query,
                chunks=chunks,
                citations=citations,
                latency_ms=round(latency_ms, 3),
                request_id=current_request_id(),
            )
        except RetrievalError:
            metrics_registry.increment("rag_search_errors_total")
            raise
        except Exception as exc:
            metrics_registry.increment("rag_search_errors_total")
            raise RAGError("Search failed") from exc

    def ask(self, request: AskRequest) -> AskResponse:
        total_started = time.perf_counter()
        retrieval_ms = context_ms = llm_ms = 0.0
        try:
            retrieval_started = time.perf_counter()
            search_response = self.search(request)
            retrieval_ms = (time.perf_counter() - retrieval_started) * 1000

            if not search_response.chunks:
                total_ms = (time.perf_counter() - total_started) * 1000
                return AskResponse(
                    answer=self._templates.insufficient_context_message,
                    citations=[],
                    retrieved_chunks=[],
                    timings=RAGTimings(
                        retrieval_ms=round(retrieval_ms, 3),
                        total_ms=round(total_ms, 3),
                    ),
                    model=self._llm.model_name,
                    request_id=current_request_id(),
                    created_at=datetime.now(timezone.utc),
                )

            context_started = time.perf_counter()
            context = self._context_builder.build(
                search_response.chunks,
                search_response.citations,
            )
            context_ms = (time.perf_counter() - context_started) * 1000

            messages = [
                LLMMessage(role="system", content=self._templates.system_prompt),
                LLMMessage(
                    role="user",
                    content=self._templates.render_user_prompt(
                        question=request.query,
                        context=context,
                        language=request.language,
                    ),
                ),
            ]

            llm_started = time.perf_counter()
            llm_response = self._llm.generate(messages)
            llm_ms = (time.perf_counter() - llm_started) * 1000
            total_ms = (time.perf_counter() - total_started) * 1000

            metrics_registry.increment("rag_ask_total")
            metrics_registry.observe_latency("llm_total_ms", llm_ms)
            logger.info(
                "RAG answer generated chunks=%d retrieval_ms=%.2f llm_ms=%.2f",
                len(search_response.chunks),
                retrieval_ms,
                llm_ms,
            )
            return AskResponse(
                answer=llm_response.content,
                citations=search_response.citations,
                retrieved_chunks=search_response.chunks,
                timings=RAGTimings(
                    retrieval_ms=round(retrieval_ms, 3),
                    context_ms=round(context_ms, 3),
                    llm_ms=round(llm_ms, 3),
                    total_ms=round(total_ms, 3),
                ),
                model=llm_response.model,
                request_id=current_request_id(),
                created_at=datetime.now(timezone.utc),
            )
        except (RetrievalError, LLMError):
            metrics_registry.increment("rag_ask_errors_total")
            raise
        except Exception as exc:
            metrics_registry.increment("rag_ask_errors_total")
            raise RAGError("RAG pipeline failed") from exc
