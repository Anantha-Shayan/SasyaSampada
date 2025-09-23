#!/usr/bin/env python3
"""
Test script to verify weather functionality
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_backend_weather():
    """Test the backend weather API endpoint"""
    print("🧪 Testing Backend Weather API...")
    
    try:
        # Test the backend API
        response = requests.post(
            "http://localhost:8000/api/weather",
            json={"city": "Bangalore"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Backend API Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running. Start it with: cd backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_ml_weather():
    """Test the ML weather function directly"""
    print("\n🧪 Testing ML Weather Function...")
    
    try:
        # Add ml-model to path
        ml_model_path = os.path.join(os.path.dirname(__file__), 'ml-model')
        sys.path.append(ml_model_path)
        
        from unified_advice import get_weather
        
        # Test with a city
        weather_data = get_weather("Bangalore")
        print("✅ ML Weather Function Response:")
        print(json.dumps(weather_data, indent=2))
        return True
        
    except ImportError as e:
        print(f"❌ Could not import ML functions: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing ML weather: {e}")
        return False

def check_api_key():
    """Check if OpenWeather API key is configured"""
    print("\n🔑 Checking API Key Configuration...")
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("❌ OPENWEATHER_API_KEY not found in environment")
        return False
    elif api_key == "your_openweather_api_key_here":
        print("⚠️ OPENWEATHER_API_KEY is set to placeholder value")
        print("   Get a free API key from: https://openweathermap.org/api")
        return False
    else:
        print(f"✅ API key configured: {api_key[:8]}...")
        return True

def main():
    print("🌤️ Agrigrow Weather System Test")
    print("=" * 40)
    
    # Check API key
    api_key_ok = check_api_key()
    
    # Test ML function
    ml_ok = test_ml_weather()
    
    # Test backend API
    backend_ok = test_backend_weather()
    
    print("\n📊 Test Results:")
    print(f"API Key: {'✅' if api_key_ok else '❌'}")
    print(f"ML Function: {'✅' if ml_ok else '❌'}")
    print(f"Backend API: {'✅' if backend_ok else '❌'}")
    
    if api_key_ok and ml_ok and backend_ok:
        print("\n🎉 All tests passed! Weather system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
        
        if not api_key_ok:
            print("\n💡 To fix API key issue:")
            print("1. Get a free API key from: https://openweathermap.org/api")
            print("2. Update the OPENWEATHER_API_KEY in your .env file")
        
        if not backend_ok:
            print("\n💡 To fix backend issue:")
            print("1. Start the backend server: cd backend && python main.py")
            print("2. Make sure it's running on http://localhost:8000")

if __name__ == "__main__":
    main()
