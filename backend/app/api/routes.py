import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.exceptions import LLMError, RAGError, RetrievalError
from app.core.observability import current_request_id, metrics_registry
from app.domain.schemas.knowledge_base import (
    DocumentCatalogEntry,
    IngestionStatus,
    LifecycleStatus,
)
from app.domain.schemas.rag import AskRequest, SearchRequest
from app.knowledge_base.paths import RAW_DIR
from app.knowledge_base.registry import (
    compute_file_sha256,
    find_duplicate_by_hash,
    get_document,
    load_catalog,
    save_catalog,
)
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
        "message": "SasyaSampada API with ML and RAG is running",
        "ml_available": ML_AVAILABLE,
        "weather_available": WEATHER_AVAILABLE,
        "chatbot_available": CHATBOT_AVAILABLE,
        "models_loaded": loaded_model_names(),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/api/health", tags=["health"])
async def health_check():
    return {
        "success": True,
        "status": "ok",
        "request_id": current_request_id(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/metrics", tags=["health"])
async def metrics():
    return {
        "success": True,
        "request_id": current_request_id(),
        **metrics_registry.snapshot(),
    }


@router.post("/api/search", tags=["rag"])
async def search_knowledge_base(request: SearchRequest):
    try:
        from app.rag.factory import build_rag_service

        return build_rag_service().search(request)
    except RetrievalError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (LLMError, RAGError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/api/ask", tags=["rag"])
async def ask_knowledge_base(request: AskRequest):
    try:
        from app.rag.factory import build_rag_service

        return build_rag_service().ask(request)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RetrievalError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RAGError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/documents", tags=["documents"])
async def list_documents(include_deleted: bool = False):
    entries = load_catalog()
    if not include_deleted:
        entries = [
            entry
            for entry in entries
            if entry.lifecycle_status != LifecycleStatus.DELETED
        ]
    return {
        "success": True,
        "documents": [entry.model_dump(mode="json") for entry in entries],
        "count": len(entries),
    }


@router.post(
    "/api/documents",
    status_code=status.HTTP_201_CREATED,
    tags=["documents"],
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    source: str | None = Form(default=None),
    organization: str | None = Form(default=None),
    language: str = Form(default="en"),
    year: int | None = Form(default=None),
    source_url: str | None = Form(default=None),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_pdf_filename(file.filename)
    destination = RAW_DIR / safe_name
    if destination.exists():
        raise HTTPException(status_code=409, detail=f"{safe_name} already exists")

    with destination.open("wb") as handle:
        shutil.copyfileobj(file.file, handle)

    content_sha256 = compute_file_sha256(destination)
    duplicate = find_duplicate_by_hash(content_sha256)
    now = datetime.now(timezone.utc)
    document_id = _unique_document_id(Path(safe_name).stem)
    entry = DocumentCatalogEntry(
        document_id=document_id,
        title=title,
        category=category,
        source=source,
        organization=organization,
        language=language,
        year=year,
        filename=safe_name,
        ingestion_status=IngestionStatus.PENDING,
        lifecycle_status=LifecycleStatus.ACTIVE,
        source_url=source_url,
        content_sha256=content_sha256,
        file_size_bytes=destination.stat().st_size,
        duplicate_of=duplicate.document_id if duplicate else None,
        created_at=now,
        updated_at=now,
    )
    entries = load_catalog()
    entries.append(entry)
    save_catalog(entries)
    metrics_registry.increment("document_upload_total")
    return {"success": True, "document": entry.model_dump(mode="json")}


@router.delete("/api/documents/{document_id}", tags=["documents"])
async def delete_document(document_id: str):
    entries = load_catalog()
    now = datetime.now(timezone.utc)
    updated = False
    for index, entry in enumerate(entries):
        if entry.document_id == document_id:
            entries[index] = entry.model_copy(
                update={
                    "lifecycle_status": LifecycleStatus.DELETED,
                    "deleted_at": now,
                    "updated_at": now,
                }
            )
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Document not found")
    save_catalog(entries)
    metrics_registry.increment("document_delete_total")
    return {"success": True, "document_id": document_id, "deleted": True}


@router.post("/api/documents/{document_id}/ingest", tags=["documents"])
async def ingest_document(document_id: str):
    if get_document(document_id) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    from app.ingestion.cli import main as ingestion_cli_main

    exit_code = ingestion_cli_main(["ingest", "--document-id", document_id])
    if exit_code != 0:
        raise HTTPException(status_code=500, detail="Ingestion failed")
    metrics_registry.increment("document_ingest_total")
    return {"success": True, "document_id": document_id}


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


def _safe_pdf_filename(filename: str) -> str:
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9_.-]+", "_", stem).strip("._-")
    if len(stem) < 3:
        stem = f"document_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    return f"{stem}.pdf"


def _unique_document_id(stem: str) -> str:
    base = re.sub(r"[^a-z0-9_]+", "_", stem.lower()).strip("_")
    if len(base) < 3:
        base = "document"
    existing = {entry.document_id for entry in load_catalog()}
    candidate = base
    suffix = 2
    while candidate in existing:
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate
