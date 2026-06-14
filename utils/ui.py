"""
InsightBridge AI — UI Components & Styling
Futuristic dark-mode glassmorphism design system.
"""
import streamlit as st


# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
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


def inject_custom_css():
    """Inject the full dark-mode futuristic CSS design system."""
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
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 0.8rem;
            color: #94a3b8;
            margin-bottom: 12px;
        }

        .source-badge a {
            color: #00d4ff;
            text-decoration: none;
        }

        .source-badge a:hover {
            text-decoration: underline;
        }

        /* ─── Empty State ─── */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        .empty-state-text {
            font-size: 1.1rem;
            color: #94a3b8;
            max-width: 400px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* ─── Buttons ─── */
        .stButton button {
            border-radius: 10px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 0.5rem 1.2rem;
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }

        .stButton button:hover {
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15);
            transform: translateY(-1px);
        }

        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
            color: white;
            border: none;
        }

        /* ─── Expanders ─── */
        .streamlit-expanderHeader {
            background: rgba(17, 22, 56, 0.4);
            border: 1px solid rgba(0, 212, 255, 0.1);
            border-radius: 10px;
            font-weight: 600;
        }

        /* ─── DataFrames ─── */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }

        /* ─── File Uploader ─── */
        .stFileUploader {
            border-radius: 12px;
        }

        /* ─── Progress bars ─── */
        .stProgress > div > div {
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            border-radius: 10px;
        }

        /* ─── Tabs ─── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 20px;
            font-weight: 500;
        }

        /* ─── Divider ─── */
        hr {
            border-color: rgba(0, 212, 255, 0.08);
        }

        /* ─── Selectbox / inputs ─── */
        .stSelectbox, .stMultiSelect, .stTextInput, .stNumberInput {
            border-radius: 10px;
        }

        /* ─── Scrollbar ─── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(17, 22, 56, 0.3);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 212, 255, 0.2);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 212, 255, 0.4);
        }

        /* ─── Hero gradient text ─── */
        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 1.15rem;
            color: #94a3b8;
            font-weight: 400;
            line-height: 1.6;
            max-width: 600px;
        }

        /* ─── Animations ─── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
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


def metric_card(title: str, value: str, description: str = "", icon: str = ""):
    """Render a glassmorphic metric card."""
    icon_html = f'<span style="margin-right: 6px;">{icon}</span>' if icon else ""
    desc_html = f'<div class="metric-delta">{description}</div>' if description else ""
    st.markdown(f"""
    <div class="metric-card animate-in">
        <div class="metric-label">{icon_html}{title}</div>
        <div class="metric-value">{value}</div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    """Render a consistent section header with gradient text."""
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="section-header animate-in">
        <h2>{title}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def glass_card(content_html: str):
    """Render content inside a glassmorphic card."""
    st.markdown(f"""
    <div class="glass-card animate-in">
        {content_html}
    </div>
    """, unsafe_allow_html=True)


def source_attribution(name: str, url: str):
    """Render a source attribution badge with link."""
    st.markdown(f"""
    <div class="source-badge">
        📡 Source: <a href="{url}" target="_blank">{name}</a>
    </div>
    """, unsafe_allow_html=True)


def empty_state(message: str, icon: str = "📭"):
    """Render a beautiful empty state placeholder."""
    st.markdown(f"""
    <div class="empty-state animate-in">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def hero_header(title: str, subtitle: str):
    """Render the main hero header with gradient text."""
    st.markdown(f"""
    <div class="animate-in" style="margin-bottom: 32px;">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Plotly Dark Theme Config ──────────────────────────────────────────────────
PLOTLY_DARK_TEMPLATE = {
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


def apply_dark_layout(fig):
    """Apply the dark futuristic layout to any Plotly figure."""
    fig.update_layout(**PLOTLY_DARK_TEMPLATE)
    return fig
