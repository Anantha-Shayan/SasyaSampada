from typing import Any, Optional

from pydantic import BaseModel


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
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    language: Optional[str] = "english"
    session_id: Optional[str] = "default"
    context: Optional[dict[str, Any]] = None


class MarketPriceRequest(BaseModel):
    state: str
    district: str
    market: str
    date: Optional[str] = None
