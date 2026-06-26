import json

import joblib

from app.config import MODEL_ASSETS_DIR
from app.models.schemas import LocationData, SoilData

ML_MODELS = {}
ML_AVAILABLE = False

try:
    ML_MODELS["model"] = joblib.load(MODEL_ASSETS_DIR / "cr_model.pkl")
    ML_MODELS["scaler"] = joblib.load(MODEL_ASSETS_DIR / "cr_scaler.pkl")
    ML_MODELS["encoder"] = joblib.load(MODEL_ASSETS_DIR / "cr_encoder.pkl")

    with (MODEL_ASSETS_DIR / "district_crop_map.json").open("r", encoding="utf-8") as file:
        ML_MODELS["district_crop_map"] = json.load(file)

    with (MODEL_ASSETS_DIR / "crop_district_map.json").open("r", encoding="utf-8") as file:
        ML_MODELS["crop_district_map"] = json.load(file)

    ML_AVAILABLE = True
except Exception as exc:
    print(f"⚠️ ML models not available: {exc}")
    ML_AVAILABLE = False


def loaded_model_names() -> list[str]:
    return list(ML_MODELS.keys()) if ML_AVAILABLE else []


def get_ml_crop_recommendation(soil_data: SoilData, location: LocationData) -> str | None:
    if not ML_AVAILABLE:
        return None

    try:
        user_input = [
            soil_data.N,
            soil_data.P,
            soil_data.K,
            soil_data.temperature,
            soil_data.humidity,
            soil_data.ph,
            soil_data.rainfall,
        ]

        user_input_scaled = ML_MODELS["scaler"].transform([user_input])
        prediction_idx = ML_MODELS["model"].predict(user_input_scaled)[0]
        predicted_crop = ML_MODELS["encoder"].inverse_transform([prediction_idx])[0]

        key = f"{location.state}|{location.district}"
        district_crops = ML_MODELS["district_crop_map"].get(key, [])
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
    except Exception as exc:
        print(f"Error in ML prediction: {exc}")
        return None


def get_district_crop_names(state: str, district: str) -> list[str]:
    if ML_AVAILABLE:
        return ML_MODELS["district_crop_map"].get(f"{state}|{district}", [])
    return ["Wheat", "Rice", "Maize", "Cotton"]


def get_all_crop_names() -> list[str]:
    if ML_AVAILABLE:
        return list(ML_MODELS["crop_district_map"].keys())
    return ["Wheat", "Rice", "Maize", "Cotton", "Soybean", "Barley", "Sorghum"]


def get_crop_districts(crop: str) -> list[dict[str, str]]:
    if ML_AVAILABLE:
        return ML_MODELS["crop_district_map"].get(crop, [])
    return [
        {"state": "Karnataka", "district": "Bangalore"},
        {"state": "Punjab", "district": "Ludhiana"},
        {"state": "Uttar Pradesh", "district": "Meerut"},
    ]


def get_all_districts() -> list[dict[str, str]]:
    if ML_AVAILABLE:
        districts = set()
        for key in ML_MODELS["district_crop_map"]:
            if "|" in key:
                state, district = key.split("|", 1)
                districts.add((state, district))
        return [{"state": state, "district": district} for state, district in sorted(districts)]
    return [
        {"state": "Karnataka", "district": "Bangalore"},
        {"state": "Maharashtra", "district": "Pune"},
        {"state": "Punjab", "district": "Ludhiana"},
    ]
