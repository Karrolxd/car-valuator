import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import update

from db.models import ScrapeRun
from db.session import AsyncSessionLocal
from scraper.fetcher import fetch_all_pages
from scraper.normalizer import normalize_many
from scraper.parser import parse_listings
from scraper.targets import TARGETS
from scraper.writer import (
    deactivate_missing,
    get_or_create_brand,
    get_or_create_model,
    upsert_listings,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def scrape_target(target, run_id: int) -> tuple[int, int, int]:
    seen = 0
    added = 0
    updated = 0

    try:
        edges = await fetch_all_pages(target, max_pages=50)
        parsed = parse_listings(edges)
        seen = len(parsed)

        async with AsyncSessionLocal() as session:
            brand_id = await get_or_create_brand(
                session, target.brand, target.brand_slug
            )
            model_id = await get_or_create_model(
                session, brand_id, target.model, target.model_slug
            )
            await session.commit()

            normalized = normalize_many(
                parsed,
                model_id=model_id,
                target=target,
            )
            added, updated = await upsert_listings(session, normalized)

            seen_ids = {r["otomoto_id"] for r in normalized}
            await deactivate_missing(session, model_id, seen_ids)

    except Exception as e:
        logger.error("Błąd scrapowania %s %s: %s", target.brand, target.model, e)

    return seen, added, updated


async def main() -> None:
    logger.info("Start scrape run — %d targetów", len(TARGETS))

    async with AsyncSessionLocal() as session:
        run = ScrapeRun(
            started_at=datetime.now(timezone.utc),
            status="running",
            seen=0,
            added=0,
            updated=0,
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        run_id = run.id

    logger.info("ScrapeRun id=%d", run_id)

    total_seen = 0
    total_added = 0
    total_updated = 0

    for target in TARGETS:
        logger.info(">>> %s %s", target.brand, target.model)
        seen, added, updated = await scrape_target(target, run_id)
        total_seen += seen
        total_added += added
        total_updated += updated

    async with AsyncSessionLocal() as session:
        await session.execute(
            update(ScrapeRun)
            .where(ScrapeRun.id == run_id)
            .values(
                finished_at=datetime.now(timezone.utc),
                status="success",
                seen=total_seen,
                added=total_added,
                updated=total_updated,
            )
        )
        await session.commit()

    logger.info(
        "Koniec — seen=%d added=%d updated=%d",
        total_seen,
        total_added,
        total_updated,
    )


if __name__ == "__main__":
    asyncio.run(main())