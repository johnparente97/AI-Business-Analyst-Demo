"""
InsightBridge AI — UI Components & Styling
Futuristic dark-mode glassmorphism design system for Streamlit.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import plotly.graph_objects as go
import streamlit as st


# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS: Dict[str, str] = {
    "bg_primary": "#0a0e27",
    "bg_secondary": "#111638",
    "bg_card": "rgba(17, 22, 56, 0.7)",
    "bg_glass": "rgba(17, 22, 56, 0.5)",
    "border": "rgba(0, 212, 255, 0.15)",
    "border_hover": "rgba(0, 212, 255, 0.4)",
    "primary": "#00d4ff",
    "secondary": "#7c3aed",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "text": "#e2e8f0",
    "text_muted": "#94a3b8",
    "gradient_1": "linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)",
    "gradient_2": "linear-gradient(135deg, #7c3aed 0%, #ec4899 100%)",
    "gradient_3": "linear-gradient(135deg, #10b981 0%, #00d4ff 100%)",
}


def inject_custom_css() -> None:
    """Inject the full dark-mode futuristic CSS design system into the Streamlit app."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ─── Base Reset ─── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #e2e8f0;
        }

        h1, h2, h3, h4 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        /* ─── Subtle Background Grid ─── */
        .stApp {
            background:
                radial-gradient(ellipse at 20% 50%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(0, 212, 255, 0.06) 0%, transparent 50%),
                linear-gradient(180deg, #0a0e27 0%, #0d1135 50%, #0a0e27 100%);
        }

        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
            z-index: 0;
        }

        /* ─── Sidebar ─── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1135 0%, #111638 100%);
            border-right: 1px solid rgba(0, 212, 255, 0.1);
        }

        section[data-testid="stSidebar"] .stRadio label {
            font-size: 0.95rem;
            padding: 6px 0;
            transition: color 0.2s ease;
        }

        section[data-testid="stSidebar"] .stRadio label:hover {
            color: #00d4ff;
        }

        /* ─── Container ─── */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        /* ─── Glassmorphic Cards ─── */
        .glass-card {
            background: rgba(17, 22, 56, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 212, 255, 0.12);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
        }

        .glass-card:hover {
            border-color: rgba(0, 212, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.08);
            transform: translateY(-2px);
        }

        /* ─── Metric Cards ─── */
        .metric-card {
            background: rgba(17, 22, 56, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 212, 255, 0.12);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .metric-card:hover::before {
            opacity: 1;
        }

        .metric-card:hover {
            border-color: rgba(0, 212, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }

        .metric-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }

        .metric-delta {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 6px;
            line-height: 1.4;
        }

        /* ─── Section Headers ─── */
        .section-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.1);
        }

        .section-header h2 {
            font-size: 1.6rem;
            margin: 0;
            background: linear-gradient(135deg, #e2e8f0, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .section-subtitle {
            font-size: 0.9rem;
            color: #94a3b8;
            margin-top: 4px;
        }

        /* ─── Source Attribution Badge ─── */
        .source-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(0, 212, 255, 0.08);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 0.75rem;
            color: #00d4ff;
            font-weight: 500;
            margin-bottom: 16px;
        }

        .source-badge a {
            color: #00d4ff;
            text-decoration: underline;
        }

        /* ─── Buttons ─── */
        .stButton > button {
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            color: #0a0e27;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            border: none;
            border-radius: 10px;
            padding: 8px 24px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px rgba(0, 212, 255, 0.25);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
            color: #0a0e27;
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        /* ─── Tabs ─── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(17, 22, 56, 0.4);
            border-radius: 12px;
            padding: 4px;
            border: 1px solid rgba(0, 212, 255, 0.08);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 500;
            padding: 8px 16px;
            transition: all 0.2s ease;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(124, 58, 237, 0.15)) !important;
            color: #00d4ff !important;
            border: 1px solid rgba(0, 212, 255, 0.3);
        }

        /* ─── Dataframe ─── */
        .stDataFrame {
            border: 1px solid rgba(0, 212, 255, 0.1);
            border-radius: 12px;
            overflow: hidden;
        }

        /* ─── Hero Section ─── */
        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            background: linear-gradient(135deg, #e2e8f0 0%, #00d4ff 50%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 1.15rem;
            color: #94a3b8;
            max-width: 600px;
            line-height: 1.5;
            margin-bottom: 24px;
        }

        /* ─── Empty State ─── */
        .empty-state {
            text-align: center;
            padding: 48px 24px;
            background: rgba(17, 22, 56, 0.4);
            border: 2px dashed rgba(0, 212, 255, 0.15);
            border-radius: 16px;
            margin: 24px 0;
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 12px;
        }

        .empty-state-text {
            color: #94a3b8;
            font-size: 1rem;
            max-width: 400px;
            margin: 0 auto;
        }

        /* ─── Animations ─── */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-in {
            animation: fadeInUp 0.5s ease-out;
        }

        /* ─── Toast / Alert styling ─── */
        .stAlert {
            border-radius: 12px;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)


def metric_card(title: str, value: str, description: str = "", icon: str = "") -> None:
    """Render a glassmorphic metric card with optional icon and delta text."""
    icon_html = f'<span style="margin-right: 6px;">{icon}</span>' if icon else ""
    desc_html = f'<div class="metric-delta">{description}</div>' if description else ""
    st.markdown(f"""
    <div class="metric-card animate-in">
        <div class="metric-label">{icon_html}{title}</div>
        <div class="metric-value">{value}</div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    """Render a consistent section header with gradient typography."""
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="section-header animate-in">
        <h2>{title}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def glass_card(content_html: str) -> None:
    """Render raw HTML content inside a stylized glassmorphic card container."""
    st.markdown(f"""
    <div class="glass-card animate-in">
        {content_html}
    </div>
    """, unsafe_allow_html=True)


def source_attribution(name: str, url: str) -> None:
    """Render a data source attribution badge with an external hyperlink."""
    st.markdown(f"""
    <div class="source-badge">
        📡 Source: <a href="{url}" target="_blank">{name}</a>
    </div>
    """, unsafe_allow_html=True)


def empty_state(message: str, icon: str = "📭") -> None:
    """Render an empty state placeholder with an icon and guidance message."""
    st.markdown(f"""
    <div class="empty-state animate-in">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def hero_header(title: str, subtitle: str) -> None:
    """Render the primary application hero banner."""
    st.markdown(f"""
    <div class="animate-in" style="margin-bottom: 32px;">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Plotly Dark Theme Config ──────────────────────────────────────────────────
PLOTLY_DARK_TEMPLATE: Dict[str, Any] = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "size": 12, "color": "#94a3b8"},
    "title_font": {"size": 16, "family": "Outfit, sans-serif", "color": "#e2e8f0"},
    "xaxis": {"showgrid": True, "gridcolor": "rgba(0, 212, 255, 0.06)", "zeroline": False},
    "yaxis": {"showgrid": True, "gridcolor": "rgba(0, 212, 255, 0.06)", "zeroline": False},
    "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
    "hovermode": "x unified",
    "colorway": ["#00d4ff", "#7c3aed", "#10b981", "#f59e0b", "#ec4899", "#06b6d4", "#8b5cf6", "#f97316"],
}


def apply_dark_layout(fig: go.Figure) -> go.Figure:
    """
    Apply the standard dark futuristic theme to any Plotly graph object.

    Args:
        fig: Plotly Figure instance.

    Returns:
        go.Figure: Styled Plotly Figure.
    """
    fig.update_layout(**PLOTLY_DARK_TEMPLATE)
    return fig
