"""
InsightBridge AI — Main Application
AI-powered business analytics platform with public data exploration.
"""
import streamlit as st
import pandas as pd
import numpy as np

# ─── Must be the FIRST Streamlit call ─────────────────────────────────────────
st.set_page_config(
    page_title="InsightBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui import (
    inject_custom_css, metric_card, section_header, glass_card,
    empty_state, source_attribution, hero_header, apply_dark_layout,
)
from utils.ai_engine import AIEngine
from utils.data_profile import generate_full_profile
from utils import charts
from utils import reporting
from utils import public_sources
import utils.data_loader as dl


# ─── Session State Initialization ─────────────────────────────────────────────

def init_session():
    """Initialize all session state keys."""
    defaults = {
        "current_page": "🏠 Home",
        "df": None,
        "profile": None,
        "summary_data": None,
        "ai_context": None,
        "dataset_name": None,
        "dataset_metadata": None,
        "deep_dive_results": None,
        "executive_summary_text": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─── Navigation ───────────────────────────────────────────────────────────────

PAGES = [
    "🏠 Home",
    "📤 Upload Data",
    "🌐 Public Data Explorer",
    "📊 Data Profile",
    "📈 Visual Analysis",
    "🤖 AI Deep Dive",
    "📋 Executive Summary",
    "💾 Export / Share",
]


def render_sidebar():
    """Render the sidebar navigation and status indicators."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 8px 0;">
            <span style="font-size: 2rem;">🌉</span><br>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 700;
                   background: linear-gradient(135deg, #00d4ff, #7c3aed);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   background-clip: text;">InsightBridge AI</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio("Navigate", PAGES, label_visibility="collapsed",
                        index=PAGES.index(st.session_state["current_page"]))
        st.session_state["current_page"] = page

        st.markdown("---")

        # Dataset status
        if st.session_state["df"] is not None:
            df = st.session_state["df"]
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2);
                        border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; color: #10b981; text-transform: uppercase;
                            font-weight: 600; letter-spacing: 0.05em;">✅ Data Loaded</div>
                <div style="font-size: 0.9rem; color: #e2e8f0; margin-top: 4px;">
                    {st.session_state.get('dataset_name', 'Dataset')}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">
                    {len(df):,} rows × {len(df.columns)} cols</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(148, 163, 184, 0.08); border: 1px solid rgba(148, 163, 184, 0.1);
                        border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;
                            font-weight: 600;">⬜ No Data Loaded</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                    Upload a file or use the Public Data Explorer</div>
            </div>
            """, unsafe_allow_html=True)

        # AI status
        ai = AIEngine()
        status = ai.get_provider_status()
        st.caption(status["label"])

        st.markdown("---")

        # Reset button
        if st.button("🔄 New Analysis", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != "current_page":
                    st.session_state[key] = None
            st.session_state["current_page"] = "🏠 Home"
            st.rerun()


# ─── Data Loading Helpers ─────────────────────────────────────────────────────

def load_dataframe(df: pd.DataFrame, name: str, metadata: dict = None):
    """Store a DataFrame in session state and generate profile + AI context."""
    st.session_state["df"] = df
    st.session_state["dataset_name"] = name
    st.session_state["dataset_metadata"] = metadata

    # Reset downstream analysis
    st.session_state["deep_dive_results"] = None
    st.session_state["executive_summary_text"] = None

    with st.spinner("🔍 Profiling data structure..."):
        st.session_state["profile"] = generate_full_profile(df)

    # Generate legacy summary for AI context compatibility
    with st.spinner("🧠 Synthesizing intelligence..."):
        summary = _build_legacy_summary(df)
        st.session_state["summary_data"] = summary
        ai = AIEngine()
        st.session_state["ai_context"] = ai.analyze_dataset_context(summary)


def _build_legacy_summary(df: pd.DataFrame) -> dict:
    """Build a summary dict compatible with the legacy AI engine interface."""
    from collections import Counter

    numeric_stats = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        clean = df[col].dropna()
        if not clean.empty:
            numeric_stats[col] = {
                "mean": float(clean.mean()),
                "max": float(clean.max()),
                "min": float(clean.min()),
                "std": float(clean.std()),
                "sum": float(clean.sum()),
                "count": len(clean),
            }

    categorical_stats = {}
    for col in df.select_dtypes(include=["object", "category"]).columns:
        categorical_stats[col] = Counter(df[col].dropna().value_counts().head(20).to_dict())

    # Detect date column
    date_col = None
    date_range = "N/A"
    for col in df.columns:
        if any(kw in col.lower() for kw in ["date", "time", "timestamp"]):
            try:
                dates = pd.to_datetime(df[col], errors="coerce").dropna()
                if len(dates) > 0:
                    date_col = col
                    date_range = f"{dates.min().date()} to {dates.max().date()}"
                    break
            except Exception:
                pass

    return {
        "rows": len(df),
        "cols": len(df.columns),
        "numeric_stats": numeric_stats,
        "categorical_stats": categorical_stats,
        "total_missing": int(df.isnull().sum().sum()),
        "date_col": date_col,
        "date_range": date_range,
        "sample_data": df.head(5),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════════════════════


def page_home():
    """🏠 Home / Overview page."""
    hero_header(
        "InsightBridge AI",
        "Turn complex data into clear, strategic decisions. Upload your data or explore free public datasets — no coding required."
    )

    if st.session_state["df"] is not None:
        # Show overview dashboard
        df = st.session_state["df"]
        profile = st.session_state["profile"]
        context = st.session_state.get("ai_context", {})
        missing = profile.get("missing_summary", {})

        # Synthesis card
        synthesis = context.get("executive_synthesis", {})
        if synthesis:
            glass_card(f"""
                <div style="font-size: 0.78rem; color: #00d4ff; text-transform: uppercase;
                            font-weight: 600; letter-spacing: 0.08em; margin-bottom: 10px;">
                    🎙️ Executive Synthesis — {context.get('domain', 'General')}
                </div>
                <div style="font-size: 1rem; color: #e2e8f0; line-height: 1.6; margin-bottom: 12px;">
                    <strong>Observation:</strong> {synthesis.get('observation', '')}
                </div>
                <div style="font-size: 1rem; color: #e2e8f0; line-height: 1.6;">
                    <strong>Implication:</strong> {synthesis.get('implication', '')}
                </div>
            """)

        # Metric cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Records", f"{len(df):,}", f"{len(df.columns)} variables", "📊")
        with c2:
            metric_card("Completeness", f"{missing.get('completeness_pct', 100)}%",
                        f"{missing.get('total_missing', 0):,} missing values", "✅")
        with c3:
            dups = profile.get("duplicates", {})
            metric_card("Duplicates", f"{dups.get('duplicate_rows', 0):,}",
                        f"{dups.get('duplicate_pct', 0):.1f}% of rows", "🔁")
        with c4:
            dt_cols = profile.get("datetime_columns", [])
            metric_card("Time Dimension",
                        "Detected" if dt_cols else "Static",
                        f"Column: {dt_cols[0]}" if dt_cols else "No temporal data",
                        "📅")

        # Key signals
        signals = context.get("key_signals", [])
        if signals:
            st.markdown("---")
            section_header("🔑 Key Signals")
            for signal in signals:
                st.markdown(f"- {signal}")

        # Variable intelligence
        var_intel = context.get("variable_intelligence", [])
        if var_intel:
            st.markdown("---")
            section_header("🧬 Variable Intelligence", "Auto-classified column roles")
            vi_df = pd.DataFrame(var_intel)
            if not vi_df.empty:
                st.dataframe(vi_df, hide_index=True, use_container_width=True,
                             column_config={
                                 "column": "Variable",
                                 "role": st.column_config.SelectboxColumn("Role", width="medium"),
                                 "description": st.column_config.TextColumn("Note", width="large"),
                             })

        # Source attribution
        meta = st.session_state.get("dataset_metadata")
        if meta:
            st.markdown("---")
            source_attribution(meta.get("source_name", ""), meta.get("source_url", ""))

    else:
        # Landing state
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            glass_card("""
                <div style="text-align:center;">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">📤</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 8px;">Upload Your Data</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">CSV or Excel files up to 200MB. Processed securely in memory.</div>
                </div>
            """)
        with c2:
            glass_card("""
                <div style="text-align:center;">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">🌐</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 8px;">Explore Public Data</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">World Bank, CDC, Census — free datasets with zero setup.</div>
                </div>
            """)
        with c3:
            glass_card("""
                <div style="text-align:center;">
                    <div style="font-size: 2.5rem; margin-bottom: 12px;">🤖</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 8px;">AI-Powered Analysis</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Get executive summaries, trend detection, and strategic insights.</div>
                </div>
            """)

        st.markdown("---")
        st.markdown("#### ⚡ Quick Start: Try Sample Data")
        if st.button("Load Sample Retail Dataset", type="primary"):
            with st.spinner("Generating synthetic data..."):
                sample_buf = dl.generate_synthetic_csv()
                sample_df = pd.read_csv(sample_buf)
                load_dataframe(sample_df, "Sample Retail Data")
                st.rerun()


def page_upload():
    """📤 Upload Data page."""
    section_header("📤 Upload Data", "Import CSV or Excel files for analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Drop your file here",
            type=["csv", "xlsx", "xls"],
            help="Supports CSV and Excel files up to 200MB",
        )

        if uploaded_file:
            with st.spinner("Processing file..."):
                try:
                    if uploaded_file.name.endswith((".xlsx", ".xls")):
                        df = pd.read_excel(uploaded_file)
                    else:
                        df = pd.read_csv(uploaded_file)

                    load_dataframe(df, uploaded_file.name)
                    st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df):,} rows × {len(df.columns)} columns")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to process file: {e}")

    with col2:
        glass_card("""
            <div style="font-size: 0.85rem; color: #94a3b8; line-height: 1.6;">
                <strong style="color: #e2e8f0;">Supported Formats</strong><br>
                • CSV (.csv)<br>
                • Excel (.xlsx, .xls)<br><br>
                <strong style="color: #e2e8f0;">Privacy</strong><br>
                • Files processed in memory only<br>
                • No data is stored or transmitted<br>
                • Only metadata sent to AI (if enabled)
            </div>
        """)

    # Sample data option
    st.markdown("---")
    st.markdown("#### Don't have data? Try our sample dataset")
    if st.button("⚡ Load Sample Retail Data", type="primary"):
        with st.spinner("Generating synthetic data..."):
            sample_buf = dl.generate_synthetic_csv()
            sample_df = pd.read_csv(sample_buf)
            load_dataframe(sample_df, "Sample Retail Data")
            st.rerun()


