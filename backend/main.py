from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import joblib
import numpy as np
import pandas as pd
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATHS = [
    os.path.join(PROJECT_ROOT, '.env'),
    os.path.join(os.path.dirname(__file__), '..', '.env'),
    '.env',
    '../.env',
]

for env_path in ENV_PATHS:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Add the ml-model directory to the path
ml_model_path = os.path.join(PROJECT_ROOT, 'ml-model')
if ml_model_path not in sys.path:
    sys.path.append(ml_model_path)

# Import your existing ML functions
try:
    from unified_advice import (
        give_advice,
        get_weather,
        fetch_highest_market_price,
        ML_AVAILABLE as UNIFIED_ML_AVAILABLE,
    )
    ML_AVAILABLE = UNIFIED_ML_AVAILABLE
    print("✅ ML helpers loaded successfully")
    print(f"📁 ML model path: {ml_model_path}")
except ImportError as e:
    print(f"⚠️ ML helpers not available: {e}")
    print(f"📁 Attempted ML model path: {ml_model_path}")
    ML_AVAILABLE = False

app = FastAPI(title="Agrigrow API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SoilData(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class LocationData(BaseModel):
    state: str
    district: str
    market: str

class AdvisoryRequest(BaseModel):
    soil_data: SoilData
    location: LocationData

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"

class WeatherRequest(BaseModel):
    city: str

class MarketPriceRequest(BaseModel):
    state: str
    district: str
    market: str
    date: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Agrigrow API is running!",
        "ml_available": ML_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# Get crop recommendations using your ML models
@app.post("/api/advisory")
async def get_crop_advisory(request: AdvisoryRequest):
    try:
        if ML_AVAILABLE:
            # Use your existing ML models
            user_input = {
                "N": request.soil_data.N,
                "P": request.soil_data.P,
                "K": request.soil_data.K,
                "temperature": request.soil_data.temperature,
                "humidity": request.soil_data.humidity,
                "ph": request.soil_data.ph,
                "rainfall": request.soil_data.rainfall
            }
            
            # Get advisory using your unified advice system
            advice = give_advice(
                user_input,
                request.location.state,
                request.location.district,
                request.location.market
            )
            
            return {
                "success": True,
                "advice": advice,
                "ml_used": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Fallback to simple logic
            soil_data = request.soil_data
            if soil_data.ph < 6.0:
                recommended_crop = "Rice"
            elif soil_data.ph > 7.5:
                recommended_crop = "Wheat"
            else:
                recommended_crop = "Maize"
            
            advice = f"""
            🌱 Crop Recommendation (Simple Mode):
            - Recommended Crop: {recommended_crop}
            - Soil pH: {soil_data.ph}
            - Temperature: {soil_data.temperature}°C
            - Location: {request.location.district}, {request.location.state}
            """
            
            return {
                "success": True,
                "advice": advice.strip(),
                "ml_used": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get weather data using your weather function
@app.post("/api/weather")
async def get_weather_data(request: WeatherRequest):
    try:
        print(f"🌤️ Weather request for city: {request.city}")
        print(f"🔧 ML_AVAILABLE: {ML_AVAILABLE}")
        if ML_AVAILABLE:
            # Check if API key is available
            api_key = os.getenv("OPENWEATHER_API_KEY")
            print(f"🔑 API Key check: {api_key[:10] if api_key else 'None'}... (length: {len(api_key) if api_key else 0})")
            print(f"🔑 Is placeholder: {api_key == 'your_openweather_api_key_here'}")
            print(f"🔑 Should use ML: {api_key and api_key != 'your_openweather_api_key_here'}")

            if not api_key or api_key == "your_openweather_api_key_here":
                print("⚠️ OpenWeather API key not configured, using mock data")
                # Use mock data when API key is not configured
                weather_data = {
                    "temp": 28,
                    "humidity": 65,
                    "rainfall": 0
                }
                return {
                    "success": True,
                    "weather": weather_data,
                    "ml_used": False,
                    "message": "Using mock data - API key not configured",
                    "timestamp": datetime.now().isoformat()
                }

            try:
                print(f"🌤️ Fetching weather for {request.city} using ML function...")
                weather_data = get_weather(request.city)
                print(f"✅ Weather data fetched for {request.city}: {weather_data}")
                return {
                    "success": True,
                    "weather": weather_data,
                    "ml_used": True,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as weather_error:
                print(f"❌ Weather API error: {weather_error}")
                # Fallback to mock data if weather API fails
                weather_data = {
                    "temp": 28,
                    "humidity": 65,
                    "rainfall": 0
                }
                return {
                    "success": True,
                    "weather": weather_data,
                    "ml_used": False,
                    "message": f"Weather API error: {str(weather_error)}",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # Mock weather data when ML is not available
            weather_data = {
                "temp": 28,
                "humidity": 65,
                "rainfall": 0
            }
            return {
                "success": True,
                "weather": weather_data,
                "ml_used": False,
                "message": "ML models not available",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"❌ Unexpected error in weather endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get market prices using your market function
@app.post("/api/market-prices")
async def get_market_prices(request: MarketPriceRequest):
    try:
        if ML_AVAILABLE:
            best_crop, best_price = fetch_highest_market_price(
                request.state,
                request.district,
                request.market,
                request.date
            )
            
            return {
                "success": True,
                "best_crop": best_crop,
                "best_price": best_price,
                "ml_used": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Mock market data
            mock_prices = {
                "Wheat": "₹2,200",
                "Rice": "₹1,800",
                "Maize": "₹1,500",
                "Cotton": "₹3,000"
            }
            best_crop = "Wheat"
            best_price = mock_prices[best_crop]
            
            return {
                "success": True,
                "best_crop": best_crop,
                "best_price": best_price,
                "ml_used": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat with AI assistant
@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Simple response based on keywords
        question = request.question.lower()
        
        if "soil" in question:
            response = "For healthy soil, test pH levels regularly and maintain organic matter content. Most crops prefer pH between 6.0-7.5."
        elif "pest" in question:
            response = "Use Integrated Pest Management (IPM) approach. Start with cultural methods like crop rotation and proper spacing."
        elif "water" in question:
            response = "Water crops early in the morning to reduce evaporation. Drip irrigation is more efficient than sprinkler systems."
        elif "fertilizer" in question:
            response = "Nitrogen promotes leaf growth, phosphorus supports root development, and potassium improves plant health."
        else:
            response = "I'm here to help with your farming questions! Ask me about soil management, pest control, irrigation, or any other agricultural topic."
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get district crop mapping using your data
@app.get("/api/district-crops/{state}/{district}")
async def get_district_crops(state: str, district: str):
    try:
        if ML_AVAILABLE:
            # Load district crop map
            district_crop_map_path = os.path.join(ml_model_path, "district_crop_map.json")
            with open(district_crop_map_path, "r") as f:
                district_crop_map = json.load(f)
            
            key = f"{state}|{district}"
            crops = district_crop_map.get(key, [])
        else:
            crops = ["Wheat", "Rice", "Maize", "Cotton"]
        
        return {
            "success": True,
            "crops": crops,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get crop district mapping using your data
@app.get("/api/crop-districts/{crop}")
async def get_crop_districts(crop: str):
    try:
        if ML_AVAILABLE:
            # Load crop district map
            crop_district_map_path = os.path.join(ml_model_path, "crop_district_map.json")
            with open(crop_district_map_path, "r") as f:
                crop_district_map = json.load(f)
            
            districts = crop_district_map.get(crop, [])
        else:
            districts = [
                {"state": "Karnataka", "district": "Bangalore"},
                {"state": "Maharashtra", "district": "Mumbai"}
            ]
        
        return {
            "success": True,
            "districts": districts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all available crops
@app.get("/api/crops")
async def get_all_crops():
    try:
        if ML_AVAILABLE:
            # Load crop district map to get all available crops
            crop_district_map_path = os.path.join(ml_model_path, "crop_district_map.json")
            with open(crop_district_map_path, "r") as f:
                crop_district_map = json.load(f)
            
            crops = list(crop_district_map.keys())
        else:
            crops = ["Wheat", "Rice", "Maize", "Cotton", "Soybean", "Barley", "Sorghum"]
        
        return {
            "success": True,
            "crops": crops,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all available districts
@app.get("/api/districts")
async def get_all_districts():
    try:
        if ML_AVAILABLE:
            # Load district crop map to get all available districts
            district_crop_map_path = os.path.join(ml_model_path, "district_crop_map.json")
            with open(district_crop_map_path, "r") as f:
                district_crop_map = json.load(f)
            
            districts = []
            for key in district_crop_map.keys():
                state, district = key.split("|")
                districts.append({"state": state, "district": district})
        else:
            districts = [
                {"state": "Karnataka", "district": "Bangalore"},
                {"state": "Karnataka", "district": "Mysore"},
                {"state": "Maharashtra", "district": "Mumbai"},
                {"state": "Tamil Nadu", "district": "Chennai"}
            ]
        
        return {
            "success": True,
            "districts": districts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)