#!/usr/bin/env python3
"""
Test script to verify enhanced Agrigrow features
"""
import requests
import json

def test_enhanced_features():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enhanced Agrigrow Features...")
    print("=" * 60)
    
    # Test 1: Health check with ML status
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health Check: {data['message']}")
            print(f"🤖 ML Models Available: {data['ml_available']}")
            if data.get('models_loaded'):
                print(f"📊 Loaded Models: {', '.join(data['models_loaded'])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: Enhanced crop advisory with ML
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
            print("✅ Enhanced Crop Advisory Working")
            print(f"   ML Used: {result.get('ml_used', False)}")
            print(f"   Recommendation: {result['advice'][:100]}...")
        else:
            print(f"❌ Crop advisory failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Crop advisory error: {e}")
    
    # Test 3: Live market prices
    try:
        market_data = {
            "state": "Karnataka",
            "district": "Bangalore",
            "market": "Ramanagara"
        }
        response = requests.post(f"{base_url}/api/market-prices", json=market_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Live Market Prices Working")
            print(f"   Live Data: {result.get('live_data', False)}")
            print(f"   Best Crop: {result['best_crop']} at {result['best_price']}")
            if result.get('all_prices'):
                print(f"   All Prices: {result['all_prices']}")
        else:
            print(f"❌ Market prices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market prices error: {e}")
    
    # Test 4: Weather with location
    try:
        weather_data = {"city": "Bangalore"}
        response = requests.post(f"{base_url}/api/weather", json=weather_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Weather API Working")
            print(f"   Weather: {result['weather']}")
        else:
            print(f"❌ Weather API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Weather API error: {e}")
    
    # Test 5: District crops with ML data
    try:
        response = requests.get(f"{base_url}/api/district-crops/Karnataka/Bangalore")
        if response.status_code == 200:
            result = response.json()
            print("✅ District Crops API Working")
            print(f"   Available crops: {len(result['crops'])} crops")
            if result['crops']:
                print(f"   Sample crops: {result['crops'][:3]}")
        else:
            print(f"❌ District crops failed: {response.status_code}")
    except Exception as e:
        print(f"❌ District crops error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Features Testing Complete!")
    print("\n📱 New Features Available:")
    print("   • Soil Card Upload & OCR")
    print("   • Auto-location Detection")
    print("   • Live Mandi Price Integration")
    print("   • Organized Recommendation Results")
    print("   • Smooth Navigation Flow")
    print("\n🌐 Access Your Enhanced App:")
    print("   Frontend: http://localhost:3000")
    print("   Backend: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_enhanced_features()