def page_public_explorer():
    """🌐 Public Data Explorer page."""
    section_header("🌐 Public Data Explorer", "Access free public datasets from trusted sources")

    sources = public_sources.get_available_sources()
    source_names = [s["name"] for s in sources]
    source_map = {s["name"]: s for s in sources}

    # Source picker
    selected_name = st.selectbox("Choose a data source", source_names,
                                 format_func=lambda x: f"{source_map[x]['category']}  •  {x}")
    source = source_map[selected_name]

    if source.get("url"):
        source_attribution(source["name"], source["url"])

    st.markdown(f"*{source['description']}*")

    if source.get("requires_key"):
        st.info("⚠️ This source requires a free API key. Add it to `.streamlit/secrets.toml`.")

    st.markdown("---")

    # ── Source-specific forms ──

    if source["id"] == "world_bank":
        _render_world_bank_form()

    elif source["id"] == "cdc":
        _render_cdc_form()

    elif source["id"] == "census":
        _render_census_form()

    elif source["id"] == "csv_url":
        _render_csv_url_form()

    elif source["id"] == "fred":
        _render_fred_form()


def _render_world_bank_form():
    """World Bank data fetch form."""
    indicators = list(public_sources.WORLD_BANK_INDICATORS.keys())
    regions = list(public_sources.WORLD_BANK_REGIONS.keys())

    c1, c2 = st.columns(2)
    with c1:
        indicator = st.selectbox("Indicator", indicators)
    with c2:
        region = st.selectbox("Country / Region", regions)

    c3, c4 = st.columns(2)
    with c3:
        start_year = st.number_input("Start Year", min_value=1960, max_value=2023, value=2000)
    with c4:
        end_year = st.number_input("End Year", min_value=1960, max_value=2023, value=2023)

    if st.button("🔍 Fetch Data", type="primary"):
        country_code = public_sources.WORLD_BANK_REGIONS[region]
        with st.spinner(f"Fetching {indicator} data..."):
            result = public_sources.fetch_world_bank_data(indicator, country_code, int(start_year), int(end_year))
            _handle_fetch_result(result, f"World Bank — {indicator}")


