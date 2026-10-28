from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTLY_TEMPLATE = "plotly_dark"
COLORS = ["#5eead4", "#8b9cff", "#f6c177", "#e78284", "#a6d189", "#c6a0f6"]


def finish(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=70, r=24, t=100, b=48),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color="#d8e1eb"),
        hoverlabel=dict(bgcolor="#111927", font_color="#f7fafc"),
        title=dict(y=1.0, x=0.02, xanchor="left", yanchor="top"),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,.12)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)", zeroline=False)
    return fig


def exposure_outcome_chart(gradient: pd.DataFrame, outcome: str) -> go.Figure:
    frame = gradient[gradient["outcome"] == outcome]
    fig = go.Figure(
        go.Scatter(
            x=frame["exposure_quartile"],
            y=frame["mean"],
            mode="lines+markers",
            line=dict(color=COLORS[0], width=3),
            marker=dict(size=10),
            error_y=dict(
                type="data",
                symmetric=False,
                array=frame["ci_high"] - frame["mean"],
                arrayminus=frame["mean"] - frame["ci_low"],
                color=COLORS[2],
            ),
            customdata=frame[["n"]],
            hovertemplate="%{x}<br>Mean %{y:.2f}<br>n=%{customdata[0]}<extra></extra>",
        )
    )
    fig.update_layout(title=outcome.replace("_", " ").capitalize(), xaxis_title="Bedtime screen exposure", yaxis_title="Mean (95% CI)")
    return finish(fig)


def correlation_heatmap(associations: pd.DataFrame) -> go.Figure:
    pivot = associations.pivot(index="exposure", columns="outcome", values="spearman_rho")
    fig = px.imshow(
        pivot,
        text_auto=".2f",
        color_continuous_scale=[[0, "#d46a6a"], [0.5, "#172130"], [1, "#56cbbd"]],
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    fig.update_layout(title="Spearman associations across exposure and sleep outcomes")
    return finish(fig, 500)


def model_comparison_chart(frame: pd.DataFrame) -> go.Figure:
    long = frame.melt(
        id_vars="model",
        value_vars=["balanced_accuracy", "roc_auc", "pr_auc"],
        var_name="metric",
        value_name="score",
    )
    fig = px.bar(
        long,
        x="score",
        y="model",
        color="metric",
        barmode="group",
        orientation="h",
        color_discrete_sequence=COLORS,
        text_auto=".3f",
    )
    fig.update_layout(title="Nested cross-validation model comparison", xaxis_range=[0, 1])
    return finish(fig, 420)


def model_evaluation_dashboard(
    calibration: pd.DataFrame,
    roc: pd.DataFrame,
    precision_recall: pd.DataFrame,
    importance: pd.DataFrame,
    roc_auc: float,
    pr_auc: float,
    height: int = 760,
) -> go.Figure:
    """Interactive holdout diagnostics replacing the legacy static matplotlib panel."""
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Holdout calibration",
            f"Holdout ROC · AUC {roc_auc:.3f}",
            f"Precision–recall · AP {pr_auc:.3f}",
            "Permutation importance · top 10",
        ),
        horizontal_spacing=0.12,
        vertical_spacing=0.18,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines", name="Perfect calibration",
            line=dict(color="#64748b", dash="dash", width=1), showlegend=False,
        ), row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=calibration["predicted_risk"], y=calibration["observed_rate"],
            mode="lines+markers", name="Observed", line=dict(color=COLORS[0], width=3),
            marker=dict(size=8), hovertemplate="Predicted %{x:.2f}<br>Observed %{y:.2f}<extra></extra>",
            showlegend=False,
        ), row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=roc["false_positive_rate"], y=roc["true_positive_rate"],
            mode="lines", name="ROC", line=dict(color=COLORS[1], width=3),
            hovertemplate="FPR %{x:.2f}<br>TPR %{y:.2f}<extra></extra>", showlegend=False,
        ), row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines", name="Chance",
            line=dict(color="#64748b", dash="dash", width=1), showlegend=False,
        ), row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=precision_recall["recall"], y=precision_recall["precision"],
            mode="lines", name="Precision–recall", line=dict(color=COLORS[2], width=3),
            hovertemplate="Recall %{x:.2f}<br>Precision %{y:.2f}<extra></extra>", showlegend=False,
        ), row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1], y=[0.33, 0.33], mode="lines", name="Prevalence",
            line=dict(color="#64748b", dash="dash", width=1), showlegend=False,
        ), row=2, col=1,
    )
    top = importance.sort_values("importance").tail(10)
    fig.add_trace(
        go.Bar(
            x=top["importance"], y=top["feature"], orientation="h",
            marker_color=COLORS[0], name="Importance", showlegend=False,
            hovertemplate="%{y}<br>Importance %{x:.4f}<extra></extra>",
        ), row=2, col=2,
    )
    fig.update_xaxes(range=[0, 1], gridcolor="rgba(148,163,184,.12)", zeroline=False)
    fig.update_yaxes(range=[0, 1], gridcolor="rgba(148,163,184,.12)", zeroline=False)
    fig.update_xaxes(title_text="Predicted risk", row=1, col=1)
    fig.update_yaxes(title_text="Observed rate", row=1, col=1)
    fig.update_xaxes(title_text="False-positive rate", row=1, col=2)
    fig.update_yaxes(title_text="True-positive rate", row=1, col=2)
    fig.update_xaxes(title_text="Recall", row=2, col=1)
    fig.update_yaxes(title_text="Precision", row=2, col=1)
    fig.update_xaxes(title_text="Permutation importance", row=2, col=2)
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=90, r=28, t=90, b=58),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color="#d8e1eb"),
        hoverlabel=dict(bgcolor="#111927", font_color="#f7fafc"),
        showlegend=False,
    )
    for annotation in fig.layout.annotations:
        annotation.font = dict(size=13, color="#f7fafc", family="IBM Plex Sans, sans-serif")
    return fig
