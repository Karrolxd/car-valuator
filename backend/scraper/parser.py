import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_params(node: dict[str, Any]) -> dict[str, str]:
    return {p["key"]: p["value"] for p in node.get("parameters", [])}


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def parse_listing(edge: dict[str, Any]) -> dict[str, Any] | None:
    try:
        node = edge["node"]
    except (KeyError, TypeError):
        logger.warning("Brak node w edge: %s", edge)
        return None

    params = _get_params(node)

    try:
        otomoto_id = str(node["id"])
    except (KeyError, TypeError):
        logger.warning("Brak id w node")
        return None

    price_units = None
    price_raw = None
    currency = None
    try:
        price_data = node["price"]["amount"]
        price_units = int(price_data["units"])
        price_raw = str(price_data["value"])
        currency = price_data["currencyCode"]
    except (KeyError, TypeError, ValueError):
        pass

    city = None
    voivodeship = None
    try:
        city = node["location"]["city"]["name"]
        voivodeship = node["location"]["region"]["name"]
    except (KeyError, TypeError):
        pass

    return {
        "otomoto_id": otomoto_id,
        "url": node.get("url"),
        "year": _safe_int(params.get("year")),
        "mileage_km": _safe_int(params.get("mileage")),
        "engine_capacity_cm3": _safe_int(params.get("engine_capacity")),
        "engine_power_hp": _safe_int(params.get("engine_power")),
        "fuel_type": params.get("fuel_type"),
        "gearbox": params.get("gearbox"),
        "price_pln": price_units,
        "price_raw": price_raw,
        "currency": currency,
        "city": city,
        "voivodeship": voivodeship,
    }


def parse_listings(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for edge in edges:
        parsed = parse_listing(edge)
        if parsed is not None:
            results.append(parsed)
    logger.info("Sparsowano %d/%d ogłoszeń", len(results), len(edges))
    return results