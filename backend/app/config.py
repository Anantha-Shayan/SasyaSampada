import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
MODEL_ASSETS_DIR = BACKEND_DIR / "model_assets"
DATA_DIR = PROJECT_ROOT / "data"
DATASETS_DIR = DATA_DIR / "datasets"


def load_environment() -> bool:
    env_paths = [
        PROJECT_ROOT / ".env",
        BACKEND_DIR / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            return True
    load_dotenv()
    return False


ENV_LOADED = load_environment()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MANDI_PRICE_KEY = os.getenv("MANDI_PRICE_KEY")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3001,http://127.0.0.1:3001",
    ).split(",")
    if origin.strip()
]

# PDF parsing (Phase 4)
OCR_ENABLED = os.getenv("OCR_ENABLED", "false").lower() in {"1", "true", "yes"}
PDF_MIN_TEXT_CHARS = int(os.getenv("PDF_MIN_TEXT_CHARS", "30"))
PDF_HEADER_FRACTION = float(os.getenv("PDF_HEADER_FRACTION", "0.12"))
PDF_FOOTER_FRACTION = float(os.getenv("PDF_FOOTER_FRACTION", "0.12"))

# Chunking (Phase 6)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Embeddings (Phase 8)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
EMBEDDING_NORMALIZE = os.getenv("EMBEDDING_NORMALIZE", "true").lower() in {
    "1",
    "true",
    "yes",
}

# Qdrant (Phase 9)
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "agri_knowledge")
QDRANT_UPSERT_BATCH_SIZE = int(os.getenv("QDRANT_UPSERT_BATCH_SIZE", "64"))

# Retrieval (Phase 10)
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "10"))
RETRIEVAL_SCORE_THRESHOLD = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.0"))

# Prompting / RAG (Phase 11+)
PROMPT_CONFIG_PATH = os.getenv("PROMPT_CONFIG_PATH")
RAG_CONTEXT_MAX_CHARS = int(os.getenv("RAG_CONTEXT_MAX_CHARS", "6000"))
RAG_CONTEXT_CHUNK_MAX_CHARS = int(os.getenv("RAG_CONTEXT_CHUNK_MAX_CHARS", "1200"))

# LLM (Phase 12)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "900"))
