import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from scraper.targets import Target

logger = logging.getLogger(__name__)

FUEL_TYPE_MAP = {
    "petrol": "petrol",
    "diesel": "diesel",
    "hybrid": "hybrid",
    "plug-in-hybrid": "phev",
    "plugin-hybrid": "phev",
    "electric": "electric",
    "lpg": "lpg",
}

GEARBOX_MAP = {
    "manual": "manual",
    "automatic": "automatic",
}

CURRENCY_TO_PLN = {
    "PLN": 1.0,
    "EUR": 4.25,
    "USD": 3.90,
}


def _normalize_price(raw: dict[str, Any]) -> int | None:
    price_pln = raw.get("price_pln")
    currency = raw.get("currency", "PLN")

    if price_pln is None:
        return None

    if currency == "PLN":
        return price_pln

    rate = CURRENCY_TO_PLN.get(currency)
    if rate is None:
        logger.warning("Nieznana waluta: %s — pomijam cenę", currency)
        return None

    converted = int(price_pln * rate)
    logger.debug("Przeliczono %s %s → %s PLN", price_pln, currency, converted)
    return converted


def _normalize_fuel_type(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = FUEL_TYPE_MAP.get(value.lower())
    if normalized is None:
        logger.debug("Nieznany fuel_type: %s", value)
    return normalized


def _normalize_gearbox(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = GEARBOX_MAP.get(value.lower())
    if normalized is None:
        logger.debug("Nieznany gearbox: %s", value)
    return normalized


def normalize(
    raw: dict[str, Any],
    model_id: int,
    target: "Target",
) -> dict[str, Any] | None:
    otomoto_id = raw.get("otomoto_id")
    if not otomoto_id:
        logger.warning("Brak otomoto_id — pomijam ogłoszenie")
        return None

    brand_slug = raw.get("brand_slug", "")
    model_slug = raw.get("model_slug", "")

    if brand_slug and brand_slug != target.brand_slug:
        logger.debug(
            "Pomijam %s — zła marka: %s != %s",
            otomoto_id,
            brand_slug,
            target.brand_slug,
        )
        return None

    if model_slug and not target.matches_model_slug(model_slug):
        logger.debug(
            "Pomijam %s — zły model: %s nie pasuje do %s",
            otomoto_id,
            model_slug,
            target.model_slug,
        )
        return None

    price_pln = _normalize_price(raw)

    return {
        "otomoto_id": otomoto_id,
        "url": raw.get("url"),
        "model_id": model_id,
        "year": raw.get("year"),
        "mileage_km": raw.get("mileage_km"),
        "engine_capacity_cm3": raw.get("engine_capacity_cm3"),
        "engine_power_hp": raw.get("engine_power_hp"),
        "fuel_type": _normalize_fuel_type(raw.get("fuel_type")),
        "gearbox": _normalize_gearbox(raw.get("gearbox")),
        "price_pln": price_pln,
        "price_raw": raw.get("price_raw"),
        "currency": raw.get("currency"),
        "city": raw.get("city"),
        "voivodeship": raw.get("voivodeship"),
        "seller_type": None,
        "accident_free": None,
        "damaged": None,
        "first_owner": None,
        "vat_invoice": None,
        "aso_serviced": None,
        "country_origin": None,
    }


def normalize_many(
    raw_listings: list[dict[str, Any]],
    model_id: int,
    target: "Target",
) -> list[dict[str, Any]]:
    results = []
    for raw in raw_listings:
        normalized = normalize(raw, model_id=model_id, target=target)
        if normalized is not None:
            results.append(normalized)
    logger.info(
        "Znormalizowano %d/%d ogłoszeń",
        len(results),
        len(raw_listings),
    )
    return results