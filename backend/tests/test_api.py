from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["message"].startswith("Agrigrow API")
    assert "ml_available" in body
    assert "weather_available" in body
    assert "chatbot_available" in body


def test_crop_advisory():
    response = client.post(
        "/api/advisory",
        json={
            "soil_data": {
                "N": 90,
                "P": 42,
                "K": 43,
                "temperature": 25,
                "humidity": 80,
                "ph": 6.5,
                "rainfall": 120,
            },
            "location": {
                "state": "Karnataka",
                "district": "Bangalore",
                "market": "Ramanagara",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["advice"]
    assert "ml_used" in body


def test_weather_uses_mock_without_api_key(monkeypatch):
    from app.services import weather

    monkeypatch.setattr(weather, "OPENWEATHER_API_KEY", None)
    response = client.post("/api/weather", json={"city": "Bangalore"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["weather"]["condition"] == "Sunny"


def test_market_prices():
    response = client.post(
        "/api/market-prices",
        json={
            "state": "Karnataka",
            "district": "Bangalore",
            "market": "Ramanagara",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["best_crop"]
    assert body["best_price"]


def test_district_crops_and_all_crops():
    district_response = client.get("/api/district-crops/Karnataka/Bangalore")
    crops_response = client.get("/api/crops")
    crop_districts_response = client.get("/api/crop-districts/rice")
    districts_response = client.get("/api/districts")

    assert district_response.status_code == 200
    assert crops_response.status_code == 200
    assert crop_districts_response.status_code == 200
    assert districts_response.status_code == 200
    assert isinstance(district_response.json()["crops"], list)
    assert isinstance(crops_response.json()["crops"], list)
    assert isinstance(crop_districts_response.json()["districts"], list)
    assert isinstance(districts_response.json()["districts"], list)


def test_chat_accepts_question_alias():
    response = client.post("/api/chat", json={"question": "What soil is best for rice?"})

    assert response.status_code == 200
    body = response.json()
    assert "success" in body
    assert "response" in body


def test_supported_languages():
    response = client.get("/api/chat/languages")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert any(language["code"] == "english" for language in body["languages"])
