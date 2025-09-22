#!/usr/bin/env python3
"""
Test script to verify ML model integration
"""
import requests
import json

def test_ml_integration():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing ML Model Integration...")
    
    # Test 1: Check if ML models are loaded
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health Check: {data['message']}")
            print(f"🤖 ML Models Available: {data['ml_available']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Test crop advisory with ML models
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
            result = response.json()
            print("✅ Crop Advisory API Working")
            print(f"   ML Used: {result.get('ml_used', False)}")
            print(f"   Recommendation: {result['advice'][:100]}...")
        else:
            print(f"❌ Crop advisory failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Crop advisory error: {e}")
    
    # Test 3: Test weather API
    try:
        weather_data = {"city": "Bangalore"}
        response = requests.post(f"{base_url}/api/weather", json=weather_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Weather API Working")
            print(f"   ML Used: {result.get('ml_used', False)}")
            print(f"   Weather: {result['weather']}")
        else:
            print(f"❌ Weather API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Weather API error: {e}")
    
    # Test 4: Test market prices
    try:
        market_data = {
            "state": "Karnataka",
            "district": "Bangalore",
            "market": "Ramanagara"
        }
        response = requests.post(f"{base_url}/api/market-prices", json=market_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Market Prices API Working")
            print(f"   ML Used: {result.get('ml_used', False)}")
            print(f"   Best crop: {result['best_crop']} at {result['best_price']}")
        else:
            print(f"❌ Market prices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market prices error: {e}")
    
    # Test 5: Test district crops
    try:
        response = requests.get(f"{base_url}/api/district-crops/Karnataka/Bangalore")
        if response.status_code == 200:
            result = response.json()
            print("✅ District Crops API Working")
            print(f"   Available crops: {len(result['crops'])} crops")
        else:
            print(f"❌ District crops failed: {response.status_code}")
    except Exception as e:
        print(f"❌ District crops error: {e}")
    
    print("\n🎉 ML Integration Testing Complete!")
    print("📱 Your React app should now be using your ML models!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")

if __name__ == "__main__":
    test_ml_integration()
