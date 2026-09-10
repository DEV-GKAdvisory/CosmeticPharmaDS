"""Model descriptions page."""

from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from dashboard.data import DASHBOARD_FREQUENCIES, FREQUENCY_LABELS, load_specifications

dash.register_page(__name__, path="/models", title="Model descriptions")

_specs = load_specifications()

_LONG_FIELDS = (
    ("description", "Description"),
    ("predictors", "Predictors"),
    ("estimator", "Estimator"),
    ("monthly_ids", "Monthly predictors"),
    ("weekly_ids", "Weekly predictors"),
    ("daily_ids", "Daily predictors"),
    ("regressors", "Regressors"),
)


def _text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "none", "null"}:
        return ""
    return text


def _scroll_box(label: str, value: str, rows: int = 4) -> html.Div:
    return html.Div(
        [
            html.Label(label, className="fw-semibold small mb-1"),
            dcc.Textarea(
                value=value,
                readOnly=True,
                style={
                    "width": "100%",
                    "minHeight": f"{max(rows, 3) * 1.4}em",
                    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, monospace",
                    "fontSize": "0.85rem",
                    "resize": "vertical",
                    "background": "#f8f9fa",
                    "border": "1px solid #dee2e6",
                    "borderRadius": "6px",
                    "padding": "0.6rem 0.75rem",
                },
            ),
        ],
        className="mb-3",
    )


def _spec_card(row: pd.Series) -> dbc.Card:
    body: list = [
        html.Dl(
            [
                html.Dt("Type"),
                html.Dd(_text(row.get("model_type")) or "—"),
                html.Dt("Horizon"),
                html.Dd(_text(row.get("horizon")) or "—"),
            ],
            className="mb-3 small",
        )
    ]
    for key, label in _LONG_FIELDS:
        value = _text(row.get(key))
        if not value:
            continue
        rows = 6 if key == "description" else 3
        body.append(_scroll_box(label, value, rows=rows))

    return dbc.Card(
        [dbc.CardHeader(html.Strong(row["model"])), dbc.CardBody(body)],
        className="mb-3 shadow-sm",
    )


layout = dbc.Container(
    [
        html.H2("Model descriptions", className="mb-3"),
        html.P(
            "Full specifications for each saved model. Long fields are shown in "
            "scrollable text boxes.",
            className="text-muted",
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.Label("Frequency", className="fw-semibold"),
                    dcc.Dropdown(
                        id="models-frequency",
                        options=[
                            {"label": FREQUENCY_LABELS[f], "value": f}
                            for f in DASHBOARD_FREQUENCIES
                        ],
                        value="daily",
                        clearable=False,
                    ),
                ],
                md=4,
                className="mb-4",
            )
        ),
        html.Div(id="models-cards"),
    ],
    fluid=True,
)


@callback(Output("models-cards", "children"), Input("models-frequency", "value"))
def update_model_cards(frequency: str):
    subset = _specs[_specs["frequency"] == frequency].sort_values("model")
    if subset.empty:
        return dbc.Alert("No model specifications for this frequency.", color="warning")
    return [_spec_card(row) for _, row in subset.iterrows()]
