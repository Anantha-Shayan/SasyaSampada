import asyncio

from app.api import routes
from app.models.schemas import (
    AdvisoryRequest,
    ChatRequest,
    LocationData,
    MarketPriceRequest,
    SoilData,
    WeatherRequest,
)


def _run(coro):
    return asyncio.run(coro)


def test_health_check():
    body = _run(routes.root())

    assert body["message"].startswith("SasyaSampada API")
    assert "ml_available" in body
    assert "weather_available" in body
    assert "chatbot_available" in body


def test_api_health_and_metrics():
    health_body = _run(routes.health_check())
    metrics_body = _run(routes.metrics())

    assert health_body["status"] == "ok"
    assert metrics_body["success"] is True
    assert "counters" in metrics_body


def test_list_documents():
    body = _run(routes.list_documents())

    assert body["success"] is True
    assert isinstance(body["documents"], list)


def test_crop_advisory():
    body = _run(
        routes.get_crop_advisory(
            AdvisoryRequest(
                soil_data=SoilData(
                    N=90,
                    P=42,
                    K=43,
                    temperature=25,
                    humidity=80,
                    ph=6.5,
                    rainfall=120,
                ),
                location=LocationData(
                    state="Karnataka",
                    district="Bangalore",
                    market="Ramanagara",
                ),
            )
        )
    )

    assert body["success"] is True
    assert body["advice"]
    assert "ml_used" in body


def test_weather_uses_mock_without_api_key(monkeypatch):
    from app.services import weather

    monkeypatch.setattr(weather, "OPENWEATHER_API_KEY", None)
    monkeypatch.setattr(routes, "OPENWEATHER_API_KEY", None, raising=False)
    body = _run(routes.get_weather_data(WeatherRequest(city="Bangalore")))

    assert body["success"] is True
    assert body["weather"]["condition"] == "Sunny"


def test_market_prices():
    body = _run(
        routes.get_market_prices(
            MarketPriceRequest(
                state="Karnataka",
                district="Bangalore",
                market="Ramanagara",
            )
        )
    )

    assert body["success"] is True
    assert body["best_crop"]
    assert body["best_price"]


def test_district_crops_and_all_crops():
    district_response = _run(routes.get_district_crops("Karnataka", "Bangalore"))
    crops_response = _run(routes.get_all_crops())
    crop_districts_response = _run(routes.get_districts_for_crop("rice"))
    districts_response = _run(routes.list_districts())

    assert isinstance(district_response["crops"], list)
    assert isinstance(crops_response["crops"], list)
    assert isinstance(crop_districts_response["districts"], list)
    assert isinstance(districts_response["districts"], list)


def test_chat_accepts_question_alias():
    body = _run(routes.chat_with_assistant(ChatRequest(question="What soil is best for rice?")))

    assert "success" in body
    assert "response" in body


def test_supported_languages():
    body = _run(routes.get_supported_languages())

    assert body["success"] is True
    assert any(language["code"] == "english" for language in body["languages"])
