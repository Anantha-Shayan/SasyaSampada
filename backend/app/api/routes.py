from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.ml.inference import (
    get_all_crop_names,
    get_all_districts,
    get_crop_districts,
    get_district_crop_names,
    get_ml_crop_recommendation,
)
from app.models.schemas import AdvisoryRequest, ChatRequest, MarketPriceRequest, WeatherRequest
from app.services.chatbot import CHATBOT_AVAILABLE, get_chatbot_response, get_supported_language_list
from app.services.market import get_market_prices_response
from app.services.weather import WEATHER_AVAILABLE, get_weather_response

router = APIRouter()


@router.get("/")
async def root():
    from app.ml.inference import ML_AVAILABLE, loaded_model_names

    return {
        "message": "Agrigrow API with ML is running! (UPDATED VERSION)",
        "ml_available": ML_AVAILABLE,
        "weather_available": WEATHER_AVAILABLE,
        "chatbot_available": CHATBOT_AVAILABLE,
        "models_loaded": loaded_model_names(),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/api/advisory")
async def get_crop_advisory(request: AdvisoryRequest):
    try:
        ml_advice = get_ml_crop_recommendation(request.soil_data, request.location)
        if ml_advice:
            return {
                "success": True,
                "advice": ml_advice,
                "ml_used": True,
                "timestamp": datetime.now().isoformat(),
            }

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
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/api/weather")
async def get_weather_data(request: WeatherRequest):
    try:
        return get_weather_response(request.city)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/api/market-prices")
async def get_market_prices(request: MarketPriceRequest):
    try:
        return get_market_prices_response(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/district-crops/{state}/{district}")
async def get_district_crops(state: str, district: str):
    try:
        return {
            "success": True,
            "crops": get_district_crop_names(state, district),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/crops")
async def get_all_crops():
    try:
        return {
            "success": True,
            "crops": get_all_crop_names(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/crop-districts/{crop}")
async def get_districts_for_crop(crop: str):
    try:
        return {
            "success": True,
            "districts": get_crop_districts(crop),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/districts")
async def list_districts():
    try:
        return {
            "success": True,
            "districts": get_all_districts(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/api/chat")
async def chat_with_assistant(request: ChatRequest):
    try:
        return get_chatbot_response(
            message=request.message or request.question,
            language=request.language,
            context=request.context,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/chat/languages")
async def get_supported_languages():
    return {
        "success": True,
        "languages": get_supported_language_list(),
    }
