#!/usr/bin/env python3

import sys
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

print("🚀 Starting Agrigrow Backend Server...")

# Import the app
try:
    from app.main import app
    print("✅ Successfully imported FastAPI app")

    from app.services.chatbot import CHATBOT_AVAILABLE
    print(f"🤖 Chatbot available: {CHATBOT_AVAILABLE}")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    raise

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
