# 05 — RAG Pipeline (Architecture)

## 1. Purpose

Define the **query-time** Retrieval Augmented Generation pipeline before implementation (Phase 12). This document is the blueprint for `app/rag/`.

## 2. Problem Being Solved

Sending farmer questions directly to an LLM produces confident but ungrounded answers about PMFBY eligibility, ICAR schedules, and regional crop practices. RAG injects verified excerpts from ingested PDFs into the prompt.

## 3. Engineering Decision

**Linear staged pipeline** with optional enhancement hooks:

```
Question → Embed → Retrieve → Rank → Build Context → Prompt → LLM → Citations → Log
```

Start with **similarity top-K** (Phase 10 baseline); progressively enable MMR, hybrid search, reranking, and context compression via configuration flags — not code forks.

## 4. Alternatives Considered

| Alternative | Notes |
|-------------|-------|
| Agentic RAG (ReAct loop) | Higher latency/cost; overkill for MVP |
| GraphRAG | Requires entity graph build — Phase 18 |
| Long-context LLM only (no RAG) | Cannot fit 6 full PDFs; expensive; hallucinates |
| Single LangChain `RetrievalQA` chain | Opaque; hard to benchmark per stage |

## 5. Why Alternative Was Not Selected

Linear pipeline is **measurable** (latency per stage), **testable** (mock retriever), and **interview-defensible**. Enhancements plug in at the retrieval/ranking stage without rewriting generation.

## 6. Tradeoffs

| Pro | Con |
|-----|-----|
| Clear bottleneck identification | May retrieve irrelevant chunks without reranker |
| Citations traceable to chunk metadata | Prompt length limits truncate context |
| Groq speed keeps UX acceptable | Two model calls worth of failure modes (embed + LLM) |

## 7. Performance Implications

| Stage | Typical latency |
|-------|-----------------|
| Query embed | 20–150 ms |
| Qdrant top-10 | 5–30 ms |
| MMR / rerank | +50–300 ms (optional) |
| Groq LLM | 300–1500 ms |
| **Total** | ~0.5–2 s target |

## 8. Scaling Considerations

- Cache frequent query embeddings (Redis, Phase 18)
- Reduce K or enable context compression under load
- Separate read replicas for Qdrant

## 9. Production Considerations

- Token budget for context: `MAX_CONTEXT_TOKENS` env (Phase 15)
- Fallback message when `retrieved_chunks == 0`
- Log retrieval scores for offline eval (Phase 18)

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| No chunks above score threshold | Return "I don't have information on that in my knowledge base" |
| LLM timeout | 504; partial retrieval logged |
| Malformed citation | Post-process validator strips bad refs |

## 11. Edge Cases

- Multi-hop questions ("Compare PMFBY and natural farming subsidies") → multi-query retrieval (Phase 10)
- User writes in Hindi, docs in English → bge-m3 or translate-then-retrieve
- Question about live mandi prices → route to market API, not RAG (intent classifier, future)

## 12. Security Concerns

- Retrieved chunks injected into prompt — sanitize control characters
- System prompt resists "ignore previous instructions" in user text

## 13. Cost Considerations

- Each `/ask` = 1 embed + 1 LLM call minimum
- `/search` skips LLM for cheaper exploration
- Smaller K and smaller context reduce Groq tokens

## 14. Common Interview Questions

**Q: What is RAG?**  
A: Retrieve relevant documents, augment the LLM prompt with them, then generate an answer grounded in those sources.

**Q: Why RAG over fine-tuning?**  
A: Updatable knowledge, citations, lower training cost, no catastrophic forgetting when policies change.

## 15. Deep Interview Questions

**Q: How do you reduce hallucinations?**  
A: Low temperature, citation-required prompt, score threshold, "answer only from context" instruction, and returning insufficient-context message when retrieval is weak.

**Q: How would you evaluate this RAG system?**  
A: Golden Q&A set from PDFs, metrics: recall@K, faithfulness, citation accuracy, latency p95.

## 16. Best Possible Answers

Walk stage-by-stage with **what each stage consumes and produces**. Mention progressive enhancements as config toggles, not rewrites.

## 17. Diagrams

```
┌─────────────┐
│ User        │
│ Question    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│  Embedding  │────▶│ query_vector     │
│  Provider   │     └────────┬─────────┘
└─────────────┘              │
                             ▼
                    ┌─────────────────┐
                    │   Retriever     │
                    │  (top-K, MMR,   │
                    │   hybrid…)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Context Builder │
                    │ (token budget)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Prompt Template │
                    │ system+context  │
                    │ +user+guards    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  LLM (Groq)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Citations +     │
                    │ Response DTO    │
                    └─────────────────┘
```

### Progressive retrieval improvements (Phase 10)

| Level | Technique | Quality | Latency |
|-------|-----------|---------|---------|
| 1 | Top-K cosine | Baseline | Lowest |
| 2 | Metadata filter | Better precision | +filter cost |
| 3 | MMR | Diversity | +O(K²) |
| 4 | Hybrid BM25+dense | Keyword + semantic | +index |
| 5 | Multi-query | Recall for paraphrases | +embed calls |
| 6 | Parent-document | Broader context | +storage |
| 7 | Context compression | Fit more in prompt | +small LLM |
| 8 | Cross-encoder rerank | Best precision | +100–300ms |

## 18. References

- Lewis et al., RAG (2020)
- `app/rag/README.md`
- `docs/13_retrieval.md` (Phase 10)
- `docs/14_prompt_engineering.md` (planned Phase 11)