def _render_cdc_form():
    """CDC dataset fetch form."""
    datasets = list(public_sources.CDC_DATASETS.keys())
    dataset = st.selectbox("Dataset", datasets)
    limit = st.slider("Max Records", 100, 10000, 2000, step=100)

    if st.button("🔍 Fetch Data", type="primary"):
        with st.spinner(f"Fetching CDC data..."):
            result = public_sources.fetch_cdc_data(dataset, limit)
            _handle_fetch_result(result, f"CDC — {dataset}")


def _render_census_form():
    """U.S. Census fetch form."""
    variables = list(public_sources.CENSUS_VARIABLES.keys())
    selected_vars = st.multiselect("Variables", variables, default=variables[:2])
    year = st.number_input("Year (ACS 5-Year)", min_value=2010, max_value=2022, value=2022)

    if not selected_vars:
        st.warning("Select at least one variable.")
        return

    if st.button("🔍 Fetch Data", type="primary"):
        with st.spinner("Fetching Census data..."):
            result = public_sources.fetch_census_data(selected_vars, int(year))
            _handle_fetch_result(result, f"Census ACS {year}")


def _render_csv_url_form():
    """CSV from URL fetch form."""
    url = st.text_input("CSV URL", placeholder="https://example.com/data.csv")

    st.caption("Paste any public URL pointing to a CSV file.")

    if url and st.button("🔍 Fetch Data", type="primary"):
        with st.spinner("Downloading CSV..."):
            result = public_sources.fetch_csv_from_url(url)
            _handle_fetch_result(result, "CSV from URL")


