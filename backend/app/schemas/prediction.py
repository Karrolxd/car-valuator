from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    model_id: int
    year: int = Field(ge=1990, le=2026)
    mileage_km: int = Field(ge=0, le=500000)
    fuel_type: str | None = None
    gearbox: str | None = None
    engine_capacity_cm3: int | None = None
    engine_power_hp: int | None = None


class PriceBucket(BaseModel):
    bucket: str
    count: int


class SimilarListing(BaseModel):
    id: int
    year: int | None
    mileage_km: int | None
    price_pln: int | None
    fuel_type: str | None
    gearbox: str | None
    city: str | None
    url: str | None


class PredictResponse(BaseModel):
    predicted_price_pln: int
    price_range: dict[str, int]
    confidence: str
    comparables_count: int
    price_distribution: list[PriceBucket]
    similar_listings: list[SimilarListing]