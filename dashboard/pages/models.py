"""Model descriptions page."""

from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from dashboard.data import DASHBOARD_FREQUENCIES, FREQUENCY_LABELS, load_specifications

dash.register_page(__name__, path="/models", title="Model descriptions")

_specs = load_specifications()


def _spec_card(row: pd.Series) -> dbc.Card:
    body = [
        html.P(row["description"], className="mb-2"),
        html.Dl(
            [
                html.Dt("Type"),
                html.Dd(row["model_type"]),
                html.Dt("Predictors"),
                html.Dd(row["predictors"] or "—"),
                html.Dt("Estimator"),
                html.Dd(row["estimator"] or "—"),
                html.Dt("Horizon"),
                html.Dd(row["horizon"]),
            ],
            className="mb-0 small",
        ),
    ]
    if pd.notna(row.get("regressors")) and str(row["regressors"]).strip():
        body.extend(
            [
                html.Hr(className="my-2"),
                html.P("Regressors", className="fw-semibold mb-1 small"),
                html.P(str(row["regressors"]), className="small text-muted mb-0"),
            ]
        )
    return dbc.Card(
        [dbc.CardHeader(html.Strong(row["model"])), dbc.CardBody(body)],
        className="mb-3 shadow-sm",
    )


layout = dbc.Container(
    [
        html.H2("Model descriptions", className="mb-3"),
        html.P(
            "Estimator details, predictors, and regressors for each saved model.",
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
