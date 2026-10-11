"""Plotly-based chart builders for EDA visualizations in EconLens AI.

Produces dark-themed, publication-quality charts for indicator distributions,
regional comparisons, correlation heatmaps, and data quality visualizations.

Visual Direction: Deep charcoal background, teal/cyan accents, restrained
colour use, high-contrast typography, and consistent formatting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from src.utils.logging_config import get_logger

logger = get_logger("analytics.eda_charts")

# ==============================================================================
# Dark Theme Constants
# ==============================================================================
THEME = {
    "bg": "#0f1117",
    "paper_bg": "#161b22",
    "card_bg": "#1c2333",
    "grid": "rgba(255, 255, 255, 0.06)",
    "text": "#e6edf3",
    "text_secondary": "#8b949e",
    "accent_teal": "#2dd4bf",
    "accent_cyan": "#22d3ee",
    "accent_blue": "#38bdf8",
    "accent_indigo": "#818cf8",
    "accent_purple": "#a78bfa",
    "positive": "#34d399",
    "negative": "#f87171",
    "warning": "#fbbf24",
    "neutral": "#64748b",
}

# Curated colour palette for charts
CHART_PALETTE = [
    "#2dd4bf", "#22d3ee", "#38bdf8", "#818cf8", "#a78bfa",
    "#f472b6", "#fb923c", "#fbbf24", "#34d399", "#60a5fa",
    "#e879f9", "#94a3b8", "#67e8f9", "#c084fc", "#fcd34d",
]

# Default layout for all charts
DEFAULT_LAYOUT = dict(
    paper_bgcolor=THEME["paper_bg"],
    plot_bgcolor=THEME["card_bg"],
    font=dict(family="Inter, -apple-system, sans-serif", color=THEME["text"], size=12),
    margin=dict(l=60, r=30, t=50, b=60),
    xaxis=dict(gridcolor=THEME["grid"], zerolinecolor=THEME["grid"]),
    yaxis=dict(gridcolor=THEME["grid"], zerolinecolor=THEME["grid"]),
    hoverlabel=dict(
        bgcolor=THEME["card_bg"],
        bordercolor=THEME["accent_teal"],
        font=dict(color=THEME["text"], size=12),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=THEME["text_secondary"]),
    ),
)


def _apply_theme(fig: "go.Figure") -> "go.Figure":
    """Applies the standard dark theme layout to a Plotly figure."""
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def _check_plotly() -> None:
    """Raises ImportError if Plotly is not available."""
    if not HAS_PLOTLY:
        raise ImportError("Plotly is required for chart generation. Install with: pip install plotly")


# ==============================================================================
# Chart Builders
# ==============================================================================

def build_regional_comparison_bar(
    rankings: List[Dict[str, Any]],
    indicator_name: str,
    unit: str,
    reference_period: str,
    top_n: Optional[int] = None,
    show_mean: bool = True,
    group_mean: Optional[float] = None,
) -> "go.Figure":
    """Horizontal bar chart comparing indicator values across regions.

    Args:
        rankings: List of dicts with region_name, value, rank.
        indicator_name: Human-readable indicator name.
        unit: Measurement unit for axis label.
        reference_period: Period label for chart title.
        top_n: If set, show only top N and bottom N regions.
        show_mean: Whether to add a mean reference line.
        group_mean: The group mean value.

    Returns:
        Plotly Figure.
    """
    _check_plotly()

    if not rankings:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for this indicator.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color=THEME["text_secondary"]),
        )
        return _apply_theme(fig)

    df = pd.DataFrame(rankings)

    if top_n and len(df) > top_n * 2:
        top = df.head(top_n)
        bottom = df.tail(top_n)
        df = pd.concat([top, bottom])

    # Sort ascending for horizontal bar (top values at top)
    df = df.sort_values("value", ascending=True)

    # Colour bars by deviation from mean
    colors = []
    for _, row in df.iterrows():
        dev = row.get("deviation_from_mean", 0)
        if dev is not None and dev > 0:
            colors.append(THEME["accent_teal"])
        elif dev is not None and dev < 0:
            colors.append(THEME["accent_blue"])
        else:
            colors.append(THEME["neutral"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["region_name"],
        x=df["value"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:,.2f}" for v in df["value"]],
        textposition="outside",
        textfont=dict(size=10, color=THEME["text_secondary"]),
        hovertemplate=(
            "<b>%{y}</b><br>"
            f"{indicator_name}: %{{x:,.2f}} {unit}<br>"
            "<extra></extra>"
        ),
    ))

    if show_mean and group_mean is not None:
        fig.add_vline(
            x=group_mean,
            line_dash="dot",
            line_color=THEME["warning"],
            line_width=1.5,
            annotation_text=f"Mean: {group_mean:,.2f}",
            annotation_font=dict(color=THEME["warning"], size=10),
            annotation_position="top",
        )

    fig.update_layout(
        title=dict(
            text=f"{indicator_name} — Regional Comparison ({reference_period})",
            font=dict(size=15),
        ),
        xaxis_title=f"{indicator_name} ({unit})",
        yaxis_title="",
        height=max(400, len(df) * 28),
        showlegend=False,
    )

    return _apply_theme(fig)


def build_indicator_histogram(
    values: List[float],
    indicator_name: str,
    unit: str,
    reference_period: str,
    bins: int = 15,
) -> "go.Figure":
    """Distribution histogram for an indicator across regions.

    Args:
        values: List of numeric values.
        indicator_name: Human-readable name.
        unit: Measurement unit.
        reference_period: Period label.
        bins: Number of histogram bins.

    Returns:
        Plotly Figure.
    """
    _check_plotly()

    if not values:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid observations for distribution.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color=THEME["text_secondary"]),
        )
        return _apply_theme(fig)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=bins,
        marker=dict(
            color=THEME["accent_teal"],
            line=dict(color=THEME["paper_bg"], width=1),
        ),
        opacity=0.85,
        hovertemplate=(
            f"Range: %{{x}}<br>"
            "Count: %{y}<br>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(
            text=f"Distribution — {indicator_name} ({reference_period})",
            font=dict(size=15),
        ),
        xaxis_title=f"{indicator_name} ({unit})",
        yaxis_title="Number of Regions",
        bargap=0.05,
        height=400,
    )

    return _apply_theme(fig)


def build_box_plot(
    data: Dict[str, List[float]],
    title: str = "Indicator Distributions",
    y_label: str = "Value",
) -> "go.Figure":
    """Box plot comparing distributions of multiple indicators.

    Args:
        data: Dict mapping indicator names to lists of values.
        title: Chart title.
        y_label: Y-axis label.

    Returns:
        Plotly Figure.
    """
    _check_plotly()

    fig = go.Figure()
    for i, (name, values) in enumerate(data.items()):
        color = CHART_PALETTE[i % len(CHART_PALETTE)]
        fig.add_trace(go.Box(
            y=values,
            name=name,
            marker_color=color,
            boxmean="sd",
            jitter=0.3,
            pointpos=-1.5,
            hovertemplate=(
                f"<b>{name}</b><br>"
                "Value: %{y:,.2f}<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        yaxis_title=y_label,
        height=450,
        showlegend=True,
    )

    return _apply_theme(fig)


def build_correlation_heatmap(
    corr_matrix: "pd.DataFrame",
    title: str = "Indicator Correlation Matrix",
) -> "go.Figure":
    """Heatmap of pairwise indicator correlations.

    Args:
        corr_matrix: Pandas DataFrame of correlation values (indicators x indicators).
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    _check_plotly()

    # Short labels for readability
    labels = [c.replace("_", " ").title()[:20] for c in corr_matrix.columns]

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale=[
            [0, "#f87171"],
            [0.25, "#1c2333"],
            [0.5, "#1c2333"],
            [0.75, "#2dd4bf"],
            [1.0, "#22d3ee"],
        ],
        zmin=-1,
        zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr_matrix.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color=THEME["text"]),
        hovertemplate=(
            "%{x} vs %{y}<br>"
            "Correlation: %{z:.3f}<br>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title="r",
            titlefont=dict(color=THEME["text_secondary"]),
            tickfont=dict(color=THEME["text_secondary"]),
        ),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        height=max(400, len(labels) * 40),
        xaxis=dict(tickangle=45),
    )

    return _apply_theme(fig)


