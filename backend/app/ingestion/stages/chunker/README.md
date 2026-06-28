# `app/ingestion/stages/chunker/`

| Module | Role |
|--------|------|
| `recursive.py` | **Default** `RecursiveCharacterChunker` |
| `splitters.py` | Recursive split algorithm (LangChain-compatible) |
| `fixed.py` | Legacy `FixedSizeChunker` for tests |

Configure via `CHUNK_SIZE` and `CHUNK_OVERLAP` environment variables.
