import asyncio
import json
import logging
from pathlib import Path

import joblib
from fastapi import FastAPI

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


async def load_model(app: FastAPI) -> None:
    if not MODEL_PATH.exists():
        logger.error("Brak pliku modelu: %s", MODEL_PATH)
        app.state.model = None
        app.state.model_metadata = None
        return

    logger.info("Ładowanie modelu: %s", MODEL_PATH)
    app.state.model = await asyncio.to_thread(joblib.load, MODEL_PATH)

    if METADATA_PATH.exists():
        with open(METADATA_PATH) as f:
            app.state.model_metadata = json.load(f)
        logger.info(
            "Model załadowany — MAPE: %.2f%%",
            app.state.model_metadata["metrics"]["mape"] * 100,
        )
    else:
        app.state.model_metadata = None
        logger.warning("Brak pliku metadata: %s", METADATA_PATH)