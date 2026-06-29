from datetime import datetime
from typing import Any

from openai import OpenAI

from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

CHATBOT_AVAILABLE = bool(OPENROUTER_API_KEY)
openrouter_client = None

if CHATBOT_AVAILABLE:
    try:
        openrouter_client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
    except Exception as exc:
        print(f"❌ Failed to initialize chatbot client: {exc}")
        CHATBOT_AVAILABLE = False


def get_system_prompt(language: str = "english") -> str:
    prompts = {
        "english": """You are an expert agricultural assistant for Indian farmers. You help with:
- Crop recommendations based on soil, weather, and season
- Pest and disease identification and treatment
- Fertilizer and irrigation advice
- Market prices and farming techniques
- Government schemes and subsidies for farmers

Do not use the general knowledge you were trained on. Only use the information provided in prompt that is retrieved.
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

ಯಾವಾಗಲೂ ಭಾರತೀಯ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ ಸೂಕ್ತವಾದ ಪ್ರಾಯೋಗಿಕ, ಕ್ರಿಯಾಶೀಲ ಸಲಹೆಯನ್ನು ನೀಡಿ।""",
    }
    return prompts.get(language.lower(), prompts["english"])


def get_chatbot_response(message: str | None, language: str = "english", context: dict[str, Any] | None = None):
    if not message:
        return {
            "success": False,
            "error": "Message is required",
            "response": "Please enter a message.",
        }

    if not CHATBOT_AVAILABLE or openrouter_client is None:
        return {
            "success": False,
            "error": "Chatbot service is not available",
            "response": "Sorry, the chatbot service is currently unavailable.",
        }

    try:
        system_prompt = get_system_prompt(language)
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

        completion = openrouter_client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://agrigrow.app",
                "X-Title": "Agrigrow - Smart Farming Assistant",
            },
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt + context_info},
                {"role": "user", "content": message},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        return {
            "success": True,
            "response": completion.choices[0].message.content,
            "language": language,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "response": f"Sorry, I encountered an error. Please try again. ({str(exc)})",
        }


def get_supported_language_list():
    return [
        {"code": "english", "name": "English", "native": "English"},
        {"code": "hindi", "name": "Hindi", "native": "हिंदी"},
        {"code": "tamil", "name": "Tamil", "native": "தமிழ்"},
        {"code": "kannada", "name": "Kannada", "native": "ಕನ್ನಡ"},
        {"code": "telugu", "name": "Telugu", "native": "తెలుగు"},
        {"code": "marathi", "name": "Marathi", "native": "मराठी"},
        {"code": "gujarati", "name": "Gujarati", "native": "ગુજરાતી"},
        {"code": "punjabi", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    ]
