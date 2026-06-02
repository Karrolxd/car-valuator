import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class FuelType(enum.Enum):
    petrol = "petrol"
    diesel = "diesel"
    hybrid = "hybrid"
    phev = "phev"
    electric = "electric"
    lpg = "lpg"


class Gearbox(enum.Enum):
    manual = "manual"
    automatic = "automatic"


class SellerType(enum.Enum):
    private = "private"
    dealer = "dealer"


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    models: Mapped[list["CarModel"]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )


class CarModel(Base):
    __tablename__ = "models"

    __table_args__ = (UniqueConstraint("brand_id", "name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("brands.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)

    brand: Mapped["Brand"] = relationship(back_populates="models")
    listings: Mapped[list["Listing"]] = relationship(
        back_populates="car_model", cascade="all, delete-orphan"
    )


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    otomoto_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("models.id"), nullable=False
    )
    year: Mapped[int | None] = mapped_column(Integer)
    mileage_km: Mapped[int | None] = mapped_column(Integer)
    engine_capacity_cm3: Mapped[int | None] = mapped_column(Integer)
    engine_power_hp: Mapped[int | None] = mapped_column(Integer)
    fuel_type: Mapped[FuelType | None] = mapped_column(Enum(FuelType))
    gearbox: Mapped[Gearbox | None] = mapped_column(Enum(Gearbox))
    price_pln: Mapped[int | None] = mapped_column(Integer)
    price_raw: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str | None] = mapped_column(Text)
    accident_free: Mapped[bool | None] = mapped_column(Boolean)
    damaged: Mapped[bool | None] = mapped_column(Boolean)
    first_owner: Mapped[bool | None] = mapped_column(Boolean)
    vat_invoice: Mapped[bool | None] = mapped_column(Boolean)
    aso_serviced: Mapped[bool | None] = mapped_column(Boolean)
    country_origin: Mapped[str | None] = mapped_column(Text)
    seller_type: Mapped[SellerType | None] = mapped_column(Enum(SellerType))
    city: Mapped[str | None] = mapped_column(Text)
    voivodeship: Mapped[str | None] = mapped_column(Text)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    car_model: Mapped["CarModel"] = relationship(back_populates="listings")


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str | None] = mapped_column(Text)
    seen: Mapped[int | None] = mapped_column(Integer)
    added: Mapped[int | None] = mapped_column(Integer)
    updated: Mapped[int | None] = mapped_column(Integer)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    input: Mapped[dict | None] = mapped_column(JSON)
    predicted_price: Mapped[int | None] = mapped_column(Integer)
    range_min: Mapped[int | None] = mapped_column(Integer)
    range_max: Mapped[int | None] = mapped_column(Integer)
    comparables_count: Mapped[int | None] = mapped_column(Integer)