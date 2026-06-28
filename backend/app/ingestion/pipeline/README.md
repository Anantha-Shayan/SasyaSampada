# `app/ingestion/pipeline`

| Module | Role |
|--------|------|
| `context.py` | `IngestionContext`, `IngestionResult`, manifest updates |
| `runner.py` | `IngestionPipeline` orchestrator |

## CLI

```bash
cd backend
python -m app.ingestion.cli ingest --document-id tnau_crop_production_guide_2020
python -m app.ingestion.cli ingest --all
```

## Programmatic

```python
from app.ingestion.factory import build_default_pipeline

pipeline = build_default_pipeline()
result = pipeline.run("tnau_crop_production_guide_2020")
```
