import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Brand, CarModel, Listing

logger = logging.getLogger(__name__)


async def get_or_create_brand(
    session: AsyncSession,
    name: str,
    slug: str,
) -> int:
    result = await session.execute(
        select(Brand).where(Brand.slug == slug)
    )
    brand = result.scalar_one_or_none()
    if brand:
        return brand.id

    brand = Brand(name=name, slug=slug)
    session.add(brand)
    await session.flush()
    logger.info("Nowa marka: %s", name)
    return brand.id


async def get_or_create_model(
    session: AsyncSession,
    brand_id: int,
    name: str,
    slug: str,
) -> int:
    result = await session.execute(
        select(CarModel).where(
            CarModel.brand_id == brand_id,
            CarModel.name == name,
        )
    )
    model = result.scalar_one_or_none()
    if model:
        return model.id

    model = CarModel(brand_id=brand_id, name=name, slug=slug)
    session.add(model)
    await session.flush()
    logger.info("Nowy model: %s", name)
    return model.id


async def upsert_listings(
    session: AsyncSession,
    listings: list[dict[str, Any]],
) -> tuple[int, int]:
    if not listings:
        return 0, 0

    now = datetime.now(timezone.utc)
    added = 0
    updated = 0

    for listing in listings:
        stmt = (
            insert(Listing)
            .values(
                **listing,
                first_seen=now,
                last_seen=now,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=["otomoto_id"],
                set_={
                    "last_seen": now,
                    "updated_at": now,
                    "is_active": True,
                    "price_pln": listing.get("price_pln"),
                    "price_raw": listing.get("price_raw"),
                    "url": listing.get("url"),
                },
            )
        )
        result = await session.execute(stmt)
        if result.rowcount == 1:
            added += 1
        else:
            updated += 1

    await session.commit()
    logger.info("Zapisano: %d nowych, %d zaktualizowanych", added, updated)
    return added, updated


async def deactivate_missing(
    session: AsyncSession,
    model_id: int,
    seen_ids: set[str],
) -> int:
    result = await session.execute(
        select(Listing).where(
            Listing.model_id == model_id,
            Listing.is_active == True,
            Listing.otomoto_id.not_in(seen_ids),
        )
    )
    listings = result.scalars().all()

    now = datetime.now(timezone.utc)
    for listing in listings:
        listing.is_active = False
        listing.updated_at = now

    await session.commit()
    count = len(listings)
    if count:
        logger.info("Dezaktywowano %d nieaktywnych ogłoszeń", count)
    return count