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
    return {"message": "Agrigrow API is running!"}

# Get crop recommendations (simplified version)
@app.post("/api/advisory")
async def get_crop_advisory(request: AdvisoryRequest):
    try:
        # Simple crop recommendation logic
        soil_data = request.soil_data
        
        # Basic crop selection based on soil parameters
        if soil_data.ph < 6.0:
            recommended_crop = "Rice"
        elif soil_data.ph > 7.5:
            recommended_crop = "Wheat"
        else:
            recommended_crop = "Maize"
        
        # Weather simulation
        weather_condition = "Good" if soil_data.temperature > 20 else "Cold"
        
        advice = f"""
        🌱 Crop Recommendation:
        - Recommended Crop: {recommended_crop}
        - Soil pH: {soil_data.ph}
        - Temperature: {soil_data.temperature}°C
        - Weather Condition: {weather_condition}
        - Location: {request.location.district}, {request.location.state}
        """
        
        return {
            "success": True,
            "advice": advice.strip(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get weather data (simplified)
@app.post("/api/weather")
async def get_weather_data(request: WeatherRequest):
    try:
        # Mock weather data
        weather_data = {
            "temp": 28,
            "humidity": 65,
            "rainfall": 0,
            "condition": "Sunny"
        }
        
        return {
            "success": True,
            "weather": weather_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get market prices (simplified)
@app.post("/api/market-prices")
async def get_market_prices(request: MarketPriceRequest):
    try:
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
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat with AI assistant (simplified)
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
        else:
            response = "I'm here to help with your farming questions! Ask me about soil management, pest control, irrigation, or any other agricultural topic."
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all available crops
@app.get("/api/crops")
async def get_all_crops():
    try:
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
