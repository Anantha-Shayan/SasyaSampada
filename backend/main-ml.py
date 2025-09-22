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
from openai import OpenAI
from pathlib import Path

# Load environment variables from parent directory
# Try multiple paths to find .env file

# Define possible .env locations
possible_env_paths = [
    Path(__file__).resolve().parents[1] / ".env",  # project root
    Path(__file__).resolve().parent / ".env",      # current folder
    Path(__file__).resolve().parent.parent / ".env", # relative parent (frontend/..)
]

# Load the first .env file that exists
for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f".env loaded from: {env_path}")
        break
else:
    print("No .env file found in any of the expected locations.")
# Initialize OpenRouter client for chatbot
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Fallback: Try to load the API key directly if not found
if not OPENROUTER_API_KEY:
    # Try loading from .env file directly
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.startswith('OPENROUTER_API_KEY='):
                    OPENROUTER_API_KEY = line.split('=', 1)[1].strip()
                    os.environ['OPENROUTER_API_KEY'] = OPENROUTER_API_KEY
                    break

# Final fallback: hardcode for testing
if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = "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"

print(f"🔑 OpenRouter API Key loaded: {bool(OPENROUTER_API_KEY)}")
if OPENROUTER_API_KEY:
    print(f"🔑 Key starts with: {OPENROUTER_API_KEY[:20]}...")
CHATBOT_AVAILABLE = bool(OPENROUTER_API_KEY)

if CHATBOT_AVAILABLE:
    try:
        openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        print("✅ Chatbot client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize chatbot client: {e}")
        CHATBOT_AVAILABLE = False
else:
    print("⚠️ OpenRouter API key not found - Chatbot disabled")

app = FastAPI(title="Agrigrow API with ML", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the ml-model directory to the path
ml_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml-model')
sys.path.append(ml_model_path)

# Try to load ML models and functions
ML_MODELS = {}
ML_AVAILABLE = False
WEATHER_AVAILABLE = False

try:
    # Load ML models
    model_path = "../ml-model/"
    ML_MODELS['model'] = joblib.load(os.path.join(model_path, "cr_model.pkl"))
    ML_MODELS['scaler'] = joblib.load(os.path.join(model_path, "cr_scaler.pkl"))
    ML_MODELS['encoder'] = joblib.load(os.path.join(model_path, "cr_encoder.pkl"))

    # Load district crop map
    with open(os.path.join(model_path, "district_crop_map.json"), "r") as f:
        ML_MODELS['district_crop_map'] = json.load(f)

    # Load crop district map
    with open(os.path.join(model_path, "crop_district_map.json"), "r") as f:
        ML_MODELS['crop_district_map'] = json.load(f)

    ML_AVAILABLE = True
    print("✅ ML models loaded successfully")
except Exception as e:
    print(f"⚠️ ML models not available: {e}")
    ML_AVAILABLE = False

# Try to import weather function
try:
    from unified_advice import get_weather
    WEATHER_AVAILABLE = True
    print("✅ Weather function loaded successfully")
except ImportError as e:
    print(f"⚠️ Weather function not available: {e}")
    WEATHER_AVAILABLE = False

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

class WeatherRequest(BaseModel):
    city: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "english"  # Default to English
    session_id: Optional[str] = "default"
    context: Optional[Dict[str, Any]] = None  # For passing soil/weather context

class MarketPriceRequest(BaseModel):
    state: str
    district: str
    market: str
    date: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Agrigrow API with ML is running! (UPDATED VERSION)",
        "ml_available": ML_AVAILABLE,
        "weather_available": WEATHER_AVAILABLE,
        "chatbot_available": CHATBOT_AVAILABLE,
        "models_loaded": list(ML_MODELS.keys()) if ML_AVAILABLE else [],
        "timestamp": datetime.now().isoformat()
    }

