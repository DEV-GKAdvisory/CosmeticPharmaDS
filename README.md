# CosmeticPharmaDS

Holdout comparison dashboard for cosmetic pharma sales forecasting models (Prophet, ProphetX, MIDAS).

Published on **GitHub Pages**: https://dev-gkadvisory.github.io/CosmeticPharmaDS/

## Views

| Page | Content |
|---|---|
| **Compare models** | WAPE bars, holdout actual vs forecast, step-ahead MAE, metrics table |
| **Model descriptions** | Estimator, predictors, regressors per model |

**Daily**, **weekly**, and **monthly** frequencies are shown.

## Local Dash server

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m dashboard
# open http://127.0.0.1:8050
```

## Update data and republish

After refreshing comparison CSVs from your analysis pipeline:

```bash
.venv/bin/python scripts/import_results.py /path/to/artifacts/comparison
.venv/bin/python -m dashboard.build_static
git add data/ docs/
git commit -m "Update dashboard results"
git push
```

GitHub → **Settings → Pages** → source: **GitHub Actions** (workflow deploys the `docs/` folder).

## Repository layout

```
data/                 # comparison CSVs (daily + weekly + monthly)
dashboard/            # Dash app + static export
docs/                 # static site served by GitHub Pages
scripts/import_results.py
```
