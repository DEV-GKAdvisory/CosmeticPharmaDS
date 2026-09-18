"""Compare models page."""

from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc

from dashboard.data import DASHBOARD_FREQUENCIES, FREQUENCY_LABELS, load_holdouts, load_metrics
from dashboard.figures import (
    error_by_step_chart,
    holdout_forecast_chart,
    metrics_table_figure,
    wape_bar_chart,
)

dash.register_page(__name__, path="/", title="Compare models")

_metrics = load_metrics()
_holdouts = load_holdouts()


layout = dbc.Container(
    [
        html.H2("Model comparison", className="mb-3"),
        html.P(
            "Holdout performance for daily, weekly, and monthly pharmacy sales forecasts. "
            "Select a frequency to compare saved models.",
            className="text-muted",
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.Label("Frequency", className="fw-semibold"),
                    dcc.Dropdown(
                        id="compare-frequency",
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
        dbc.Row(dbc.Col(dcc.Graph(id="compare-wape"), width=12), className="mb-3"),
        dbc.Row(dbc.Col(dcc.Graph(id="compare-holdout"), width=12), className="mb-3"),
        dbc.Row(dbc.Col(dcc.Graph(id="compare-step-error"), width=12), className="mb-3"),
        dbc.Row(dbc.Col(dcc.Graph(id="compare-metrics-table"), width=12)),
    ],
    fluid=True,
)


@callback(
    Output("compare-wape", "figure"),
    Output("compare-holdout", "figure"),
    Output("compare-step-error", "figure"),
    Output("compare-metrics-table", "figure"),
    Input("compare-frequency", "value"),
)
def update_compare_charts(frequency: str):
    return (
        wape_bar_chart(_metrics, frequency),
        holdout_forecast_chart(_holdouts, frequency),
        error_by_step_chart(_holdouts, frequency),
        metrics_table_figure(_metrics, frequency),
    )
