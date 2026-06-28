import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.catalog import BrandResponse, ModelResponse
from db.models import Brand, CarModel, Listing
from db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/brands", tags=["catalog"])


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("", response_model=list[BrandResponse])
async def get_brands(
    session: AsyncSession = Depends(get_session),
) -> list[BrandResponse]:
    result = await session.execute(
        select(Brand)
        .join(CarModel, CarModel.brand_id == Brand.id)
        .join(Listing, Listing.model_id == CarModel.id)
        .where(Listing.is_active == True)
        .distinct()
        .order_by(Brand.name)
    )
    brands = result.scalars().all()
    return [
        BrandResponse(id=b.id, name=b.name, slug=b.slug)
        for b in brands
    ]


@router.get("/{brand_id}/models", response_model=list[ModelResponse])
async def get_models(
    brand_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[ModelResponse]:
    result = await session.execute(
        select(
            CarModel,
            func.count(Listing.id).label("listings_count"),
        )
        .join(Listing, Listing.model_id == CarModel.id)
        .where(
            CarModel.brand_id == brand_id,
            Listing.is_active == True,
        )
        .group_by(CarModel.id)
        .order_by(CarModel.name)
    )
    rows = result.all()
    return [
        ModelResponse(
            id=row.CarModel.id,
            name=row.CarModel.name,
            slug=row.CarModel.slug,
            listings_count=row.listings_count,
        )
        for row in rows
    ]