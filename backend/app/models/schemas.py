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


class DocumentMetadata(BaseModel):
    document_id: str
    title: Optional[str] = None
    quality: Optional[str] = None
    source_url: Optional[str] = None


class ParsedDocument(BaseModel):
    document_id: str
    metadata: dict[str, Any]
    pages: list[dict[str, Any]]
    source_url: Optional[str] = None

class CleanDocument(BaseModel):
    document_id: str
    metadata: DocumentMetadata
    content: str

class DocumentChunk(BaseModel):
    document_id: str
    metadata: DocumentMetadata
    chunks: dict[int, str]
    chunk_size: int
    total_chunks: int