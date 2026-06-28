# `app/ingestion/stages/metadata/`

| Module | Role |
|--------|------|
| `generator.py` | `RichMetadataGenerator` — builds `ChunkRecord` JSONL |
| `section_detector.py` | Infer `section_title` from chunk headings |
| `page_mapper.py` | Map chunks → page numbers via parsed artifact overlap |

`DefaultMetadataGenerator` is an alias for `RichMetadataGenerator`.