def _render_fred_form():
    """FRED data fetch form."""
    api_key = AIEngine._get_secret("FRED_API_KEY")
    if not api_key:
        st.warning("FRED requires a free API key. Add `FRED_API_KEY` to `.streamlit/secrets.toml` or environment variables.")
        st.markdown("[Get a free FRED API key →](https://fred.stlouisfed.org/docs/api/api_key.html)")
        api_key = st.text_input("Or enter your key here:", type="password")

    if not api_key:
        return

    series_list = list(public_sources.FRED_SERIES.keys())
    series = st.selectbox("Economic Series", series_list)

    if st.button("🔍 Fetch Data", type="primary"):
        with st.spinner(f"Fetching FRED data..."):
            result = public_sources.fetch_fred_data(series, api_key)
            _handle_fetch_result(result, f"FRED — {series}")


def _handle_fetch_result(result: tuple, name: str):
    """Handle the (DataFrame, metadata) or (None, error) result from a fetch."""
    df_result, meta_or_error = result
    if df_result is not None:
        load_dataframe(df_result, name, meta_or_error)
        st.success(f"✅ Loaded **{name}** — {len(df_result):,} rows × {len(df_result.columns)} columns")
        st.rerun()
    else:
        st.error(f"❌ {meta_or_error}")


def page_data_profile():
    """📊 Data Profile page."""
    if st.session_state["df"] is None:
        empty_state("No data loaded yet. Upload a file or use the Public Data Explorer.", "📊")
        return

    section_header("📊 Data Profile", "Automatic data quality and structure analysis")

    df = st.session_state["df"]
    profile = st.session_state["profile"]
    missing = profile.get("missing_summary", {})
    dups = profile.get("duplicates", {})

    # Quality metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Completeness", f"{missing.get('completeness_pct', 100)}%",
                     f"{missing.get('total_missing', 0):,} missing cells", "✅")
    with c2:
        metric_card("Duplicates", f"{dups.get('duplicate_rows', 0):,}",
                     f"{dups.get('duplicate_pct', 0):.1f}% of rows", "🔁")
    with c3:
        num_count = sum(1 for v in profile.get("columns", {}).values() if v.get("type") == "numeric")
        metric_card("Numeric Columns", str(num_count), "Quantitative variables", "🔢")
    with c4:
        cat_count = sum(1 for v in profile.get("columns", {}).values() if v.get("type") == "categorical")
        metric_card("Categorical Columns", str(cat_count), "Qualitative variables", "🏷️")

    st.markdown("---")

    # Data preview
    with st.expander("👁️ Data Preview", expanded=True):
        # Column filter
        cols_to_show = st.multiselect("Filter columns", df.columns.tolist(), default=df.columns.tolist()[:10])
        if cols_to_show:
            st.dataframe(df[cols_to_show].head(100), use_container_width=True, hide_index=True)

        # Search
        search_term = st.text_input("🔍 Search data", placeholder="Type to search across all columns...")
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            results = df[mask]
            st.caption(f"Found {len(results)} matching rows")
            st.dataframe(results.head(100), use_container_width=True, hide_index=True)

    # Missing values visualization
    fig_missing = charts.create_missing_values_chart(df)
    if fig_missing:
        st.markdown("---")
        st.plotly_chart(fig_missing, use_container_width=True)

    # Column profiles
    st.markdown("---")
    section_header("🔬 Column Details")

    for col_name, col_info in profile.get("columns", {}).items():
        col_type = col_info.get("type", "unknown")
        icon = {"numeric": "🔢", "categorical": "🏷️", "datetime": "📅",
                "boolean": "✅", "identifier": "🔑"}.get(col_type, "📊")

        with st.expander(f"{icon} {col_name} — {col_type.capitalize()}"):
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("Missing", f"{col_info.get('missing_pct', 0):.1f}%")
            with mc2:
                st.metric("Unique", f"{col_info.get('unique_count', 0):,}")
            with mc3:
                st.metric("Type", col_type.capitalize())

            stats = col_info.get("stats", {})
            if col_type == "numeric" and stats:
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    st.metric("Mean", f"{stats.get('mean', 0):,.2f}")
                with sc2:
                    st.metric("Median", f"{stats.get('median', 0):,.2f}")
                with sc3:
                    st.metric("Std Dev", f"{stats.get('std', 0):,.2f}")
                with sc4:
                    st.metric("Skewness", f"{stats.get('skew', 0):.2f}")

                outliers = col_info.get("outliers", {})
                if outliers.get("count", 0) > 0:
                    st.warning(f"⚠️ {outliers['count']} outliers detected ({outliers['pct']:.1f}%) outside [{outliers['lower_bound']:.2f}, {outliers['upper_bound']:.2f}]")

            elif col_type == "categorical" and stats:
                top_vals = stats.get("top_values", {})
                if top_vals:
                    top_df = pd.DataFrame(list(top_vals.items()), columns=["Value", "Count"])
                    st.dataframe(top_df, hide_index=True, use_container_width=True)


