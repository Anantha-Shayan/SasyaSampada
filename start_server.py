#!/usr/bin/env python3

import os
import sys
import uvicorn

# Add backend to path
sys.path.append('backend')

print("🚀 Starting Agrigrow Backend Server...")
print("📁 Current directory:", os.getcwd())

# Import the app
try:
    from main_ml import app
    print("✅ Successfully imported FastAPI app")
    
    # Check if chatbot is available
    from main_ml import CHATBOT_AVAILABLE
    print(f"🤖 Chatbot available: {CHATBOT_AVAILABLE}")
    
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    sys.exit(1)

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
