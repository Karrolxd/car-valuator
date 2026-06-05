import asyncio
import json
import logging
import random
from typing import Any

from curl_cffi.requests import AsyncSession

from scraper.targets import Target, build_search_url

logger = logging.getLogger(__name__)

HEADERS = {
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

MIN_DELAY = 1.5
MAX_DELAY = 4.0


async def fetch_page(
    session: AsyncSession,
    url: str,
    retries: int = 3,
) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = await session.get(
                url,
                headers=HEADERS,
                impersonate="chrome",
                timeout=30,
            )
            if response.status_code == 200:
                return response.text
            logger.warning(
                "HTTP %s dla %s (próba %d/%d)",
                response.status_code,
                url,
                attempt,
                retries,
            )
        except Exception as e:
            logger.warning(
                "Błąd pobierania %s (próba %d/%d): %s",
                url,
                attempt,
                retries,
                e,
            )
        if attempt < retries:
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    return None


def extract_next_data(html: str) -> dict[str, Any] | None:
    marker = '__NEXT_DATA__"'
    start = html.find(marker)
    if start == -1:
        logger.warning("Nie znaleziono __NEXT_DATA__ w HTML")
        return None

    start = html.find(">", start)
    if start == -1:
        logger.warning("Nie znaleziono końca tagu __NEXT_DATA__")
        return None
    start += 1

    end = html.find("</script>", start)
    if end == -1:
        logger.warning("Nie znaleziono końca __NEXT_DATA__")
        return None

    try:
        return json.loads(html[start:end])
    except json.JSONDecodeError as e:
        logger.warning("Błąd parsowania __NEXT_DATA__: %s", e)
        return None


def _get_advert_search(next_data: dict[str, Any]) -> dict[str, Any] | None:
    try:
        urql = next_data["props"]["pageProps"]["urqlState"]
        keys = list(urql.keys())
        for key in keys:
            inner = json.loads(urql[key]["data"])
            if "advertSearch" in inner:
                return inner["advertSearch"]
    except (KeyError, TypeError, json.JSONDecodeError):
        pass
    return None


def get_total_pages(next_data: dict[str, Any]) -> int:
    search = _get_advert_search(next_data)
    if not search:
        return 1
    try:
        total = search.get("totalCount", 0)
        page_size = len(search.get("edges", [])) or 32
        return max(1, -(-total // page_size))  # ceiling division
    except (KeyError, TypeError, ValueError):
        return 1


def get_listings_raw(next_data: dict[str, Any]) -> list[dict[str, Any]]:
    search = _get_advert_search(next_data)
    if not search:
        return []
    return search.get("edges", [])


async def fetch_all_pages(
    target: Target,
    max_pages: int = 50,
) -> list[dict[str, Any]]:
    all_listings: list[dict[str, Any]] = []

    async with AsyncSession() as session:
        first_url = build_search_url(target, page=1)
        logger.info("Pobieranie strony 1: %s", first_url)

        html = await fetch_page(session, first_url)
        if not html:
            logger.error("Nie udało się pobrać strony 1 dla %s", target.model)
            return []

        next_data = extract_next_data(html)
        if not next_data:
            return []

        total_pages = min(get_total_pages(next_data), max_pages)
        listings = get_listings_raw(next_data)
        all_listings.extend(listings)
        logger.info(
            "%s %s: %d stron, %d ogłoszeń na stronie 1",
            target.brand,
            target.model,
            total_pages,
            len(listings),
        )

        for page in range(2, total_pages + 1):
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            url = build_search_url(target, page=page)
            logger.info("Pobieranie strony %d/%d: %s", page, total_pages, url)

            html = await fetch_page(session, url)
            if not html:
                logger.warning("Pomijam stronę %d", page)
                continue

            next_data = extract_next_data(html)
            if not next_data:
                continue

            listings = get_listings_raw(next_data)
            all_listings.extend(listings)

    logger.info(
        "%s %s: łącznie %d ogłoszeń",
        target.brand,
        target.model,
        len(all_listings),
    )
    return all_listings