def page_visual_analysis():
    """📈 Visual Analysis page."""
    if st.session_state["df"] is None:
        empty_state("No data loaded yet. Upload a file or use the Public Data Explorer.", "📈")
        return

    section_header("📈 Visual Analysis", "Interactive charts and data visualization")

    df = st.session_state["df"]
    profile = st.session_state["profile"]

    # Recommended charts
    recs = profile.get("recommended_charts", [])
    if recs:
        st.markdown("#### 💡 Recommended Visualizations")
        tabs = st.tabs([r["title"] for r in recs])

        for tab, rec in zip(tabs, recs):
            with tab:
                st.caption(rec["description"])
                fig = None

                if rec["type"] == "time_series" and len(rec["columns"]) >= 2:
                    fig = charts.create_time_series(df, rec["columns"][0], rec["columns"][1])

                elif rec["type"] == "correlation":
                    fig = charts.create_correlation_heatmap(df)

                elif rec["type"] == "scatter" and len(rec["columns"]) >= 2:
                    fig = charts.create_scatter_plot(df, rec["columns"][0], rec["columns"][1])

                elif rec["type"] == "distribution" and rec["columns"]:
                    fig = charts.create_distribution_chart(df, rec["columns"][0])

                elif rec["type"] == "categorical" and rec["columns"]:
                    fig = charts.create_categorical_chart(df=df, column=rec["columns"][0])

                elif rec["type"] == "pie" and rec["columns"]:
                    fig = charts.create_pie_chart(df, rec["columns"][0])

                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Insufficient data for this visualization.")

    # Custom chart builder
    st.markdown("---")
    section_header("🛠️ Custom Chart Builder")

    chart_type = st.selectbox("Chart Type", ["Distribution", "Box Plot", "Scatter", "Bar Chart", "Donut", "Time Series"])

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    all_cols = df.columns.tolist()

    if chart_type == "Distribution" and numeric_cols:
        col = st.selectbox("Column", numeric_cols, key="dist_col")
        fig = charts.create_distribution_chart(df, col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box Plot" and numeric_cols:
        cols = st.multiselect("Columns", numeric_cols, default=numeric_cols[:3], key="box_cols")
        if cols:
            fig = charts.create_box_plot(df, cols)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter" and len(numeric_cols) >= 2:
        sc1, sc2 = st.columns(2)
        with sc1:
            x = st.selectbox("X Axis", numeric_cols, key="scat_x")
        with sc2:
            y = st.selectbox("Y Axis", numeric_cols, index=min(1, len(numeric_cols) - 1), key="scat_y")
        color = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="scat_color")
        fig = charts.create_scatter_plot(df, x, y, color_col=color if color != "None" else None)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Bar Chart" and cat_cols:
        col = st.selectbox("Column", cat_cols, key="bar_col")
        fig = charts.create_categorical_chart(df=df, column=col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Donut" and cat_cols:
        col = st.selectbox("Column", cat_cols, key="pie_col")
        fig = charts.create_pie_chart(df, col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Time Series":
        dt_cols = profile.get("datetime_columns", [])
        if dt_cols and numeric_cols:
            tc1, tc2 = st.columns(2)
            with tc1:
                date_col = st.selectbox("Date Column", dt_cols, key="ts_date")
            with tc2:
                val_col = st.selectbox("Value Column", numeric_cols, key="ts_val")
            fig = charts.create_time_series(df, date_col, val_col)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date columns detected for time series analysis.")

    else:
        st.info("Select columns to generate the chart.")


def page_ai_deep_dive():
    """🤖 AI Deep Dive page."""
    if st.session_state["df"] is None:
        empty_state("No data loaded yet. Upload a file or use the Public Data Explorer.", "🤖")
        return

    section_header("🤖 AI Deep Dive", "AI-powered analysis of your dataset")

    df = st.session_state["df"]
    profile = st.session_state["profile"]

    # Provider status
    ai = AIEngine()
    status = ai.get_provider_status()
    st.info(f"{status['label']}  •  {status['description']}")

    # Generate analysis
    if st.button("🧠 Run Deep Dive Analysis", type="primary") or st.session_state.get("deep_dive_results"):
        if not st.session_state.get("deep_dive_results"):
            with st.spinner("Analyzing dataset..."):
                results = ai.deep_dive_analysis(df, profile)
                st.session_state["deep_dive_results"] = results

        results = st.session_state["deep_dive_results"]

        # Summary
        st.markdown("### 📝 Summary")
        glass_card(f"<div style='color: #e2e8f0; line-height: 1.7;'>{results.get('summary', '')}</div>")

        # Two-column layout for trends and anomalies
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 📈 Trends & Patterns")
            for trend in results.get("trends", []):
                st.markdown(f"- {trend}")

        with c2:
            st.markdown("### ⚠️ Outliers & Anomalies")
            for anomaly in results.get("outliers_and_anomalies", []):
                st.markdown(f"- {anomaly}")

        st.markdown("---")

        # Business implications
        st.markdown("### 💼 Business Implications")
        for imp in results.get("business_implications", []):
            st.markdown(f"- {imp}")

        # Limitations
        st.markdown("### ⚖️ Limitations")
        for lim in results.get("limitations", []):
            st.markdown(f"- {lim}")

        # Follow-up questions
        st.markdown("### ❓ Follow-Up Questions")
        for q in results.get("follow_up_questions", []):
            st.markdown(f"- {q}")

        # Recommended sources
        recs = results.get("recommended_data_sources", [])
        if recs:
            st.markdown("### 📚 Recommended Additional Data Sources")
            for src in recs:
                st.markdown(f"- {src}")

    # Custom question
    st.markdown("---")
    question = st.text_area("🔎 Ask a specific question about the data",
                            placeholder="E.g., 'What could explain the outliers in the Sales column?'")
    if question and st.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = ai.deep_dive_analysis(df, profile, question)
            st.markdown("### 💬 Response")
            glass_card(f"<div style='color: #e2e8f0; line-height: 1.7;'>{answer.get('summary', '')}</div>")
            for imp in answer.get("business_implications", []):
                st.markdown(f"- {imp}")


def page_executive_summary():
    """📋 Executive Summary page."""
    if st.session_state["df"] is None:
        empty_state("No data loaded yet. Upload a file or use the Public Data Explorer.", "📋")
        return

    section_header("📋 Executive Summary", "Comprehensive analysis report")

    df = st.session_state["df"]
    profile = st.session_state["profile"]

    if st.button("📝 Generate Executive Summary", type="primary") or st.session_state.get("executive_summary_text"):
        if not st.session_state.get("executive_summary_text"):
            with st.spinner("Generating executive summary..."):
                ai = AIEngine()
                summary_text = ai.generate_executive_summary(df, profile)
                st.session_state["executive_summary_text"] = summary_text

        summary_text = st.session_state["executive_summary_text"]
        st.markdown(summary_text)

        # Download button
        st.markdown("---")
        md_bytes = reporting.export_summary_as_markdown(
            summary_text, st.session_state.get("dataset_name", "Dataset")
        )
        st.download_button(
            "📥 Download Executive Summary (.md)",
            data=md_bytes,
            file_name=f"insightbridge_executive_summary.md",
            mime="text/markdown",
        )


def page_export():
    """💾 Export / Share page."""
    if st.session_state["df"] is None:
        empty_state("No data loaded yet. Upload a file or use the Public Data Explorer.", "💾")
        return

    section_header("💾 Export / Share", "Download your data and analysis reports")

    df = st.session_state["df"]
    profile = st.session_state["profile"]
    name = st.session_state.get("dataset_name", "Dataset")

    st.markdown("### 📂 Data Export")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Cleaned CSV")
        drop_dups = st.checkbox("Remove duplicate rows", value=True)
        selected_cols = st.multiselect("Select columns to export",
                                       df.columns.tolist(),
                                       default=df.columns.tolist(),
                                       key="export_cols")

        csv_bytes = reporting.export_cleaned_csv(df, drop_duplicates=drop_dups,
                                                  selected_columns=selected_cols)
        st.download_button(
            "📥 Download CSV",
            data=csv_bytes,
            file_name=f"insightbridge_export.csv",
            mime="text/csv",
        )

    with c2:
        st.markdown("#### Data Profile Report")
        profile_bytes = reporting.export_profile_report(profile, name)
        st.download_button(
            "📥 Download Profile Report (.md)",
            data=profile_bytes,
            file_name=f"insightbridge_profile_report.md",
            mime="text/markdown",
        )

    # Executive summary export
    st.markdown("---")
    st.markdown("### 📋 Executive Summary Export")
    if st.session_state.get("executive_summary_text"):
        md_bytes = reporting.export_summary_as_markdown(
            st.session_state["executive_summary_text"], name
        )
        st.download_button(
            "📥 Download Executive Summary (.md)",
            data=md_bytes,
            file_name=f"insightbridge_executive_summary.md",
            mime="text/markdown",
            key="export_exec_summary",
        )
    else:
        st.info("Generate an Executive Summary first (from the 📋 Executive Summary page).")

    # Source metadata
    meta = st.session_state.get("dataset_metadata")
    if meta:
        st.markdown("---")
        st.markdown("### 📡 Source Metadata")
        st.json(meta)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    init_session()
    inject_custom_css()
    render_sidebar()

    # Page router
    page = st.session_state["current_page"]
    {
        "🏠 Home": page_home,
        "📤 Upload Data": page_upload,
        "🌐 Public Data Explorer": page_public_explorer,
        "📊 Data Profile": page_data_profile,
        "📈 Visual Analysis": page_visual_analysis,
        "🤖 AI Deep Dive": page_ai_deep_dive,
        "📋 Executive Summary": page_executive_summary,
        "💾 Export / Share": page_export,
    }[page]()


if __name__ == "__main__":
    main()
