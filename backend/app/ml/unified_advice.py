import json
import time
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import requests

from app.config import MANDI_PRICE_KEY, MODEL_ASSETS_DIR, OPENWEATHER_API_KEY

model = None
scaler = None
encoder = None
district_crop_map = {}
ML_AVAILABLE = False

try:
    model = joblib.load(MODEL_ASSETS_DIR / "cr_model.pkl")
    scaler = joblib.load(MODEL_ASSETS_DIR / "cr_scaler.pkl")
    encoder = joblib.load(MODEL_ASSETS_DIR / "cr_encoder.pkl")
    with (MODEL_ASSETS_DIR / "district_crop_map.json").open("r", encoding="utf-8") as file:
        district_crop_map = json.load(file)
    ML_AVAILABLE = True
except FileNotFoundError as exc:
    print(f"⚠️ ML model file missing: {exc.filename}. Falling back to simple advice mode.")
except Exception as exc:
    print(f"⚠️ Could not load ML models: {exc}. Falling back to simple advice mode.")


def get_weather(city):
    api_key = OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url, timeout=15)
    data = response.json()
    if response.status_code != 200 or "main" not in data:
        raise ValueError(f"Error fetching weather data: {data.get('message', 'Unknown error')}")

    rainfall = None
    if "rain" in data:
        rainfall = data["rain"].get("1h") or data["rain"].get("3h")

    return {
        "temp": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "rainfall": rainfall if rainfall is not None else 0,
    }


def fetch_highest_market_price(state, district, market, date=None):
    api_key = MANDI_PRICE_KEY
    if not api_key:
        raise ValueError("MANDI_PRICE_KEY not found in environment variables.")

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": 1000,
    }
    if state:
        params["filters[state]"] = state
    if district:
        params["filters[district]"] = district
    if market:
        params["filters[market]"] = market

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["records"])
    df = df.rename(columns={"Modal_x0020_Price": "modal_price", "modal_price": "modal_price"})

    if "modal_price" not in df.columns:
        raise KeyError(f"'modal_price' column not found. Got: {df.columns.tolist()}")

    df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
    df = df.dropna(subset=["modal_price"])

    if df.empty:
        return None, None

    best_row = df.loc[df["modal_price"].idxmax()]
    return best_row["commodity"], best_row["modal_price"]


crop_requirements = {
    "rice": {"temp": (20, 35), "humidity": (70, 90), "rainfall": (100, float("inf"))},
    "maize": {"temp": (18, 27), "humidity": (50, 70), "rainfall": (50, 100)},
    "jute": {"temp": (24, 37), "humidity": (70, 90), "rainfall": (150, float("inf"))},
    "cotton": {"temp": (21, 30), "humidity": (60, 80), "rainfall": (50, 100)},
    "coconut": {"temp": (20, 32), "humidity": (70, 90), "rainfall": (100, float("inf"))},
    "papaya": {"temp": (22, 30), "humidity": (60, 85), "rainfall": (100, 150)},
    "orange": {"temp": (15, 29), "humidity": (50, 70), "rainfall": (100, 120)},
    "apple": {"temp": (8, 22), "humidity": (30, 60), "rainfall": (0, 150)},
    "muskmelon": {"temp": (20, 30), "humidity": (50, 70), "rainfall": (40, 60)},
    "watermelon": {"temp": (20, 30), "humidity": (50, 70), "rainfall": (40, 60)},
    "grapes": {"temp": (15, 30), "humidity": (50, 70), "rainfall": (75, 85)},
    "mango": {"temp": (24, 30), "humidity": (50, 70), "rainfall": (0, 100)},
    "banana": {"temp": (26, 30), "humidity": (70, 90), "rainfall": (100, float("inf"))},
    "pomegranate": {"temp": (18, 35), "humidity": (40, 60), "rainfall": (50, 100)},
    "lentil": {"temp": (18, 30), "humidity": (40, 60), "rainfall": (40, 60)},
    "blackgram": {"temp": (25, 35), "humidity": (60, 80), "rainfall": (60, 80)},
    "mungbean": {"temp": (25, 35), "humidity": (60, 80), "rainfall": (60, 80)},
    "mothbeans": {"temp": (24, 30), "humidity": (50, 70), "rainfall": (50, 75)},
    "pigeonpeas": {"temp": (26, 30), "humidity": (60, 80), "rainfall": (60, 100)},
    "kidneybeans": {"temp": (18, 27), "humidity": (50, 70), "rainfall": (60, 120)},
    "chickpea": {"temp": (10, 30), "humidity": (40, 60), "rainfall": (40, 60)},
    "coffee": {"temp": (15, 28), "humidity": (70, 90), "rainfall": (150, float("inf"))},
}


