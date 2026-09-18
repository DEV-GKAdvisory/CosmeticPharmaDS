"""Build a static site in docs/ for GitHub Pages."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from dashboard.data import (
    DASHBOARD_FREQUENCIES,
    FREQUENCY_LABELS,
    export_payload,
    load_holdouts,
    load_metrics,
)
from dashboard.figures import (
    error_by_step_chart,
    holdout_forecast_chart,
    metrics_table_figure,
    wape_bar_chart,
)

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
SITE_TITLE = "Cosmetic Pharma DS"

STYLE = """
body { font-family: system-ui, -apple-system, sans-serif; margin: 0; background: #f8f9fa; color: #212529; }
header { background: #2c3e50; color: #fff; padding: 1rem 1.5rem; }
header a { color: #ecf0f1; text-decoration: none; margin-right: 1.25rem; font-weight: 500; }
header a.active, header a:hover { color: #fff; text-decoration: underline; }
header .brand { font-weight: 700; font-size: 1.15rem; margin-right: 2rem; }
main { max-width: 1100px; margin: 0 auto; padding: 1.5rem; }
.card { background: #fff; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.card h3 { margin-top: 0; }
.muted { color: #6c757d; }
label { font-weight: 600; display: block; margin-bottom: .35rem; }
select { padding: .4rem .6rem; font-size: 1rem; min-width: 280px; }
.plot { background: #fff; border-radius: 8px; padding: .5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
dl { display: grid; grid-template-columns: 120px 1fr; gap: .25rem .75rem; margin: 0; font-size: .92rem; }
dt { font-weight: 600; }
dd { margin: 0; color: #495057; }
.hero { background: #fff; border-radius: 8px; padding: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.hero h1 { margin-top: 0; }
.grid { display: grid; gap: 1rem; }
@media (min-width: 720px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
.field-label { font-weight: 600; font-size: .85rem; display: block; margin: .75rem 0 .35rem; }
.scrollbox {
  width: 100%;
  min-height: 4.5em;
  max-height: 12em;
  overflow: auto;
  resize: vertical;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .85rem;
  line-height: 1.4;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: .6rem .75rem;
  color: #212529;
  white-space: pre-wrap;
  box-sizing: border-box;
}
.scrollbox.tall { min-height: 7em; max-height: 16em; }
"""


def _header(active: str) -> str:
    links = [
        ("index.html", "Home", "home"),
        ("compare.html", "Compare models", "compare"),
        ("models.html", "Model descriptions", "models"),
    ]
    nav = " ".join(
        f'<a href="{href}" class="{"active" if key == active else ""}">{label}</a>'
        for href, label, key in links
    )
    return f"""
<header>
  <span class="brand">{SITE_TITLE}</span>
  {nav}
</header>
"""


def _page(title: str, active: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — {SITE_TITLE}</title>
  <style>{STYLE}</style>
</head>
<body>
{_header(active)}
<main>
{body}
</main>
</body>
</html>
"""


def _figure_bundle(metrics: pd.DataFrame, holdouts: pd.DataFrame) -> dict:
    bundle = {}
    for freq in DASHBOARD_FREQUENCIES:
        bundle[freq] = {
            "wape": json.loads(wape_bar_chart(metrics, freq).to_json()),
            "holdout": json.loads(holdout_forecast_chart(holdouts, freq).to_json()),
            "step_error": json.loads(error_by_step_chart(holdouts, freq).to_json()),
            "metrics_table": json.loads(
                metrics_table_figure(metrics, freq).to_json()
            ),
        }
    return bundle


def _write_index() -> None:
    body = """
<div class="hero">
  <h1>Cosmetic pharma sales forecasting</h1>
  <p class="muted">Holdout comparison of Prophet, ProphetX, and MIDAS models on daily, weekly, and monthly frequencies.</p>
  <div class="grid grid-2" style="margin-top: 1.5rem;">
    <div class="card">
      <h3>Compare models</h3>
      <p>WAPE bars, holdout paths, step-ahead errors, and metrics tables.</p>
      <p><a href="compare.html">Open comparison →</a></p>
    </div>
    <div class="card">
      <h3>Model descriptions</h3>
      <p>Estimator details, predictors, and regressors per saved model.</p>
      <p><a href="models.html">View specifications →</a></p>
    </div>
  </div>
</div>
"""
    (DOCS_DIR / "index.html").write_text(
        _page("Home", "home", body), encoding="utf-8"
    )


def _write_compare(figures: dict) -> None:
    options = "".join(
        f'<option value="{f}">{FREQUENCY_LABELS[f]}</option>'
        for f in DASHBOARD_FREQUENCIES
    )
    body = f"""
<h2>Model comparison</h2>
<p class="muted">Select frequency to compare holdout performance across saved models.</p>
<label for="frequency">Frequency</label>
<select id="frequency">{options}</select>
<div class="plot" id="plot-wape"></div>
<div class="plot" id="plot-holdout"></div>
<div class="plot" id="plot-step"></div>
<div class="plot" id="plot-metrics"></div>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<script>
const FIGURES = {json.dumps(figures)};
function render(freq) {{
  const f = FIGURES[freq];
  Plotly.newPlot('plot-wape', f.wape.data, f.wape.layout, {{responsive: true}});
  Plotly.newPlot('plot-holdout', f.holdout.data, f.holdout.layout, {{responsive: true}});
  Plotly.newPlot('plot-step', f.step_error.data, f.step_error.layout, {{responsive: true}});
  Plotly.newPlot('plot-metrics', f.metrics_table.data, f.metrics_table.layout, {{responsive: true}});
}}
document.getElementById('frequency').addEventListener('change', (e) => render(e.target.value));
render('daily');
</script>
"""
    (DOCS_DIR / "compare.html").write_text(
        _page("Compare models", "compare", body), encoding="utf-8"
    )


def _write_models(specs: list[dict]) -> None:
    options = "".join(
        f'<option value="{f}">{FREQUENCY_LABELS[f]}</option>'
        for f in DASHBOARD_FREQUENCIES
    )
    body = f"""
<h2>Model descriptions</h2>
<p class="muted">Full specifications for each saved model. Long fields use scrollable text boxes.</p>
<label for="frequency">Frequency</label>
<select id="frequency">{options}</select>
<div id="cards" style="margin-top: 1rem;"></div>
<script>
const SPECS = {json.dumps(specs, allow_nan=False)};
const LONG_FIELDS = [
  ["description", "Description", true],
  ["predictors", "Predictors", false],
  ["estimator", "Estimator", false],
  ["monthly_ids", "Monthly predictors", false],
  ["weekly_ids", "Weekly predictors", false],
  ["daily_ids", "Daily predictors", false],
  ["regressors", "Regressors", false],
];
function esc(s) {{
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
function hasText(v) {{
  if (v === null || v === undefined) return false;
  const t = String(v).trim();
  return t.length > 0 && t.toLowerCase() !== 'nan' && t.toLowerCase() !== 'none' && t.toLowerCase() !== 'null';
}}
function field(label, value, tall) {{
  return `<label class="field-label">${{esc(label)}}</label>` +
    `<textarea class="scrollbox${{tall ? ' tall' : ''}}" readonly>${{esc(value)}}</textarea>`;
}}
function card(row) {{
  const parts = [
    `<div class="card"><h3>${{esc(row.model)}}</h3>`,
    `<dl><dt>Type</dt><dd>${{esc(row.model_type || '—')}}</dd>`,
    `<dt>Horizon</dt><dd>${{esc(row.horizon || '—')}}</dd></dl>`
  ];
  for (const [key, label, tall] of LONG_FIELDS) {{
    if (hasText(row[key])) parts.push(field(label, row[key], tall));
  }}
  parts.push('</div>');
  return parts.join('');
}}
function render(freq) {{
  const rows = SPECS.filter(r => r.frequency === freq).sort((a,b) => a.model.localeCompare(b.model));
  document.getElementById('cards').innerHTML = rows.length
    ? rows.map(card).join('')
    : '<div class="card">No specifications for this frequency.</div>';
}}
document.getElementById('frequency').addEventListener('change', (e) => render(e.target.value));
render('daily');
</script>
"""
    (DOCS_DIR / "models.html").write_text(
        _page("Model descriptions", "models", body), encoding="utf-8"
    )


def build() -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics()
    holdouts = load_holdouts()
    payload = export_payload()

    assets = DOCS_DIR / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "data.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8"
    )

    figures = _figure_bundle(metrics, holdouts)
    _write_index()
    _write_compare(figures)
    _write_models(payload["specifications"])

    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Static dashboard written to {DOCS_DIR}")
    return DOCS_DIR


if __name__ == "__main__":
    build()