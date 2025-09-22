#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

print("🔍 Testing Backend Environment Loading...")

# Test the exact same logic as in main-ml.py
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # Parent directory
    os.path.join(os.path.dirname(__file__), '..', '.env'),  # Relative parent
    '.env',  # Current directory
    '../.env'  # Relative parent
]

print("Checking paths:")
for i, env_path in enumerate(env_paths):
    abs_path = os.path.abspath(env_path)
    exists = os.path.exists(env_path)
    print(f"  {i+1}. {env_path} -> {abs_path} (exists: {exists})")

env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("⚠️ No .env file found in expected locations")

# Test API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"API Key loaded: {bool(OPENROUTER_API_KEY)}")

if OPENROUTER_API_KEY:
    print(f"Key starts with: {OPENROUTER_API_KEY[:20]}...")
    
    # Test OpenAI import and client creation
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        print("✅ Chatbot client would be available")
    except Exception as e:
        print(f"❌ Chatbot client creation failed: {e}")
else:
    print("❌ No API key found - Chatbot would be disabled")

print("\n🎯 Current working directory:", os.getcwd())
print("🎯 Script location:", __file__)
print("🎯 Script directory:", os.path.dirname(__file__))
