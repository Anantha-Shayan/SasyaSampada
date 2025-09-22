#!/usr/bin/env python3
"""
Test what environment variables the backend is seeing
"""
import os
import sys
from dotenv import load_dotenv

# Test different ways of loading environment
print("🔧 Testing Environment Loading")
print("=" * 40)

# Method 1: Load from current directory
print("1. Loading from current directory:")
load_dotenv()
api_key_1 = os.getenv("OPENWEATHER_API_KEY")
print(f"   API Key: {api_key_1[:10] if api_key_1 else 'None'}...")

# Method 2: Load from parent directory (like backend does)
print("2. Loading from parent directory:")
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
api_key_2 = os.getenv("OPENWEATHER_API_KEY")
print(f"   API Key: {api_key_2[:10] if api_key_2 else 'None'}...")

# Method 3: Load from explicit path
print("3. Loading from explicit path:")
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"   Env path: {env_path}")
print(f"   Env exists: {os.path.exists(env_path)}")
load_dotenv(env_path)
api_key_3 = os.getenv("OPENWEATHER_API_KEY")
print(f"   API Key: {api_key_3[:10] if api_key_3 else 'None'}...")

# Check what the backend directory sees
print("\n4. From backend directory:")
os.chdir('backend')
load_dotenv('../.env')
api_key_4 = os.getenv("OPENWEATHER_API_KEY")
print(f"   API Key: {api_key_4[:10] if api_key_4 else 'None'}...")

print(f"\n📊 Results:")
print(f"Current dir: {api_key_1 is not None}")
print(f"Parent dir: {api_key_2 is not None}")
print(f"Explicit: {api_key_3 is not None}")
print(f"Backend dir: {api_key_4 is not None}")

# Test the actual condition from backend
final_key = api_key_4 or api_key_3 or api_key_2 or api_key_1
if final_key:
    print(f"\n✅ Final API Key: {final_key[:10]}...")
    print(f"Length: {len(final_key)}")
    print(f"Is placeholder: {final_key == 'your_openweather_api_key_here'}")
    print(f"Should use ML: {final_key != 'your_openweather_api_key_here'}")
else:
    print("\n❌ No API key found")
