from pydantic import BaseModel


class BrandResponse(BaseModel):
    id: int
    name: str
    slug: str


class ModelResponse(BaseModel):
    id: int
    name: str
    slug: str
    listings_count: int