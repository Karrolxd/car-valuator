import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBRegressor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = "postgresql+psycopg2://car_valuator:car_valuator@localhost:5433/car_valuator"
MODEL_DIR = Path(__file__).parent.parent / "models"

NUMERIC_FEATURES = [
    "year",
    "mileage_km",
    "engine_capacity_cm3",
    "engine_power_hp",
]

CATEGORICAL_FEATURES = [
    "fuel_type",
    "gearbox",
    "brand",
    "model",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
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
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1,
        )),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, NUMERIC_FEATURES),
        ("cat", categorical_transformer, CATEGORICAL_FEATURES),
    ])

    pipeline = Pipeline([
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

    return pipeline


def evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    y_true_orig = np.expm1(y_true)
    y_pred_orig = np.expm1(y_pred)

    mape = mean_absolute_percentage_error(y_true_orig, y_pred_orig)
    mae = np.mean(np.abs(y_true_orig - y_pred_orig))
    median_ae = np.median(np.abs(y_true_orig - y_pred_orig))

    logger.info("MAPE:      %.2f%%", mape * 100)
    logger.info("MAE:       %.0f PLN", mae)
    logger.info("Median AE: %.0f PLN", median_ae)

    return {
        "mape": round(mape, 4),
        "mae": round(float(mae), 2),
        "median_ae": round(float(median_ae), 2),
    }


def save_artifacts(pipeline: Pipeline, metrics: dict) -> None:
    MODEL_DIR.mkdir(exist_ok=True)

    model_path = MODEL_DIR / "model.pkl"
    joblib.dump(pipeline, model_path)
    logger.info("Model zapisany: %s", model_path)

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "metrics": metrics,
    }

    meta_path = MODEL_DIR / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Metadata zapisana: %s", meta_path)


def main() -> None:
    engine = sa.create_engine(DB_URL)

    df = load_data(engine)
    df = clean_data(df)

    # target: log1p(cena) — stabilizuje wariancję
    y = np.log1p(df[TARGET].values)
    X = df[ALL_FEATURES]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(
        "Train: %d, Test: %d",
        len(X_train),
        len(X_test),
    )

    pipeline = build_pipeline()

    logger.info("Trening modelu...")
    pipeline.fit(X_train, y_train)

    logger.info("Ewaluacja...")
    y_pred = pipeline.predict(X_test)
    metrics = evaluate(y_test, y_pred)

    save_artifacts(pipeline, metrics)
    logger.info("Gotowe!")


if __name__ == "__main__":
    main()