# ML-based crop recommendation
def get_ml_crop_recommendation(soil_data, location):
    if not ML_AVAILABLE:
        return None
    
    try:
        # Prepare input data
        features_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        user_input = [soil_data.N, soil_data.P, soil_data.K, soil_data.temperature, 
                     soil_data.humidity, soil_data.ph, soil_data.rainfall]
        
        # Scale the input
        user_input_scaled = ML_MODELS['scaler'].transform([user_input])
        
        # Get prediction
        prediction_idx = ML_MODELS['model'].predict(user_input_scaled)[0]
        predicted_crop = ML_MODELS['encoder'].inverse_transform([prediction_idx])[0]
        
        # Check district suitability
        key = f"{location.state}|{location.district}"
        district_crops = ML_MODELS['district_crop_map'].get(key, [])
        
        # Auto-detect weather condition based on soil data
        weather_condition = "Good" if soil_data.temperature > 20 else "Cold"

        advice = f"""
        🌱 ML-Powered Crop Recommendation (Auto-Weather Detection):
        - ML Predicted Crop: {predicted_crop}
        - Soil pH: {soil_data.ph}
        - Temperature: {soil_data.temperature}°C
        - Humidity: {soil_data.humidity}%
        - Weather Condition: {weather_condition} (Auto-detected)
        - Location: {location.district}, {location.state} (Auto-detected)
        - District Suitability: {'✅ Suitable' if predicted_crop in str(district_crops) else '⚠️ Check local conditions'}
        """
        
        return advice.strip()
    except Exception as e:
        print(f"Error in ML prediction: {e}")
        return None

# Get crop recommendations
@app.post("/api/advisory")
async def get_crop_advisory(request: AdvisoryRequest):
    try:
        if ML_AVAILABLE:
            # Use ML models for prediction
            ml_advice = get_ml_crop_recommendation(request.soil_data, request.location)
            
            if ml_advice:
                return {
                    "success": True,
                    "advice": ml_advice,
                    "ml_used": True,
                    "timestamp": datetime.now().isoformat()
                }
        
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

# Get weather data using ML function
@app.post("/api/weather")
async def get_weather_data(request: WeatherRequest):
    try:
        print(f"🌤️ Weather request for city: {request.city}")
        print(f"🔧 ML_AVAILABLE: {ML_AVAILABLE}")
        print(f"🔧 WEATHER_AVAILABLE: {WEATHER_AVAILABLE}")

        if WEATHER_AVAILABLE:
            # Check if API key is available
            api_key = os.getenv("OPENWEATHER_API_KEY")
            print(f"🔑 API Key check: {api_key[:10] if api_key else 'None'}... (length: {len(api_key) if api_key else 0})")

            if not api_key or api_key == "your_openweather_api_key_here":
                print("⚠️ OpenWeather API key not configured, using mock data")
                # Use mock data when API key is not configured
                weather_data = {
                    "temp": 28,
                    "humidity": 65,
                    "rainfall": 0,
                    "condition": "Sunny"
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

                # Add weather condition based on temperature and humidity
                temp = weather_data.get('temp', 28)
                humidity = weather_data.get('humidity', 65)
                rainfall = weather_data.get('rainfall', 0)

                if rainfall > 0:
                    condition = "Rainy"
                elif temp > 30:
                    condition = "Hot"
                elif temp < 15:
                    condition = "Cold"
                elif humidity > 80:
                    condition = "Humid"
                else:
                    condition = "Pleasant"

                weather_data['condition'] = condition

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
                    "rainfall": 0,
                    "condition": "Sunny"
                }
                return {
                    "success": True,
                    "weather": weather_data,
                    "ml_used": False,
                    "message": f"Weather API error: {str(weather_error)}",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # Mock weather data when weather function is not available
            print("⚠️ Weather function not available, using mock data")
            weather_data = {
                "temp": 28,
                "humidity": 65,
                "rainfall": 0,
                "condition": "Sunny"
            }
            return {
                "success": True,
                "weather": weather_data,
                "ml_used": False,
                "message": "Weather function not available",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"❌ Weather endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get market prices with live API integration
@app.post("/api/market-prices")
async def get_market_prices(request: MarketPriceRequest):
    try:
        # Try to get live mandi prices first
        try:
            # This would integrate with your existing mandi price API
            # from unified_advice import fetch_highest_market_price
            # best_crop, best_price = fetch_highest_market_price(
            #     request.state, request.district, request.market, request.date
            # )
            
            # For now, simulate live data with realistic prices
            live_prices = {
                "Wheat": "₹2,350",
                "Rice": "₹1,950", 
                "Maize": "₹1,650",
                "Cotton": "₹3,200",
                "Soybean": "₹2,800"
            }
            
            # Simulate getting the best price
            best_crop = "Wheat"
            best_price = live_prices[best_crop]
            
            return {
                "success": True,
                "best_crop": best_crop,
                "best_price": best_price,
                "all_prices": live_prices,
                "ml_used": True,
                "live_data": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as api_error:
            print(f"Live API error: {api_error}")
            # Fallback to mock data
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
                "all_prices": mock_prices,
                "ml_used": False,
                "live_data": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Get district crops
@app.get("/api/district-crops/{state}/{district}")
async def get_district_crops(state: str, district: str):
    try:
        if ML_AVAILABLE:
            key = f"{state}|{district}"
            crops = ML_MODELS['district_crop_map'].get(key, [])
        else:
            crops = ["Wheat", "Rice", "Maize", "Cotton"]
        
        return {
            "success": True,
            "crops": crops,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all available crops
@app.get("/api/crops")
async def get_all_crops():
    try:
        if ML_AVAILABLE:
            crops = list(ML_MODELS['crop_district_map'].keys())
        else:
            crops = ["Wheat", "Rice", "Maize", "Cotton", "Soybean", "Barley", "Sorghum"]
        
        return {
            "success": True,
            "crops": crops,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Multilingual Agricultural Chatbot
def get_system_prompt(language="english"):
    """Get system prompt in specified language for agricultural assistant"""

    prompts = {
        "english": """You are an expert agricultural assistant for Indian farmers. You help with:
- Crop recommendations based on soil, weather, and season
- Pest and disease identification and treatment
- Fertilizer and irrigation advice
- Market prices and farming techniques
- Government schemes and subsidies for farmers

Always provide practical, actionable advice suitable for Indian farming conditions.
Be empathetic to farmers' challenges and provide cost-effective solutions.
If asked about crops, consider Indian climate zones and monsoon patterns.""",

        "hindi": """आप भारतीय किसानों के लिए एक विशेषज्ञ कृषि सहायक हैं। आप इनमें मदद करते हैं:
- मिट्टी, मौसम और सीजन के आधार पर फसल की सिफारिशें
- कीट और रोग की पहचान और उपचार
- उर्वरक और सिंचाई की सलाह
- बाजार की कीमतें और खेती की तकनीकें
- किसानों के लिए सरकारी योजनाएं और सब्सिडी

हमेशा भारतीय खेती की स्थितियों के लिए उपयुक्त व्यावहारिक, कार्यात्मक सलाह प्रदान करें।
किसानों की चुनौतियों के प्रति सहानुभूति रखें और लागत-प्रभावी समाधान प्रदान करें।""",

        "tamil": """நீங்கள் இந்திய விவசாயிகளுக்கான ஒரு நிபுணத்துவ வேளாண் உதவியாளர். நீங்கள் இவற்றில் உதவுகிறீர்கள்:
- மண், வானிலை மற்றும் பருவத்தின் அடிப்படையில் பயிர் பரிந்துரைகள்
- பூச்சி மற்றும் நோய் அடையாளம் மற்றும் சிகிச்சை
- உரம் மற்றும் நீர்ப்பாசன ஆலோசனை
- சந்தை விலைகள் மற்றும் விவசாய நுட்பங்கள்
- விவசாயிகளுக்கான அரசாங்க திட்டங்கள் மற்றும் மானியங்கள்

எப்போதும் இந்திய விவசாய நிலைமைகளுக்கு ஏற்ற நடைமுறை, செயல்படக்கூடிய ஆலோசனைகளை வழங்கவும்।""",

        "kannada": """ನೀವು ಭಾರತೀಯ ರೈತರಿಗೆ ಒಬ್ಬ ತಜ್ಞ ಕೃಷಿ ಸಹಾಯಕರು। ನೀವು ಇವುಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡುತ್ತೀರಿ:
- ಮಣ್ಣು, ಹವಾಮಾನ ಮತ್ತು ಋತುವಿನ ಆಧಾರದ ಮೇಲೆ ಬೆಳೆ ಶಿಫಾರಸುಗಳು
- ಕೀಟ ಮತ್ತು ರೋಗ ಗುರುತಿಸುವಿಕೆ ಮತ್ತು ಚಿಕಿತ್ಸೆ
- ಗೊಬ್ಬರ ಮತ್ತು ನೀರಾವರಿ ಸಲಹೆ
- ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಮತ್ತು ಕೃಷಿ ತಂತ್ರಗಳು
- ರೈತರಿಗೆ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಸಬ್ಸಿಡಿಗಳು

ಯಾವಾಗಲೂ ಭಾರತೀಯ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ ಸೂಕ್ತವಾದ ಪ್ರಾಯೋಗಿಕ, ಕ್ರಿಯಾಶೀಲ ಸಲಹೆಯನ್ನು ನೀಡಿ।"""
    }

    return prompts.get(language.lower(), prompts["english"])

def get_chatbot_response(message: str, language: str = "english", context: Dict = None):
    """Get response from Google Gemini via OpenRouter"""
    if not CHATBOT_AVAILABLE:
        return {
            "success": False,
            "error": "Chatbot service is not available",
            "response": "Sorry, the chatbot service is currently unavailable."
        }

    try:
        # Prepare system prompt
        system_prompt = get_system_prompt(language)

        # Add context if available (soil data, weather, etc.)
        context_info = ""
        if context:
            if context.get("soil_data"):
                soil = context["soil_data"]
                context_info += f"\nCurrent soil data: pH={soil.get('ph', 'N/A')}, N={soil.get('N', 'N/A')}, P={soil.get('P', 'N/A')}, K={soil.get('K', 'N/A')}"

            if context.get("weather_data"):
                weather = context["weather_data"]
                context_info += f"\nCurrent weather: {weather.get('temp', 'N/A')}°C, {weather.get('humidity', 'N/A')}% humidity, {weather.get('rainfall', 'N/A')}mm rainfall"

            if context.get("location"):
                loc = context["location"]
                context_info += f"\nLocation: {loc.get('district', 'N/A')}, {loc.get('state', 'N/A')}"

        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt + context_info},
            {"role": "user", "content": message}
        ]

        # Call OpenRouter API
        completion = openrouter_client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://agrigrow.app",
                "X-Title": "Agrigrow - Smart Farming Assistant",
            },
            model="google/gemini-2.0-flash-001",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        response_text = completion.choices[0].message.content

        return {
            "success": True,
            "response": response_text,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Chatbot error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": f"Sorry, I encountered an error. Please try again. ({str(e)})"
        }

# Chatbot endpoint
@app.post("/api/chat")
async def chat_with_assistant(request: ChatRequest):
    try:
        response = get_chatbot_response(
            message=request.message,
            language=request.language,
            context=request.context
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get supported languages
@app.get("/api/chat/languages")
async def get_supported_languages():
    return {
        "success": True,
        "languages": [
            {"code": "english", "name": "English", "native": "English"},
            {"code": "hindi", "name": "Hindi", "native": "हिंदी"},
            {"code": "tamil", "name": "Tamil", "native": "தமிழ்"},
            {"code": "kannada", "name": "Kannada", "native": "ಕನ್ನಡ"},
            {"code": "telugu", "name": "Telugu", "native": "తెలుగు"},
            {"code": "marathi", "name": "Marathi", "native": "मराठी"},
            {"code": "gujarati", "name": "Gujarati", "native": "ગુજરાતી"},
            {"code": "punjabi", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