def build_scatter_plot(
    scatter_data: Dict[str, Any],
    show_trendline: bool = False,
) -> "go.Figure":
    """Scatter plot showing relationship between two indicators.

    Args:
        scatter_data: Dict from ExploratoryAnalyzer.compute_pairwise_scatter_data.
        show_trendline: Whether to add a linear trendline.

    Returns:
        Plotly Figure.
    """
    _check_plotly()

    x = scatter_data.get("x_values", [])
    y = scatter_data.get("y_values", [])
    regions = scatter_data.get("regions", [])
    ind_a = scatter_data.get("indicator_a", "Indicator A")
    ind_b = scatter_data.get("indicator_b", "Indicator B")
    unit_a = scatter_data.get("unit_a", "")
    unit_b = scatter_data.get("unit_b", "")

    if not x or not y:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for scatter plot.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color=THEME["text_secondary"]),
        )
        return _apply_theme(fig)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        marker=dict(
            color=THEME["accent_teal"],
            size=9,
            line=dict(width=1, color=THEME["paper_bg"]),
        ),
        text=regions,
        textposition="top center",
        textfont=dict(size=8, color=THEME["text_secondary"]),
        hovertemplate=(
            "<b>%{text}</b><br>"
            f"{ind_a}: %{{x:,.2f}} {unit_a}<br>"
            f"{ind_b}: %{{y:,.2f}} {unit_b}<br>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(
            text=f"{ind_a.replace('_', ' ').title()} vs {ind_b.replace('_', ' ').title()}",
            font=dict(size=15),
        ),
        xaxis_title=f"{ind_a.replace('_', ' ').title()} ({unit_a})",
        yaxis_title=f"{ind_b.replace('_', ' ').title()} ({unit_b})",
        height=500,
    )

    return _apply_theme(fig)


