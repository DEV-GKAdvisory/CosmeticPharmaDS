#!/usr/bin/env python3
"""Import comparison CSVs from a local analysis project into data/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import DASHBOARD_FREQUENCIES
from dashboard.sanitize import sanitize_text

DATA_DIR = REPO_ROOT / "data"

FILES = (
    "metrics_by_model.csv",
    "holdout_forecasts_long.csv",
    "model_specifications.csv",
)


def _sanitize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in out.select_dtypes(include="object").columns:
        out[col] = out[col].map(sanitize_text)
    return out


def import_results(source_dir: Path) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        src = source_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing {src}")
        frame = pd.read_csv(src)
        if "frequency" in frame.columns:
            frame = frame[frame["frequency"].isin(DASHBOARD_FREQUENCIES)]
        if name == "model_specifications.csv":
            frame = _sanitize_frame(frame)
        dest = DATA_DIR / name
        frame.to_csv(dest, index=False)
        print(f"Wrote {dest} ({len(frame)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Path to comparison/ folder with metrics and holdout CSVs",
    )
    args = parser.parse_args()
    source = args.source
    if source is None:
        default = REPO_ROOT.parent / "artifacts" / "comparison"
        source = default if default.exists() else None
    if source is None:
        parser.error("Provide source path to comparison/ folder")
    import_results(source.resolve())


if __name__ == "__main__":
    main()
