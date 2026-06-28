# 08 — Text Cleaning

## 1. Purpose

Document the **text cleaning stage** that transforms noisy parser output into retrieval-ready plain text by removing layout artifacts, normalizing whitespace, and fixing encoding issues.

## 2. Problem Being Solved

PDF extraction leaves headers, footers, page numbers, hyphenation breaks, and irregular whitespace in chunk text. Embeddings trained on clean prose degrade when every chunk repeats "Page 47" or contains `agricul-\nture`. Retrieval precision drops because queries match boilerplate instead of agricultural content.

## 3. Engineering Decision

**`AgriculturalTextCleaner`** in `app/ingestion/stages/cleaner/` applies a deterministic pipeline of pure functions in `text_utils.py`:

1. Build page source from `body_text` + table markdown (Phase 4 fields)
2. Strip leaked header/footer strings
3. Unicode NFKC normalization + control char removal
4. Fix hyphenated line breaks
5. Remove page number lines and inline page refs
6. Collapse duplicate whitespace and excess blank lines
7. Join pages with `\n\n`

`PassthroughCleaner` retained for tests and regression comparison.

## 4. Alternatives Considered

| Alternative | Issue |
|-------------|-------|
| Clean during parsing | Violates single-responsibility; parser already complex |
| LLM-based cleaning | Non-deterministic; expensive; hallucination risk |
| `ftfy` library | Extra dep; NFKC + control strip sufficient for MVP |
| Regex-only monolith | Untestable; hard to tune per rule |

## 5. Why Alternative Was Not Selected

Pure functions with explicit rules are **testable**, **fast**, **offline**, and **interview-defensible**. Parser provides structure (header/footer bands); cleaner applies content rules.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Higher retrieval signal-to-noise | Aggressive page-number regex may drop valid short lines |
| Reproducible output | Heuristic rules need tuning per corpus |
| Zero API cost | Cannot fix semantic garbling (OCR errors) — needs better OCR |

## 7. Performance Implications

- Regex passes are O(n) per page — negligible vs PDF parse
- Runs once at ingest — no query-time cost
- Smaller cleaned files → faster chunking

## 8. Scaling Considerations

- Stateless — parallelize per document in worker pool
- Rule config via env (future) for regional footer patterns
- Hindi/Tamil page labels need extra patterns (future)

## 9. Production Considerations

- Output: `data/processed/{document_id}/v{version}/cleaned.txt`
- `cleaner_name` = `agricultural_text` in `CleanedDocument`
- Empty output → `NonRetryableError` (pipeline marks failed)
- Tables preserved as markdown blocks — not stripped

### Cleaning rules (`rules.py`)

| Rule | Pattern / action |
|------|------------------|
| Page lines | `Page 12`, `- 5 -`, `12/45` |
| Inline page refs | trailing `Page N`, `p. N` |
| Hyphen breaks | `word-\nword` → merged |
| Whitespace | collapse spaces; max 2 newlines |
| Encoding | NFKC; strip control chars |

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| All pages empty after clean | `NonRetryableError` |
| Table-only page | Table markdown preserved |
| OCR gibberish | Passes through — fix at OCR stage |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| List item "1." on own line | Not removed (unlike lone `12`) |
| Header in body quote | `strip_header_footer_leaks` may over-remove — rare |
| Multi-column text | Whitespace normalize helps; semantic chunking in Phase 6 |

## 12. Security Concerns

- No external calls; regex only
- Control char removal prevents log injection oddities

## 13. Cost Considerations

- Zero marginal cost — CPU microseconds per page

## 14. Common Interview Questions

**Q: Why clean before chunking?**  
A: Chunks inherit noise; embeddings conflate page numbers with content; harder to fix post-chunk.

**Q: Why not clean at query time?**  
A: Ingest-time cleaning is amortized; index stays consistent; query path stays fast.

## 15. Deep Interview Questions

**Q: How does cleaning improve retrieval?**  
A: Reduces boilerplate token overlap; tighter semantic clusters; better cosine similarity to user questions about crops not "Page 12".

**Q: How measure cleaning impact?**  
A: A/B recall@K on golden questions before/after; chunk boilerplate ratio; embedding distance variance.

## 16. Best Possible Answers

Name each artifact removed, which parser field feeds the cleaner (`body_text`, `header_text`, `footer_text`, `tables`), and why deterministic rules beat LLM cleaning for production.

## 17. Diagrams

```
ParsedPage (per page)
   │
   ▼
build_page_source_text()  ← body_text + tables
   │
   ▼
strip_header_footer_leaks()
   │
   ▼
normalize_encoding()
   │
   ▼
fix_hyphenated_line_breaks()
   │
   ▼
remove_page_numbers()
   │
   ▼
remove_duplicate_whitespace()
   │
   ▼
Join pages → cleaned.txt
```

### Why cleaning improves retrieval

```
Before:  "... PMFBY rules Page 47 Page 48 premium rates ..."
After:   "... PMFBY rules premium rates ..."
Query:   "PMFBY premium calculation"
         ↑ stronger match on content tokens
```

## 18. References

- `backend/app/ingestion/stages/cleaner/text_utils.py`
- `backend/app/ingestion/stages/cleaner/agricultural_cleaner.py`
- `docs/07_pdf_parsing.md`
- `docs/09_chunking.md` (planned Phase 6)
