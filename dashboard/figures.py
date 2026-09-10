"""Plotly figure builders shared by Dash and static export."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .data import FREQUENCY_LABELS, MODEL_COLORS


def _color_map(models: list[str]) -> dict[str, str]:
    palette = px.colors.qualitative.Plotly
    colors = {}
    for index, model in enumerate(models):
        colors[model] = MODEL_COLORS.get(model, palette[index % len(palette)])
    return colors


def wape_bar_chart(metrics: pd.DataFrame, frequency: str) -> go.Figure:
    subset = (
        metrics[metrics["frequency"] == frequency]
        .sort_values("WAPE")
        .reset_index(drop=True)
    )
    colors = _color_map(subset["model"].tolist())
    fig = go.Figure(
        go.Bar(
            x=subset["model"],
            y=subset["WAPE"],
            marker_color=[colors[m] for m in subset["model"]],
            text=[f"{v:.1f}%" for v in subset["WAPE"]],
            textposition="outside",
        )
    )
    fig.update_layout(
        title=f"WAPE by model — {FREQUENCY_LABELS[frequency]}",
        xaxis_title="Model",
        yaxis_title="WAPE (%)",
        yaxis=dict(rangemode="tozero"),
        margin=dict(t=60, b=40),
        height=420,
    )
    return fig


def metrics_table_figure(metrics: pd.DataFrame, frequency: str) -> go.Figure:
    subset = (
        metrics[metrics["frequency"] == frequency]
        .sort_values("WAPE")
        .reset_index(drop=True)
    )
    display = subset[["model", "MAE", "RMSE", "sMAPE", "WAPE", "n"]].copy()
    for col in ("MAE", "RMSE", "sMAPE", "WAPE"):
        display[col] = display[col].map(lambda v: f"{v:.2f}")
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(display.columns),
                    fill_color="#f8f9fa",
                    align="left",
                    font=dict(size=13, color="#212529"),
                ),
                cells=dict(
                    values=[display[c] for c in display.columns],
                    align="left",
                    font=dict(size=12),
                ),
            )
        ]
    )
    fig.update_layout(
        title=f"Holdout metrics — {FREQUENCY_LABELS[frequency]}",
        margin=dict(t=60, l=10, r=10, b=10),
        height=280,
    )
    return fig


def holdout_forecast_chart(holdouts: pd.DataFrame, frequency: str) -> go.Figure:
    subset = holdouts[holdouts["frequency"] == frequency].copy()
    if subset.empty:
        return go.Figure().update_layout(title="No holdout data")

    actual = (
        subset.groupby("target_date", as_index=False)["actual"]
        .first()
        .sort_values("target_date")
    )
    colors = _color_map(sorted(subset["model"].unique()))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=actual["target_date"],
            y=actual["actual"],
            mode="lines+markers",
            name="Actual",
            line=dict(color="#111111", width=3),
            marker=dict(size=6),
        )
    )
    # Stable order so every model appears in the legend and plot.
    for model in sorted(subset["model"].dropna().unique()):
        group = subset[subset["model"] == model].sort_values("target_date")
        fig.add_trace(
            go.Scatter(
                x=group["target_date"],
                y=group["prediction"],
                mode="lines+markers",
                name=str(model),
                line=dict(color=colors[model], width=2.5),
                marker=dict(size=5),
            )
        )

    fig.update_layout(
        title=f"Holdout actual vs forecast — {FREQUENCY_LABELS[frequency]}",
        xaxis_title="Date",
        yaxis_title="Pharmacy sales",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=80, b=40),
        height=460,
        hovermode="x unified",
    )
    return fig


def error_by_step_chart(holdouts: pd.DataFrame, frequency: str) -> go.Figure:
    subset = holdouts[holdouts["frequency"] == frequency].copy()
    if subset.empty:
        return go.Figure().update_layout(title="No step-ahead data")
    if "step_ahead" not in subset.columns or subset["step_ahead"].isna().all():
        return go.Figure().update_layout(title="No step-ahead data")

    subset = subset.dropna(subset=["step_ahead", "actual", "prediction"])
    subset["abs_error"] = (subset["actual"] - subset["prediction"]).abs()
    by_step = (
        subset.groupby(["model", "step_ahead"], as_index=False)["abs_error"]
        .mean()
        .sort_values(["model", "step_ahead"])
    )
    colors = _color_map(sorted(by_step["model"].unique()))
    fig = px.line(
        by_step,
        x="step_ahead",
        y="abs_error",
        color="model",
        markers=True,
        color_discrete_map=colors,
        title=f"Mean absolute error by horizon step — {FREQUENCY_LABELS[frequency]}",
        labels={"step_ahead": "Step ahead", "abs_error": "MAE"},
    )
    fig.update_layout(height=420, margin=dict(t=60, b=40))
    return fig