def check_crop_suitability(crop, temp, humidity, rainfall):
    if crop not in crop_requirements:
        return f"No rules defined for {crop}"

    limits = crop_requirements[crop]
    reasons = []

    if not (limits["temp"][0] <= temp <= limits["temp"][1]):
        reasons.append(f"temperature={temp}°C (expected {limits['temp'][0]}-{limits['temp'][1]}°C)")
    if not (limits["rainfall"][0] <= rainfall <= limits["rainfall"][1]):
        reasons.append(f"rainfall={rainfall}mm (expected {limits['rainfall'][0]}-{limits['rainfall'][1]} mm)")
    if not (limits["humidity"][0] <= humidity <= limits["humidity"][1]):
        reasons.append(f"humidity={humidity}% (expected {limits['humidity'][0]}-{limits['humidity'][1]}%)")

    if reasons:
        return f"⚠️ Recommended crop {crop} is not suitable due to: {', '.join(reasons)}"
    return f"✅ Recommended crop {crop} is suitable under current weather conditions."


def give_advice(user_input, state, district, Market):
    features_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

    if isinstance(user_input, dict):
        user_df = pd.DataFrame([user_input], columns=features_order)
    elif isinstance(user_input, (list, np.ndarray)):
        user_df = pd.DataFrame([user_input], columns=features_order)
    elif isinstance(user_input, pd.DataFrame):
        user_df = user_input[features_order]
    else:
        raise ValueError("user_input must be dict, list, np.array, or DataFrame")

    if not ML_AVAILABLE or model is None or scaler is None or encoder is None:
        soil_data = user_df.iloc[0]
        if soil_data["ph"] < 6.0:
            recommended_crop = "Rice"
        elif soil_data["ph"] > 7.5:
            recommended_crop = "Wheat"
        else:
            recommended_crop = "Maize"

        return f"""
        🌱 Simple advisory fallback:
        - Recommended Crop: {recommended_crop}
        - Soil pH: {soil_data['ph']}
        - Location: {district}, {state}
        - Market: {Market}
        """.strip()

    soil_scaled = scaler.transform(user_df)
    ml_pred_idx = model.predict(soil_scaled)[0]
    ml_crop = encoder.inverse_transform([ml_pred_idx])[0]

    weather_data = get_weather(district)
    temp, humidity, rainfall = weather_data["temp"], weather_data["humidity"], weather_data["rainfall"]
    suitability_msg = check_crop_suitability(ml_crop, temp, humidity, rainfall)

    if "not suitable" in suitability_msg:
        time.sleep(2)
        nearest_crop = None
        min_diff = float("inf")

        for crop, limits in crop_requirements.items():
            diff = 0
            if temp < limits["temp"][0]:
                diff += limits["temp"][0] - temp
            elif temp > limits["temp"][1]:
                diff += temp - limits["temp"][1]
            if humidity < limits["humidity"][0]:
                diff += limits["humidity"][0] - humidity
            elif humidity > limits["humidity"][1]:
                diff += humidity - limits["humidity"][1]
            if rainfall < limits["rainfall"][0]:
                diff += limits["rainfall"][0] - rainfall
            elif rainfall > limits["rainfall"][1]:
                diff += rainfall - limits["rainfall"][1]

            if diff < min_diff:
                min_diff = diff
                nearest_crop = crop

        final_crop = nearest_crop if nearest_crop else ml_crop
    else:
        final_crop = ml_crop

    key = f"('{state}', '{district}')"
    if key in district_crop_map:
        crops_in_district = district_crop_map[key]
        if final_crop not in crops_in_district:
            final_crop = crops_in_district[0]

    try:
        market_prices = fetch_highest_market_price(state, district, Market, date=datetime.now().strftime("%Y-%m-%d"))
        if market_prices:
            best_crop, best_price = market_prices
        else:
            best_crop, best_price = final_crop, "N/A"
    except Exception as exc:
        print(f"⚠️ Market API unavailable: {exc}")
        best_crop, best_price = final_crop, "N/A"

    advice = f"""
    \n🌱 Based on soil, weather, ICRISAT & market:
    - ML Suggested Crop: {ml_crop}
    - Final Recommended Crop: {final_crop}
    - Best Market Crop: {best_crop} (₹{best_price})
    """
    return advice.strip()
