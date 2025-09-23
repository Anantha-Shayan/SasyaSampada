#!/usr/bin/env python3
"""
Simple test script to verify the Agrigrow API is working
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Agrigrow API...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Crop advisory
    try:
        advisory_data = {
            "soil_data": {
                "N": 90,
                "P": 42,
                "K": 43,
                "temperature": 25,
                "humidity": 80,
                "ph": 6.5,
                "rainfall": 120
            },
            "location": {
                "state": "Karnataka",
                "district": "Bangalore",
                "market": "Ramanagara"
            }
        }
        
        response = requests.post(f"{base_url}/api/advisory", json=advisory_data)
        if response.status_code == 200:
            print("✅ Crop advisory API working")
            result = response.json()
            print(f"   Recommendation: {result['advice'][:100]}...")
        else:
            print(f"❌ Crop advisory failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Crop advisory error: {e}")
    
    # Test 3: Weather API
    try:
        weather_data = {"city": "Bangalore"}
        response = requests.post(f"{base_url}/api/weather", json=weather_data)
        if response.status_code == 200:
            print("✅ Weather API working")
            result = response.json()
            print(f"   Weather: {result['weather']}")
        else:
            print(f"❌ Weather API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Weather API error: {e}")
    
    # Test 4: Market prices
    try:
        market_data = {
            "state": "Karnataka",
            "district": "Bangalore",
            "market": "Ramanagara"
        }
        response = requests.post(f"{base_url}/api/market-prices", json=market_data)
        if response.status_code == 200:
            print("✅ Market prices API working")
            result = response.json()
            print(f"   Best crop: {result['best_crop']} at {result['best_price']}")
        else:
            print(f"❌ Market prices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market prices error: {e}")
    
    # Test 5: Chat API
    try:
        chat_data = {"question": "What is the best soil for growing rice?"}
        response = requests.post(f"{base_url}/api/chat", json=chat_data)
        if response.status_code == 200:
            print("✅ Chat API working")
            result = response.json()
            print(f"   Response: {result['response'][:100]}...")
        else:
            print(f"❌ Chat API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat API error: {e}")
    
    print("\n🎉 API testing complete!")
    print("📱 Frontend should be available at: http://localhost:3000")
    print("🔧 Backend API available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()
