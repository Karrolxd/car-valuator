import logging

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.prediction import (
    PredictRequest,
    PredictResponse,
    PriceBucket,
    SimilarListing,
)
from app.services.comparables import get_comparables
from ml.preprocessing import ALL_FEATURES

logger = logging.getLogger(__name__)


def _confidence(comparables_count: int) -> str:
    if comparables_count >= 30:
        return "high"
    if comparables_count >= 10:
        return "medium"
    return "low"


def _price_distribution(prices: list[int]) -> list[PriceBucket]:
    if not prices:
        return []

    prices_arr = np.array(prices)
    p5 = int(np.percentile(prices_arr, 5))
    p95 = int(np.percentile(prices_arr, 95))

    if p5 == p95:
        return [PriceBucket(bucket=f"{p5//1000}k", count=len(prices))]

    bins = np.linspace(p5, p95, 9)
    counts, edges = np.histogram(prices_arr, bins=bins)

    buckets = []
    for i, count in enumerate(counts):
        label = f"{int(edges[i])//1000}-{int(edges[i+1])//1000}k"
        buckets.append(PriceBucket(bucket=label, count=int(count)))

    return buckets


def _top5_similar(comparables, predicted_price: int) -> list[SimilarListing]:
    if not comparables:
        return []

    scored = sorted(
        comparables,
        key=lambda l: abs((l.price_pln or 0) - predicted_price),
    )

    return [
        SimilarListing(
            id=l.id,
            year=l.year,
            mileage_km=l.mileage_km,
            price_pln=l.price_pln,
            fuel_type=l.fuel_type.value if l.fuel_type else None,
            gearbox=l.gearbox.value if l.gearbox else None,
            city=l.city,
            url=l.url,
        )
        for l in scored[:5]
    ]


async def predict(
    request: PredictRequest,
    model,
    model_metadata: dict,
    session: AsyncSession,
) -> PredictResponse:
    # pobierz markę i model z bazy przez model_id
    from sqlalchemy import select
    from db.models import CarModel, Brand

    result = await session.execute(
        select(CarModel, Brand)
        .join(Brand, Brand.id == CarModel.brand_id)
        .where(CarModel.id == request.model_id)
    )
    row = result.one_or_none()
    if row is None:
        raise ValueError(f"Nie znaleziono modelu o id={request.model_id}")

    car_model, brand = row

    # przygotuj input dla modelu ML
    input_data = pd.DataFrame([{
        "year": request.year,
        "mileage_km": request.mileage_km,
        "engine_capacity_cm3": request.engine_capacity_cm3,
        "engine_power_hp": request.engine_power_hp,
        "fuel_type": request.fuel_type,
        "gearbox": request.gearbox,
        "brand": brand.name,
        "model": car_model.name,
    }])[ALL_FEATURES]

    # predykcja
    log_price = model.predict(input_data)[0]
    predicted_price = int(np.expm1(log_price))
    logger.info("Predykcja: %d PLN dla %s %s", predicted_price, brand.name, car_model.name)

    # podobne ogłoszenia
    comparables = await get_comparables(
        session=session,
        model_id=request.model_id,
        year=request.year,
        mileage_km=request.mileage_km,
    )

    prices = [c.price_pln for c in comparables if c.price_pln is not None]

    # przedział p10/p90
    if len(prices) >= 2:
        range_min = int(np.percentile(prices, 10))
        range_max = int(np.percentile(prices, 90))
    else:
        margin = int(predicted_price * 0.15)
        range_min = predicted_price - margin
        range_max = predicted_price + margin

    return PredictResponse(
        predicted_price_pln=predicted_price,
        price_range={"min": range_min, "max": range_max},
        confidence=_confidence(len(comparables)),
        comparables_count=len(comparables),
        price_distribution=_price_distribution(prices),
        similar_listings=_top5_similar(comparables, predicted_price),
    )