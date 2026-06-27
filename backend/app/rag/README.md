# `app/rag`

Assembles the full RAG pipeline (Phase 12).

**Components:**

- `RAGService` — main orchestrator
- `ContextBuilder` — formats retrieved chunks for the prompt
- `PromptTemplates` — system, user, citation, guard prompts (Phase 11)
- `CitationExtractor` — maps answer spans to source chunks

Depends on: `retrieval`, `llm`, `embeddings`, `core.logging`.

Does **not** depend on FastAPI (testable in isolation).
