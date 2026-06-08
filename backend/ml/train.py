import logging
from pathlib import Path

import numpy as np
import pandas as pd
import sqlalchemy as sa
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from ml.preprocessing import ALL_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES, build_preprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = "postgresql+psycopg2://car_valuator:car_valuator@localhost:5433/car_valuator"
MODEL_DIR = Path(__file__).parent.parent / "models"
TARGET = "price_pln"


def load_data(engine: sa.Engine) -> pd.DataFrame:
    logger.info("Wczytywanie danych z bazy...")
    df = pd.read_sql("""
        SELECT
            l.year,
            l.mileage_km,
            l.engine_capacity_cm3,
            l.engine_power_hp,
            l.fuel_type,
            l.gearbox,
            l.price_pln,
            b.name as brand,
            m.name as model
        FROM listings l
        JOIN models m ON l.model_id = m.id
        JOIN brands b ON m.brand_id = b.id
        WHERE l.price_pln IS NOT NULL
    """, engine)
    logger.info("Wczytano %d rekordów", len(df))
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Czyszczenie danych...")
    n_before = len(df)

    df = df[df["price_pln"] >= 5000]
    df = df[df["price_pln"] <= 500000]
    df = df[df["mileage_km"] <= 500000]
    df = df[df["year"] >= 1990]
    df = df.dropna(subset=["year", "mileage_km"])

    n_after = len(df)
    logger.info(
        "Po czyszczeniu: %d rekordów (usunięto %d)",
        n_after,
        n_before - n_after,
    )
    return df


def build_pipeline() -> Pipeline:
    preprocessor = build_preprocessor()
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", XGBRegressor(
            n_estimators=1000,
            learning_rate=0.02,
            max_depth=7,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            random_state=42,
            n_jobs=-1,
        )),
    ])


def main() -> tuple[Pipeline, np.ndarray, np.ndarray]:
    engine = sa.create_engine(DB_URL)

    df = load_data(engine)
    df = clean_data(df)

    y = np.log1p(df[TARGET].values)
    X = df[ALL_FEATURES]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info("Train: %d, Test: %d", len(X_train), len(X_test))

    pipeline = build_pipeline()

    logger.info("Trening modelu...")
    pipeline.fit(X_train, y_train)
    logger.info("Trening zakończony")

    return pipeline, X_test, y_test


if __name__ == "__main__":
    from ml.evaluate import evaluate_and_save
    pipeline, X_test, y_test = main()
    evaluate_and_save(pipeline, X_test, y_test)