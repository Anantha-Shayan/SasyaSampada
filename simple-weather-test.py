#!/usr/bin/env python3
"""
Simple test to verify weather functionality works end-to-end
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_direct_ml():
    """Test ML function directly"""
    print("🧪 Testing ML Function Directly:")
    try:
        # Add ml-model to path
        ml_model_path = os.path.join(os.path.dirname(__file__), 'ml-model')
        sys.path.append(ml_model_path)
        
        from unified_advice import get_weather
        
        cities = ['Mumbai', 'Delhi', 'Chennai']
        for city in cities:
            weather_data = get_weather(city)
            print(f"✅ {city}: {weather_data}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_direct():
    """Test backend by calling it directly"""
    print("\n🌐 Testing Backend Directly:")
    
    # Import backend modules
    sys.path.append('backend')
    
    try:
        from main import get_weather_data
        from main import WeatherRequest
        
        # Create a request
        request = WeatherRequest(city="Mumbai")
        
        # Call the function directly
        import asyncio
        result = asyncio.run(get_weather_data(request))
        print(f"✅ Direct backend call: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoint():
    """Test API endpoint"""
    print("\n🔗 Testing API Endpoint:")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/weather",
            json={"city": "Mumbai"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {data}")
            return data.get('ml_used', False)
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔍 Simple Weather Test")
    print("=" * 40)
    
    # Test ML function
    ml_works = test_direct_ml()
    
    # Test backend function
    backend_works = test_backend_direct()
    
    # Test API endpoint
    api_works = test_api_endpoint()
    
    print(f"\n📊 Results:")
    print(f"ML Function: {'✅' if ml_works else '❌'}")
    print(f"Backend Direct: {'✅' if backend_works else '❌'}")
    print(f"API Endpoint: {'✅' if api_works else '❌'}")
    
    if ml_works and not api_works:
        print("\n💡 ML works but API doesn't - backend integration issue")

if __name__ == "__main__":
    main()
