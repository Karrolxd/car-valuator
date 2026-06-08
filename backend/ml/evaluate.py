import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.pipeline import Pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "models"


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    y_true_orig = np.expm1(y_true)
    y_pred_orig = np.expm1(y_pred)

    mape = mean_absolute_percentage_error(y_true_orig, y_pred_orig)
    mae = float(np.mean(np.abs(y_true_orig - y_pred_orig)))
    median_ae = float(np.median(np.abs(y_true_orig - y_pred_orig)))

    logger.info("MAPE:      %.2f%%", mape * 100)
    logger.info("MAE:       %.0f PLN", mae)
    logger.info("Median AE: %.0f PLN", median_ae)

    if mape * 100 <= 10:
        logger.info("✅ Cel osiągnięty — MAPE <= 10%%")
    else:
        logger.warning("⚠️  Cel nieosiągnięty — MAPE > 10%% (%.2f%%)", mape * 100)

    return {
        "mape": round(mape, 4),
        "mae": round(mae, 2),
        "median_ae": round(median_ae, 2),
    }


def plot_errors(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    y_true_orig = np.expm1(y_true)
    y_pred_orig = np.expm1(y_pred)
    errors_pct = (y_pred_orig - y_true_orig) / y_true_orig * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # histogram błędów procentowych
    axes[0].hist(errors_pct, bins=50, color="steelblue", edgecolor="white")
    axes[0].axvline(0, color="red", linestyle="--", linewidth=1)
    axes[0].set_title("Rozkład błędów procentowych")
    axes[0].set_xlabel("Błąd (%)")
    axes[0].set_ylabel("Liczba predykcji")

    # predykcja vs rzeczywistość
    axes[1].scatter(y_true_orig, y_pred_orig, alpha=0.1, s=1, color="coral")
    max_val = max(y_true_orig.max(), y_pred_orig.max())
    axes[1].plot([0, max_val], [0, max_val], "r--", linewidth=1)
    axes[1].set_title("Predykcja vs Rzeczywistość")
    axes[1].set_xlabel("Cena rzeczywista (PLN)")
    axes[1].set_ylabel("Cena predykowana (PLN)")

    plt.tight_layout()
    plot_path = MODEL_DIR / "evaluation_plots.png"
    plt.savefig(plot_path, dpi=150)
    logger.info("Wykresy zapisane: %s", plot_path)
    plt.show()


def save_artifacts(pipeline: Pipeline, metrics: dict) -> None:
    MODEL_DIR.mkdir(exist_ok=True)

    model_path = MODEL_DIR / "model.pkl"
    joblib.dump(pipeline, model_path)
    logger.info("Model zapisany: %s", model_path)

    from ml.preprocessing import ALL_FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES

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


def evaluate_and_save(
    pipeline: Pipeline,
    X_test,
    y_test: np.ndarray,
) -> None:
    logger.info("Ewaluacja modelu...")
    y_pred = pipeline.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)
    plot_errors(y_test, y_pred)
    save_artifacts(pipeline, metrics)
    logger.info("Gotowe!")


if __name__ == "__main__":
    from ml.train import main as train_main
    pipeline, X_test, y_test = train_main()
    evaluate_and_save(pipeline, X_test, y_test)