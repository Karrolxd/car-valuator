import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.model_loader import load_model

from app.api.catalog import router as catalog_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Start aplikacji")
    await load_model(app)
    yield
    logger.info("Zamknięcie aplikacji")


app = FastAPI(
    title="Car Valuator API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(catalog_router)

@app.get("/health")
async def health(request: Request) -> dict:
    model_loaded = getattr(request.app.state, "model", None) is not None
    trained_at = None
    if model_loaded and request.app.state.model_metadata:
        trained_at = request.app.state.model_metadata.get("trained_at")
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "trained_at": trained_at,
    }