import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.prediction import PredictRequest, PredictResponse
from app.services.prediction import predict
from db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(tags=["predict"])


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/predict", response_model=PredictResponse)
async def predict_endpoint(
    body: PredictRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> PredictResponse:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model nie jest załadowany")

    model_metadata = getattr(request.app.state, "model_metadata", None)

    try:
        result = await predict(
            request=body,
            model=model,
            model_metadata=model_metadata,
            session=session,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Błąd predykcji: %s", e)
        raise HTTPException(status_code=500, detail="Błąd wewnętrzny serwera")