import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Listing

logger = logging.getLogger(__name__)


async def get_comparables(
    session: AsyncSession,
    model_id: int,
    year: int,
    mileage_km: int,
) -> list[Listing]:
    mileage_min = int(mileage_km * 0.8)
    mileage_max = int(mileage_km * 1.2)
    year_min = year - 2
    year_max = year + 2

    result = await session.execute(
        select(Listing)
        .where(
            Listing.model_id == model_id,
            Listing.is_active == True,
            Listing.year >= year_min,
            Listing.year <= year_max,
            Listing.mileage_km >= mileage_min,
            Listing.mileage_km <= mileage_max,
            Listing.price_pln.is_not(None),
        )
        .order_by(Listing.price_pln)
    )
    listings = result.scalars().all()
    logger.info(
        "Znaleziono %d podobnych ogłoszeń (model_id=%d, rok=%d±2, przebieg=%d±20%%)",
        len(listings),
        model_id,
        year,
        mileage_km,
    )
    return listings