def build_coverage_heatmap(
    coverage_matrix: "pd.DataFrame",
    title: str = "Data Coverage — Regions × Indicators",
) -> "go.Figure":
    """Heatmap showing observation coverage across regions and indicators.

    Args:
        coverage_matrix: Pivot table (regions x indicators) with observation counts.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    _check_plotly()

    # Short labels
    y_labels = coverage_matrix.index.tolist()
    x_labels = [c.replace("_", " ").title()[:20] for c in coverage_matrix.columns]

    fig = go.Figure(data=go.Heatmap(
        z=coverage_matrix.values,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, "#1c2333"],
            [0.5, THEME["accent_blue"]],
            [1.0, THEME["accent_teal"]],
        ],
        text=[[str(int(v)) for v in row] for row in coverage_matrix.values],
        texttemplate="%{text}",
        textfont=dict(size=9, color=THEME["text"]),
        hovertemplate=(
            "Region: %{y}<br>"
            "Indicator: %{x}<br>"
            "Observations: %{z}<br>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title="Count",
            titlefont=dict(color=THEME["text_secondary"]),
            tickfont=dict(color=THEME["text_secondary"]),
        ),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        height=max(400, len(y_labels) * 22),
        xaxis=dict(tickangle=45),
    )

    return _apply_theme(fig)


def build_kpi_card_html(
    label: str,
    value: str,
    unit: str = "",
    description: str = "",
    comparison: Optional[str] = None,
    status: str = "neutral",
) -> str:
    """Generates HTML for a styled KPI card.

    Args:
        label: The KPI label/title.
        value: The displayed value.
        unit: Unit of measurement.
        description: Brief explanation.
        comparison: Optional comparison text (e.g. "+2.3% vs state avg").
        status: 'positive', 'negative', 'warning', or 'neutral'.

    Returns:
        HTML string for the KPI card.
    """
    status_colors = {
        "positive": THEME["positive"],
        "negative": THEME["negative"],
        "warning": THEME["warning"],
        "neutral": THEME["accent_teal"],
    }
    accent = status_colors.get(status, THEME["accent_teal"])

    comparison_html = ""
    if comparison:
        comparison_html = f'<div style="font-size: 0.78rem; color: {accent}; margin-top: 4px;">{comparison}</div>'

    unit_html = f' <span style="font-size: 0.85rem; color: {THEME["text_secondary"]};">{unit}</span>' if unit else ""

    return f"""
    <div style="
        background: {THEME['card_bg']};
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid {accent};
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        min-height: 100px;
    ">
        <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em;
                    color: {THEME['text_secondary']}; margin-bottom: 6px;">
            {label}
        </div>
        <div style="font-size: 1.6rem; font-weight: 700; color: {THEME['text']};">
            {value}{unit_html}
        </div>
        {comparison_html}
        <div style="font-size: 0.75rem; color: {THEME['text_secondary']}; margin-top: 6px;">
            {description}
        </div>
    </div>
    """


def build_empty_state_html(
    title: str,
    message: str,
    icon: str = "📊",
) -> str:
    """Generates HTML for an empty/unavailable analysis state.

    Args:
        title: Short title.
        message: Explanation of why data/analysis is unavailable.
        icon: Emoji icon.

    Returns:
        HTML string.
    """
    return f"""
    <div style="
        background: {THEME['card_bg']};
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 12px;">{icon}</div>
        <div style="font-size: 1.1rem; font-weight: 600; color: {THEME['text']}; margin-bottom: 8px;">
            {title}
        </div>
        <div style="font-size: 0.88rem; color: {THEME['text_secondary']}; max-width: 400px; line-height: 1.5;">
            {message}
        </div>
    </div>
    """
