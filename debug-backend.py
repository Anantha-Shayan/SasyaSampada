#!/usr/bin/env python3
"""
Debug script to test backend weather functionality
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def test_environment():
    """Test environment variable loading"""
    print("🔧 Environment Test:")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    print(f"API Key: {api_key[:10]}... (length: {len(api_key) if api_key else 0})")
    return api_key

def test_ml_function():
    """Test ML weather function directly"""
    print("\n🧪 ML Function Test:")
    try:
        # Add ml-model to path
        ml_model_path = os.path.join(os.path.dirname(__file__), 'ml-model')
        sys.path.append(ml_model_path)
        
        from unified_advice import get_weather
        
        # Test with different cities
        cities = ['Mumbai', 'Delhi', 'Chennai', 'Kolkata']
        for city in cities:
            try:
                weather_data = get_weather(city)
                print(f"✅ {city}: {weather_data}")
            except Exception as e:
                print(f"❌ {city}: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import ML functions: {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    print("\n🌐 Backend API Test:")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"ML Available: {data.get('ml_available')}")
            print(f"Models: {data.get('models_loaded', [])}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test weather endpoint with different cities
    cities = ['Mumbai', 'Delhi', 'Chennai', 'Bangalore']
    for city in cities:
        try:
            response = requests.post(
                "http://localhost:8000/api/weather",
                json={"city": city},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                weather = data.get('weather', {})
                ml_used = data.get('ml_used', False)
                print(f"✅ {city}: Temp={weather.get('temp')}°C, ML={ml_used}")
            else:
                print(f"❌ {city}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {city}: {e}")
    
    return True

def main():
    print("🔍 Agrigrow Backend Debug")
    print("=" * 40)
    
    # Test environment
    api_key = test_environment()
    
    # Test ML function
    ml_ok = test_ml_function()
    
    # Test backend API
    backend_ok = test_backend_api()
    
    print("\n📊 Summary:")
    print(f"Environment: {'✅' if api_key else '❌'}")
    print(f"ML Function: {'✅' if ml_ok else '❌'}")
    print(f"Backend API: {'✅' if backend_ok else '❌'}")
    
    if api_key and ml_ok and not backend_ok:
        print("\n💡 Issue: ML function works but backend doesn't use it")
        print("Possible causes:")
        print("1. Backend not loading environment variables correctly")
        print("2. Backend code path not reaching ML function")
        print("3. Backend using cached/old code")

if __name__ == "__main__":
    main()
