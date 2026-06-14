"""
InsightBridge AI — Chart Generator
Modern Plotly charts with dark futuristic theme.
"""
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from utils.ui import apply_dark_layout


# ─── Color Palette ────────────────────────────────────────────────────────────
PALETTE = ["#00d4ff", "#7c3aed", "#10b981", "#f59e0b", "#ec4899",
           "#06b6d4", "#8b5cf6", "#f97316", "#14b8a6", "#a855f7"]
GRADIENT_FILL = "rgba(0, 212, 255, 0.08)"


# ─── Time Series ──────────────────────────────────────────────────────────────

def create_time_series(df: pd.DataFrame, date_col: str, value_col: str,
                       title: str = "📈 Trend Over Time") -> go.Figure:
    """Create an enhanced time series chart with optional moving average."""
    try:
        plot_df = df[[date_col, value_col]].copy()
        plot_df[date_col] = pd.to_datetime(plot_df[date_col], errors="coerce")
        plot_df = plot_df.dropna().sort_values(date_col)

        if len(plot_df) < 2:
            return None

        fig = go.Figure()

        # Main line
        fig.add_trace(go.Scatter(
            x=plot_df[date_col], y=plot_df[value_col],
            mode="lines", name=value_col,
            line=dict(color="#00d4ff", width=2),
            fill="tozeroy", fillcolor=GRADIENT_FILL,
        ))

        # Moving average (if enough data points)
        if len(plot_df) >= 14:
            window = max(7, len(plot_df) // 20)
            plot_df["MA"] = plot_df[value_col].rolling(window=window, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=plot_df[date_col], y=plot_df["MA"],
                mode="lines", name=f"{window}-period MA",
                line=dict(color="#7c3aed", width=2, dash="dash"),
            ))

        # Trend direction annotation
        direction = _trend_direction(plot_df[value_col])
        fig.update_layout(title=f"{title} <span style='font-size:13px;color:#94a3b8'>({direction})</span>")
        apply_dark_layout(fig)
        return fig
    except Exception:
        return None


