import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import BACKEND_PORT, CORS_ORIGINS
from app.core.observability import metrics_registry, new_request_id, request_id_var

app = FastAPI(
    title="SasyaSampada API",
    version="1.0.0",
    description="AI-powered agricultural assistant with ML advisory and RAG APIs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or new_request_id()
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        metrics_registry.increment("http_requests_total")
        return response
    finally:
        request_id_var.reset(token)


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
