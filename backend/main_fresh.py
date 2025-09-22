#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from typing import Dict, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Set API key directly for testing
OPENROUTER_API_KEY = "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"

print(f"🔑 OpenRouter API Key: {bool(OPENROUTER_API_KEY)}")

# Initialize OpenAI client
try:
    from openai import OpenAI
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    CHATBOT_AVAILABLE = True
    print("✅ Chatbot client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize chatbot client: {e}")
    CHATBOT_AVAILABLE = False

# FastAPI app
app = FastAPI(title="Agrigrow Fresh API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str
    language: str = "english"
    context: Optional[Dict] = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Agrigrow Fresh API is running!",
        "chatbot_available": CHATBOT_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# Languages endpoint
@app.get("/api/chat/languages")
async def get_supported_languages():
    languages = [
        {"code": "english", "name": "English", "native": "English"},
        {"code": "hindi", "name": "Hindi", "native": "हिंदी"},
        {"code": "tamil", "name": "Tamil", "native": "தமிழ்"},
        {"code": "kannada", "name": "Kannada", "native": "ಕನ್ನಡ"},
        {"code": "telugu", "name": "Telugu", "native": "తెలుగు"},
        {"code": "marathi", "name": "Marathi", "native": "मराठी"},
        {"code": "gujarati", "name": "Gujarati", "native": "ગુજરાતી"},
        {"code": "punjabi", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"}
    ]
    return {"success": True, "languages": languages}

def get_system_prompt(language: str = "english"):
    """Get system prompt for the specified language"""
    prompts = {
        "english": """You are an expert agricultural advisor for Indian farmers. You have deep knowledge of:
- Indian crops, seasons, and farming practices
- Soil management and fertilizers
- Pest and disease control
- Weather patterns and irrigation
- Government schemes and subsidies
- Market prices and crop economics

Always provide practical, actionable advice suitable for Indian agricultural conditions. Be helpful, encouraging, and culturally sensitive.""",

        "hindi": """आप भारतीय किसानों के लिए एक विशेषज्ञ कृषि सलाहकार हैं। आपको गहरी जानकारी है:
- भारतीय फसलों, मौसम और खेती की प्रथाओं की
- मिट्टी प्रबंधन और उर्वरकों की
- कीट और रोग नियंत्रण की
- मौसम पैटर्न और सिंचाई की
- सरकारी योजनाओं और सब्सिडी की
- बाजार की कीमतों और फसल अर्थशास्त्र की

हमेशा भारतीय कृषि परिस्थितियों के लिए उपयुक्त व्यावहारिक, कार्यशील सलाह दें।""",

        "tamil": """நீங்கள் இந்திய விவசாயிகளுக்கான ஒரு நிபுணர் வேளாண் ஆலோசகர். உங்களுக்கு ஆழமான அறிவு உள்ளது:
- இந்திய பயிர்கள், பருவங்கள் மற்றும் விவசாய நடைமுறைகள்
- மண் மேலாண்மை மற்றும் உரங்கள்
- பூச்சி மற்றும் நோய் கட்டுப்பாடு
- வானிலை முறைகள் மற்றும் நீர்ப்பாசனம்
- அரசாங்க திட்டங்கள் மற்றும் மானியங்கள்
- சந்தை விலைகள் மற்றும் பயிர் பொருளாதாரம்

எப்போதும் இந்திய வேளாண் நிலைமைகளுக்கு ஏற்ற நடைமுறை, செயல்படக்கூடிய ஆலோசனை வழங்கவும்।""",

        "kannada": """ನೀವು ಭಾರತೀಯ ರೈತರಿಗೆ ಒಬ್ಬ ತಜ್ಞ ಕೃಷಿ ಸಲಹೆಗಾರರು. ನಿಮಗೆ ಆಳವಾದ ಜ್ಞಾನವಿದೆ:
- ಭಾರತೀಯ ಬೆಳೆಗಳು, ಋತುಗಳು ಮತ್ತು ಕೃಷಿ ಪದ್ಧತಿಗಳು
- ಮಣ್ಣಿನ ನಿರ್ವಹಣೆ ಮತ್ತು ಗೊಬ್ಬರಗಳು
- ಕೀಟ ಮತ್ತು ರೋಗ ನಿಯಂತ್ರಣ
- ಹವಾಮಾನ ಮಾದರಿಗಳು ಮತ್ತು ನೀರಾವರಿ
- ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಸಬ್ಸಿಡಿಗಳು
- ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಮತ್ತು ಬೆಳೆ ಅರ್ಥಶಾಸ್ತ್ರ

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

        # Add context if available
        context_info = ""
        if context:
            if context.get("soil_data"):
                soil = context["soil_data"]
                context_info += f"\nCurrent soil data: pH={soil.get('ph', 'N/A')}, N={soil.get('N', 'N/A')}, P={soil.get('P', 'N/A')}, K={soil.get('K', 'N/A')}"

            if context.get("weather_data"):
                weather = context["weather_data"]
                context_info += f"\nCurrent weather: {weather.get('temp', 'N/A')}°C, {weather.get('humidity', 'N/A')}% humidity"

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

if __name__ == "__main__":
    print("🚀 Starting Agrigrow Fresh Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