def create_trend_chart(summary_data: dict, title: str = "📈 Activity Trends") -> go.Figure:
    """Create a trend chart from legacy summary_data format."""
    if not summary_data or not summary_data.get("trend_sorted"):
        return None

    trend_dict = summary_data["trend_sorted"]
    if len(trend_dict) < 2:
        return None

    df = pd.DataFrame(list(trend_dict.items()), columns=["Date", "Records"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    direction = _trend_direction(df["Records"])
    fig = px.area(df, x="Date", y="Records",
                  title=f"{title} <span style='font-size:13px;color:#94a3b8'>({direction})</span>")
    fig.update_traces(line_color="#00d4ff", fillcolor=GRADIENT_FILL)
    apply_dark_layout(fig)
    return fig


# ─── Correlation Heatmap ──────────────────────────────────────────────────────

def create_correlation_heatmap(df: pd.DataFrame,
                               title: str = "🔥 Correlation Matrix") -> go.Figure:
    """Create a correlation heatmap for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return None

    # Limit to 12 columns for readability
    cols = numeric_df.columns[:12].tolist()
    corr = numeric_df[cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[
            [0.0, "#1e1b4b"],
            [0.25, "#312e81"],
            [0.5, "#111638"],
            [0.75, "#0e4c7c"],
            [1.0, "#00d4ff"],
        ],
        zmin=-1, zmax=1,
        text=corr.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>",
    ))

    fig.update_layout(title=title, height=500)
    apply_dark_layout(fig)
    return fig


# ─── Distribution Chart ──────────────────────────────────────────────────────

def create_distribution_chart(df: pd.DataFrame, column: str,
                               title: str = "") -> go.Figure:
    """Create a histogram with KDE-style overlay for a numeric column."""
    if column not in df.columns:
        return None

    clean = df[column].dropna()
    if clean.empty:
        return None

    display_title = title or f"📊 Distribution: {column}"
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=clean, nbinsx=50,
        marker_color="#00d4ff", opacity=0.7,
        name="Frequency",
    ))

    # Add mean + median vertical lines
    mean_val = clean.mean()
    median_val = clean.median()

    fig.add_vline(x=mean_val, line_dash="dash", line_color="#f59e0b",
                  annotation_text=f"Mean: {mean_val:.2f}", annotation_font_color="#f59e0b")
    fig.add_vline(x=median_val, line_dash="dot", line_color="#10b981",
                  annotation_text=f"Median: {median_val:.2f}", annotation_font_color="#10b981")

    fig.update_layout(title=display_title, xaxis_title=column, yaxis_title="Frequency")
    apply_dark_layout(fig)
    return fig


# ─── Box Plot ─────────────────────────────────────────────────────────────────

def create_box_plot(df: pd.DataFrame, columns: list,
                    title: str = "📦 Outlier Detection") -> go.Figure:
    """Create box plots for multiple numeric columns."""
    valid_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not valid_cols:
        return None

    fig = go.Figure()
    for i, col in enumerate(valid_cols[:6]):
        fig.add_trace(go.Box(
            y=df[col].dropna(), name=col,
            marker_color=PALETTE[i % len(PALETTE)],
            boxmean="sd",
        ))

    fig.update_layout(title=title, showlegend=False)
    apply_dark_layout(fig)
    return fig


# ─── Scatter Plot ─────────────────────────────────────────────────────────────

def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str,
                        color_col: str = None,
                        title: str = "") -> go.Figure:
    """Create a scatter plot between two numeric columns."""
    if x_col not in df.columns or y_col not in df.columns:
        return None

    display_title = title or f"🔬 {x_col} vs {y_col}"

    kwargs = {"x": x_col, "y": y_col, "title": display_title, "opacity": 0.7}
    if color_col and color_col in df.columns:
        kwargs["color"] = color_col
        kwargs["color_discrete_sequence"] = PALETTE

    fig = px.scatter(df, **kwargs)
    if not color_col:
        fig.update_traces(marker_color="#00d4ff")

    apply_dark_layout(fig)
    return fig


# ─── Categorical Bar Chart ───────────────────────────────────────────────────

def create_categorical_chart(summary_data: dict = None, df: pd.DataFrame = None,
                              column: str = None,
                              title: str = "📊 Category Breakdown") -> go.Figure:
    """Create a horizontal bar chart for categorical data."""
    if df is not None and column and column in df.columns:
        vc = df[column].value_counts().head(15)
        bar_df = pd.DataFrame({"Category": vc.index.astype(str), "Count": vc.values})
    elif summary_data and summary_data.get("categorical_stats"):
        cat_stats = summary_data["categorical_stats"]
        best_col = max(cat_stats, key=lambda c: sum(cat_stats[c].values()), default=None)
        if not best_col:
            return None
        top_items = cat_stats[best_col].most_common(15)
        bar_df = pd.DataFrame(top_items, columns=["Category", "Count"])
        title = f"{title}: {best_col}"
    else:
        return None

    fig = px.bar(bar_df, x="Count", y="Category", orientation="h",
                 text="Count", title=title, color_discrete_sequence=["#10b981"])
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    apply_dark_layout(fig)
    return fig


# ─── Pie / Donut Chart ───────────────────────────────────────────────────────

def create_pie_chart(df: pd.DataFrame, column: str,
                     title: str = "") -> go.Figure:
    """Create a donut chart for categorical column composition."""
    if column not in df.columns:
        return None

    vc = df[column].value_counts().head(10)
    display_title = title or f"🍩 Composition: {column}"

    fig = go.Figure(data=[go.Pie(
        labels=vc.index.astype(str), values=vc.values,
        hole=0.5,
        marker=dict(colors=PALETTE[:len(vc)]),
        textinfo="label+percent",
        textfont=dict(size=11, color="#e2e8f0"),
    )])

    fig.update_layout(title=display_title, showlegend=True,
                      legend=dict(font=dict(color="#94a3b8")))
    apply_dark_layout(fig)
    return fig


# ─── Missing Values Chart ────────────────────────────────────────────────────

def create_missing_values_chart(df: pd.DataFrame,
                                 title: str = "🕳️ Missing Values") -> go.Figure:
    """Visualize missing values per column."""
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=True)

    if missing.empty:
        return None

    pct = (missing / len(df) * 100).round(2)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pct.values, y=pct.index.tolist(),
        orientation="h",
        marker_color=["#ef4444" if p > 50 else "#f59e0b" if p > 20 else "#10b981" for p in pct.values],
        text=[f"{p}%" for p in pct.values],
        textposition="outside",
    ))

    fig.update_layout(title=title, xaxis_title="Missing %", yaxis_title="")
    apply_dark_layout(fig)
    return fig


# ─── Utilities ────────────────────────────────────────────────────────────────

def _trend_direction(series: pd.Series) -> str:
    """Simple heuristic to determine trend direction."""
    if len(series) < 5:
        return "Stable"
    x = np.arange(len(series))
    y = series.values.astype(float)
    try:
        z = np.polyfit(x, y, 1)
        slope = z[0]
        if slope > 0.5:
            return "Trending Up ↗"
        elif slope < -0.5:
            return "Trending Down ↘"
        return "Stable →"
    except (np.linalg.LinAlgError, ValueError):
        return "Stable"
