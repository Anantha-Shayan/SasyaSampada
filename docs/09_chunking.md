# 09 — Chunking

## 1. Purpose

Document how cleaned agricultural text is split into retrieval-sized **chunks** using `RecursiveCharacterChunker` — the default chunking strategy for SasyaSampada.

## 2. Problem Being Solved

Embedding models and vector databases operate on finite context windows. Full PDFs (50–500 pages) cannot be embedded whole. Naive fixed-window splitting cuts mid-sentence and separates tables from their headers, degrading retrieval precision for farmer questions like "What is the PMFBY premium rate?"

## 3. Engineering Decision

**`RecursiveCharacterChunker`** (`app/ingestion/stages/chunker/`) implements the same algorithm as LangChain's `RecursiveCharacterTextSplitter`, natively in `splitters.py`:

**Separator priority:** `\n\n` → `\n` → `. ` → ` ` → character

**Defaults:** `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=200` (configurable via env)

`FixedSizeChunker` retained for regression tests and A/B comparison.

## 4. Alternatives Considered

| Strategy | Description | Verdict |
|----------|-------------|---------|
| **Fixed chunking** | Character window with step | Fast but splits mid-word/sentence |
| **Recursive chunking** | Hierarchical separators | **Selected** — best cost/quality for prose |
| **Semantic chunking** | Embed sentences; cluster by similarity | High quality; 10× embed cost at ingest |
| **Sliding windows** | Fixed window + overlap only | Same as fixed; no boundary respect |
| **Parent-child** | Small chunks retrieve; large parent for LLM | Excellent; 2× storage; Phase 18 |
| **Agentic chunking** | LLM decides split points | Non-deterministic; expensive |

## 5. Why Alternative Was Not Selected

- **Semantic/agentic** — overkill for 6 English agri PDFs; adds ingest latency and cost
- **Fixed-only** — Phase 3 MVP; poor sentence integrity hurts embedding quality
- **Parent-child** — planned upgrade (Phase 18) once baseline retrieval metrics exist

Recursive chunking is the **industry default** for prose-heavy government PDFs: respects paragraphs, predictable, offline, tunable.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Sentence/paragraph aware splits | Not semantically optimal |
| Overlap preserves cross-boundary context | ~20% more chunks vs zero overlap |
| Zero extra API calls | Table blocks may span chunks |
| Native impl — no LangChain coupling | Must maintain splitter ourselves |

## 7. Performance Implications

| Parameter | Effect |
|-----------|--------|
| `chunk_size` ↑ | Fewer chunks; less ingest cost; risk missing fine-grained matches |
| `chunk_size` ↓ | More chunks; better precision; higher embed cost |
| `chunk_overlap` ↑ | Better context continuity; redundant storage |
| `chunk_overlap` ↓ | Less redundancy; boundary facts may be lost |

**This project:** 1000/200 balances English agri prose (~750 tokens/chunk) with overlap for policy sentences spanning paragraph breaks.

## 8. Scaling Considerations

- Chunking is O(n) in document length — negligible vs PDF parse
- 1000-char chunks × 6 PDFs ≈ 10³–10⁴ vectors — well within Qdrant MVP
- At 10⁶ chunks: tune size upward; add parent-child; shard collection

## 9. Production Considerations

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CHUNK_SIZE` | `1000` | Max characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between consecutive chunks |

### Output

`ChunkedDocument` with `chunker_name=recursive_character`, passed to metadata generator.

### Tuning guide

| Corpus signal | Action |
|---------------|--------|
| Short Q&A style docs | Reduce to 512 |
| Long policy chapters | Increase to 1500 |
| Missed cross-paragraph answers | Increase overlap to 300 |
| High embed cost | Increase chunk_size |

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| Empty cleaned text | `NonRetryableError` (cleaner should catch first) |
| `chunk_overlap >= chunk_size` | `ValueError` at init |
| Single giant paragraph > chunk_size | Falls back to char-level split |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| Markdown tables `[TABLE n]` | Kept intact until separator forces char split |
| Hindi/Tamil text (future) | Add separators for `।` and language-specific rules |
| Very short doc (< chunk_size) | Single chunk |

## 12. Security Concerns

- Pure string processing — no code execution
- Chunk text flows to embedder — already trusted from own PDFs

## 13. Cost Considerations

- Chunk count ≈ `doc_length / (chunk_size - overlap)` — drives embed API cost
- 1000/200 → ~1.25× raw length in total chunk characters
- Semantic chunking would add one embed per sentence at ingest — rejected for MVP

## 14. Common Interview Questions

**Q: Why chunk overlap?**  
A: Facts spanning chunk boundaries appear in both adjacent chunks; improves recall when the matching sentence straddles a split.

**Q: Why 1000 characters?**  
A: ~200–250 tokens — fits embedding model sweet spot; small enough for precise retrieval; large enough for policy context.

**Q: Recursive vs fixed chunking?**  
A: Recursive tries paragraph/line/sentence boundaries first; fixed blindly cuts at N characters.

## 15. Deep Interview Questions

**Q: When would you switch to semantic chunking?**  
A: When recall@K plateaus and documents mix unrelated topics in long chapters; worth the ingest cost at scale.

**Q: How implement parent-child?**  
A: Index small child chunks; store `parent_id` pointing to full section text; retrieve children, pass parent to LLM.

**Q: How measure chunk quality?**  
A: Golden questions with known answer spans; check if gold span is fully contained in at least one retrieved chunk.

## 16. Best Possible Answers

Explain separator hierarchy, overlap math, and why recursive is the right **baseline** for this corpus before adding semantic/parent-child complexity.

## 17. Diagrams

### Recursive split flow

```
Full cleaned text
      │
      ▼
Split on "\n\n" (paragraphs)
      │
      ├── chunk ≤ 1000 chars ──► emit
      │
      └── chunk > 1000 chars
              │
              ▼
          Split on "\n" (lines)
              │
              └── still too big ──► ". " ──► " " ──► chars
      │
      ▼
Merge with 200-char overlap
      │
      ▼
TextChunk[0..N]
```

### Strategy comparison (this project)

```
                Quality ──────────────────────►
Fixed          ██░░░░░░░░  fast, naive
Recursive      ██████░░░░  ← chosen baseline
Sliding window █████░░░░░  overlap only
Semantic       ████████░░  costly ingest
Parent-child   █████████░  storage + complexity
Agentic        ██████████  non-deterministic
```

## 18. References

- `backend/app/ingestion/stages/chunker/splitters.py`
- LangChain `RecursiveCharacterTextSplitter` documentation
- `docs/08_cleaning.md`
- `docs/10_metadata.md` (planned Phase 7)
