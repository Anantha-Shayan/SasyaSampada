from __future__ import annotations

from app.domain.schemas.rag import AskRequest, SearchRequest
from app.domain.schemas.retrieval import RetrievedChunk, RetrievalResult
from app.llm.base import LLMMessage, LLMResponse
from app.rag.context import ContextBuilder
from app.rag.pipeline import RAGService
from app.rag.prompts import PromptTemplates


class FakeRetriever:
    def retrieve(self, query, *, filters=None):
        return RetrievalResult(
            query=query,
            chunks=[
                RetrievedChunk(
                    chunk_id="doc::v1::chunk_0000",
                    document_id="doc",
                    document_version=1,
                    chunk_index=0,
                    text="Rice should be transplanted with adequate irrigation.",
                    score=0.92,
                    category="crop_production",
                    language="en",
                    filename="doc.pdf",
                    page_start=3,
                )
            ],
            top_k=10,
            score_threshold=0.0,
            embedding_model="fake",
            filters_applied=filters,
        )


class FakeLLM:
    model_name = "fake-llm"

    def __init__(self) -> None:
        self.messages: list[LLMMessage] = []

    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        self.messages = messages
        return LLMResponse(
            content="Use adequate irrigation for rice transplanting. [1]",
            model=self.model_name,
        )


def _service(llm: FakeLLM) -> RAGService:
    templates = PromptTemplates()
    return RAGService(
        retriever=FakeRetriever(),
        llm=llm,
        templates=templates,
        context_builder=ContextBuilder(templates),
    )


def test_search_returns_citations() -> None:
    response = _service(FakeLLM()).search(SearchRequest(query="rice irrigation"))

    assert response.success is True
    assert len(response.chunks) == 1
    assert response.citations[0].citation_id == 1
    assert response.citations[0].page_start == 3


def test_ask_assembles_prompt_and_answer() -> None:
    llm = FakeLLM()
    response = _service(llm).ask(AskRequest(query="How should I irrigate rice?"))

    assert response.answer.endswith("[1]")
    assert response.model == "fake-llm"
    assert "Retrieved context" in llm.messages[1].content
    assert "[1]" in llm.messages[1].content
