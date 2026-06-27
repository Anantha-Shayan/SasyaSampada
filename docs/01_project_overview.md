# 01 — Project Overview

## 1. Purpose

Define the scope, goals, and current state of **SasyaSampada** as it evolves from a farmer advisory web application into a **production-grade Retrieval Augmented Generation (RAG)** system suitable for Senior AI Engineering review.

## 2. Problem Being Solved

Indian farmers need trustworthy, domain-specific agricultural guidance (crop selection, pest management, government schemes, natural farming) in local languages. Generic LLMs hallucinate policy details, regional practices, and subsidy rules. A RAG layer grounds answers in curated PDFs from TNAU, ICAR, MANAGE, and government ministries already collected in this repository.

**Secondary problem:** The existing codebase mixes ML crop recommendation, weather/market APIs, and a direct LLM chatbot (OpenRouter/Gemini) without retrieval. That chatbot cannot cite sources and may invent facts about PMFBY or ICAR advisories.

## 3. Engineering Decision

Build a **modular RAG subsystem** alongside the existing FastAPI + React stack:

- **Ingestion path:** PDF → parse → clean → chunk → embed → Qdrant
- **Query path:** question → embed → retrieve → prompt → Groq LLM → cited answer
- **Preserve** existing ML advisory, weather, and market endpoints unchanged during migration
- **Incremental delivery** across 18 phased milestones with documentation and conventional commits

## 4. Alternatives Considered

| Alternative | Description |
|-------------|-------------|
| Fine-tune an LLM on agricultural PDFs | Teaches style but not updatable facts; expensive; stale on policy changes |
| Replace backend with LangChain/LlamaIndex monolith | Fast prototype but poor testability and opaque abstractions |
| Keep FAISS in-process (README legacy mention) | No metadata filtering, no horizontal scaling, no persistence story |
| Managed-only stack (Pinecone + OpenAI) | Higher cost, vendor lock-in, weaker self-hosted story for rural deployments |
| Greenfield microservice | Clean separation but duplicates auth, config, and deployment for a small team |

## 5. Why Alternative Was Not Selected

- **Fine-tuning** cannot guarantee factual grounding on 6 PDFs and fails when documents update quarterly.
- **Monolithic LangChain app** hides retrieval tuning behind chains; Staff interviewers expect you to explain each stage.
- **FAISS** lacks payload filters (e.g., `category=crop_insurance`) needed for scheme-specific questions.
- **Fully managed** stack increases per-query cost for a nonprofit-style agricultural product.
- **Separate microservice** adds operational overhead before product-market fit.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Grounded, citable answers | Higher latency (embed + retrieve + LLM) |
| Swappable embeddings/LLM/vector DB | More interfaces to maintain |
| Clear interview narrative | Slower initial delivery vs. one-shot LangChain script |
| Existing farmer UI preserved | Dual chat paths during migration |

## 7. Performance Implications

- Ingestion is **offline/batch** — does not affect query latency
- Query latency budget: embedding (~50–200 ms) + Qdrant (~10–50 ms) + LLM (~500–2000 ms)
- bge-small-en-v1.5 chosen as default for speed; bge-m3 available for multilingual content

## 8. Scaling Considerations

- Stateless FastAPI workers scale horizontally
- Qdrant scales via sharding/replication (Phase 9, 16)
- Embedding model can move to dedicated GPU service under load
- Document corpus starts at 6 PDFs (~50 MB); architecture targets 10⁶ chunks

## 9. Production Considerations

- Environment-based configuration (Groq key, Qdrant URL, embedding model)
- Structured logging with request IDs (Phase 14)
- Docker Compose for local parity (Phase 17)
- Idempotent ingestion keyed by `document_id` + content hash

## 10. Failure Cases

| Failure | Mitigation |
|---------|------------|
| Groq API down | Graceful degradation message; cached answers not in v1 |
| Qdrant unreachable | Health check fails; API returns 503 on `/ask` |
| Corrupt PDF | Validation stage rejects; logged with document_id |
| Empty retrieval | Prompt instructs model to say "I don't know" (Phase 11) |

## 11. Edge Cases

- Scanned PDFs with no text layer → OCR path (Phase 4 architecture)
- Duplicate uploads with same filename → manifest version increment (Phase 2)
- Multilingual user question vs. English PDFs → bge-m3 or query translation (future)
- Very long government reports → chunk overlap prevents context loss (Phase 6)

## 12. Security Concerns

- API keys in `.env` only; never committed
- Upload endpoint must validate PDF MIME and size (Phase 13)
- Prompt injection via malicious PDF text → sanitization + system guard prompts
- Farmer PII in chat logs → redaction policy (future)

## 13. Cost Considerations

- Groq: low-cost inference vs. GPT-4 class models
- Local embeddings: one-time GPU/CPU cost vs. OpenAI embedding API per chunk
- Qdrant self-hosted: free tier sufficient for MVP; cloud pricing at scale documented in Phase 9

## 14. Common Interview Questions

**Q: What is SasyaSampada?**  
A: An AI agricultural advisory platform for Indian farmers combining ML crop recommendation, live weather/market data, and a RAG chatbot grounded in government and university PDFs.

**Q: Why add RAG to an existing app?**  
A: The current chatbot calls an LLM directly without retrieval, so it cannot cite ICAR advisories or PMFBY rules accurately.

**Q: What documents are in the knowledge base?**  
A: Six PDFs cataloged in `data/manifests/documents.json` — crop production guide, agri welfare report, farmer handbook, ICAR kharif advisories, PMFBY guidelines, natural farming material.

## 15. Deep Interview Questions

**Q: How would you migrate users from the legacy chatbot to RAG without downtime?**  
A: Feature flag on `/api/chat` routing to `RAGService` when `RAG_ENABLED=true`; shadow-mode logging compares responses before cutover.

**Q: Why not use the ML model for text QA?**  
A: ML crop model predicts crop labels from numeric soil features; it does not consume unstructured policy PDFs.

## 16. Best Possible Answers

Emphasize **separation of concerns**: ML for structured prediction, RAG for unstructured knowledge, APIs for live data. Point to `docs/02_architecture.md` for the component diagram and phased roadmap in `docs/README.md`.

## 17. Diagrams

```
┌─────────────────────────────────────────────────────────────┐
│                    SasyaSampada Platform                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   React UI   │  FastAPI API │  ML Models   │  RAG Subsystem │
│  (farmer)    │  (routes)    │  (crop rec)  │  (new, phased) │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Knowledge Base   │
                    │  6 agri PDFs      │
                    │  data/raw/        │
                    └───────────────────┘
```

## 18. References

- Repository: `SasyaSampada`
- Document manifest: `data/manifests/documents.json`
- Existing API: `backend/app/api/routes.py`
- Legacy chatbot: `backend/app/services/chatbot.py`
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)
