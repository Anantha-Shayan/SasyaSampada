#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

print("🔍 Testing Chatbot Setup...")

# Test 1: Check environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"✅ API Key loaded: {bool(OPENROUTER_API_KEY)}")
if OPENROUTER_API_KEY:
    print(f"   Key starts with: {OPENROUTER_API_KEY[:20]}...")

# Test 2: Test OpenAI import
try:
    from openai import OpenAI
    print("✅ OpenAI import successful")
except Exception as e:
    print(f"❌ OpenAI import failed: {e}")
    sys.exit(1)

# Test 3: Test client creation
try:
    if OPENROUTER_API_KEY:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        print("✅ OpenRouter client created successfully")
    else:
        print("❌ No API key available")
        sys.exit(1)
except Exception as e:
    print(f"❌ Client creation failed: {e}")
    sys.exit(1)

# Test 4: Test chat completion
try:
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://agrigrow.app",
            "X-Title": "Agrigrow - Smart Farming Assistant",
        },
        model="google/gemini-2.0-flash-001",
        messages=[
            {"role": "system", "content": "You are an agricultural expert for Indian farmers."},
            {"role": "user", "content": "Hello, can you help me with farming?"}
        ],
        max_tokens=100,
        temperature=0.7
    )
    
    response_text = completion.choices[0].message.content
    print("✅ Chat completion successful!")
    print(f"   Response: {response_text[:100]}...")
    
except Exception as e:
    print(f"❌ Chat completion failed: {e}")
    sys.exit(1)

print("\n🎉 All tests passed! Chatbot is working correctly.")
print("\nNow you can start the backend with:")
print(".venv\\Scripts\\python.exe backend/main-ml.py")
