"""Load comparison data bundled with the dashboard repository."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .sanitize import sanitize_text

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DASHBOARD_FREQUENCIES = ("daily", "monthly")

FREQUENCY_LABELS = {
    "daily": "Daily (1-month horizon)",
    "monthly": "Monthly (1-year horizon)",
}

MODEL_COLORS = {
    "ProphetX": "#636EFA",
    "prophet": "#EF553B",
    "MIDAS_all": "#00CC96",
    "MIDAS_daily": "#AB63FA",
    "MIDAS_monthly": "#FFA15A",
    "Avg_MIDAS": "#19D3F3",
    "Avg_ex_prophet": "#FF6692",
}


def data_dir(root: Path | None = None) -> Path:
    return root or DATA_DIR


def _sanitize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(sanitize_text)
    return out


def _fill_step_ahead(frame: pd.DataFrame) -> pd.DataFrame:
    """Prophet holdouts often omit step_ahead; derive it from date order."""
    out = frame.copy()
    if "step_ahead" not in out.columns:
        out["step_ahead"] = pd.NA
    out = out.sort_values(["frequency", "model", "target_date"]).reset_index(drop=True)
    missing = out["step_ahead"].isna()
    if missing.any():
        derived = out.groupby(["frequency", "model"], sort=False).cumcount() + 1
        out.loc[missing, "step_ahead"] = derived.loc[missing]
    out["step_ahead"] = out["step_ahead"].astype(float)
    return out


def _records_clean(frame: pd.DataFrame) -> list[dict]:
    """Convert frame to JSON-safe records (NaN / NaT → None)."""
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def load_metrics(root: Path | None = None) -> pd.DataFrame:
    path = data_dir(root) / "metrics_by_model.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run scripts/import_results.py first.")
    frame = pd.read_csv(path)
    return _sanitize_frame(frame[frame["frequency"].isin(DASHBOARD_FREQUENCIES)])


def load_holdouts(root: Path | None = None) -> pd.DataFrame:
    path = data_dir(root) / "holdout_forecasts_long.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run scripts/import_results.py first.")
    frame = pd.read_csv(path, parse_dates=["target_date", "forecast_origin"])
    frame = frame[frame["frequency"].isin(DASHBOARD_FREQUENCIES)].copy()
    return _fill_step_ahead(frame)


def load_specifications(root: Path | None = None) -> pd.DataFrame:
    path = data_dir(root) / "model_specifications.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run scripts/import_results.py first.")
    frame = pd.read_csv(path)
    return _sanitize_frame(frame[frame["frequency"].isin(DASHBOARD_FREQUENCIES)])


def export_payload(root: Path | None = None) -> dict:
    metrics = load_metrics(root)
    holdouts = load_holdouts(root)
    specs = load_specifications(root)

    holdouts = holdouts.copy()
    holdouts["target_date"] = holdouts["target_date"].dt.strftime("%Y-%m-%d")
    if "forecast_origin" in holdouts.columns:
        holdouts["forecast_origin"] = holdouts["forecast_origin"].dt.strftime(
            "%Y-%m-%d"
        )

    return {
        "frequencies": list(DASHBOARD_FREQUENCIES),
        "frequency_labels": FREQUENCY_LABELS,
        "metrics": _records_clean(metrics),
        "holdouts": _records_clean(holdouts),
        "specifications": _records_clean(specs),
        "model_colors": MODEL_COLORS,
    }
