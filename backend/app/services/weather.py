from datetime import datetime

from app.config import OPENWEATHER_API_KEY

WEATHER_AVAILABLE = True


def _mock_weather(message: str):
    return {
        "success": True,
        "weather": {
            "temp": 28,
            "humidity": 65,
            "rainfall": 0,
            "condition": "Sunny",
        },
        "ml_used": False,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }


def get_weather_response(city: str):
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "your_openweather_api_key_here":
        return _mock_weather("Using mock data - API key not configured")

    try:
        from app.ml.unified_advice import get_weather

        weather_data = get_weather(city)
        temp = weather_data.get("temp", 28)
        humidity = weather_data.get("humidity", 65)
        rainfall = weather_data.get("rainfall", 0)

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

        weather_data["condition"] = condition
        return {
            "success": True,
            "weather": weather_data,
            "ml_used": True,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        return _mock_weather(f"Weather API error: {str(exc)}")
