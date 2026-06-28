from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @model_validator(mode="before")
    @classmethod
    def parse_cors_origins(cls, values):
        if "CORS_ORIGINS" in values and isinstance(values["CORS_ORIGINS"], str):
            values["CORS_ORIGINS"] = [
                o.strip() for o in values["CORS_ORIGINS"].split(",")
            ]
        return values


settings = Settings()