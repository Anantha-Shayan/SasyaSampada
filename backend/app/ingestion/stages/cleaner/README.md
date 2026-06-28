# `app/ingestion/stages/cleaner/`

| Module | Role |
|--------|------|
| `agricultural_cleaner.py` | Default `AgriculturalTextCleaner` stage |
| `text_utils.py` | Pure cleaning functions (testable) |
| `rules.py` | Regex patterns for page numbers, whitespace |
| `passthrough.py` | Legacy no-op cleaner for tests |
