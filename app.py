import streamlit as st
import pandas as pd
import utils.data_loader as dl
import utils.chart_generator as cg
from utils.ai_engine import AIEngine
import time

# -----------------
# 1. Config & Style
# -----------------
st.set_page_config(
    page_title="InsightBridge AI",
    page_icon="🌉",
    layout="wide"
)

# Modern UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Cards */
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .stMetric {
            background-color: #262730;
            box-shadow: 0 1px 3px rgba(255,255,255,0.05);
        }
    }
    
    .stButton button {
        border-radius: 20px;
    }
    .stAlert {
        padding: 0.5rem;
    }
    
    section[data-testid="stSidebar"] {
        background-color: rgba(0,0,0,0.02);
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
</style>
""", unsafe_allow_html=True)

def insight_card(title, value, interpretation):
    st.markdown(
        f"""
        <div style="
            background: rgba(0,0,0,0.03);
            padding: 18px;
            border-radius: 14px;
            margin-bottom: 12px;
        ">
            <strong>{title}</strong><br>
            <span style="font-size: 1.3em;">{value}</span><br>
            <span style="color: #6c757d;">{interpretation}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------
# 2. Main Logic
# -----------------
def main():
    # Header
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.write("## 🌉")
    with col2:
        st.title("InsightBridge AI")
    
    if 'analysis_state' not in st.session_state:
        st.session_state['analysis_state'] = 'upload' # upload, processing, assessed, deep_dive

    uploaded_file = st.file_uploader("📂 Upload Dataset", type=["csv"], help="Max 200MB")
    
    if uploaded_file is None:
        render_landing()
        st.session_state['analysis_state'] = 'upload'
        st.session_state['summary_data'] = None
        st.session_state['ai_context'] = None
    else:
        # Check if new file
        if st.session_state.get('file_name') != uploaded_file.name:
            st.session_state['file_name'] = uploaded_file.name
            st.session_state['analysis_state'] = 'processing'
            
            with st.spinner("🔍 Reading & Profiling Data..."):
                summary = dl.process_uploaded_file(uploaded_file)
                st.session_state['summary_data'] = summary
                
            with st.spinner("🧠 Analyzing Context & Domain..."):
                 ai = AIEngine()
                 context = ai.analyze_dataset_context(summary)
                 st.session_state['ai_context'] = context
            
            st.session_state['analysis_state'] = 'assessed'
            st.rerun()

        # Render Main Interface if processed
        if st.session_state.get('summary_data'):
            render_expert_interface()

def render_landing():
    st.markdown("### Expert Business Analyst")
    st.markdown("Drop a file to receive an instant executive briefing and guided strategic deep-dives.")
    st.info("👋 **Welcome!** Analysis happens locally on the server. No raw data is shared.")

def render_expert_interface():
    summary = st.session_state['summary_data']
    context = st.session_state['ai_context']
    
    # --- PHASE 1: Executive Assessment ---
    st.markdown("---")
    st.subheader(f"📑 Executive Assessment: {context['domain']}")
    
    # --- High-Level Insight Metrics (guarded) ---
    if summary and context:
        st.markdown("### 🧠 What This Data Appears to Represent")

        st.info(
            f"""
            **Expert Interpretation**

            This dataset appears to focus on **{context['domain'].lower()}** information.
            Based on its structure and variables, it is likely intended to **{context['purpose'].lower()}**.

            The strongest signals suggest the data is more suitable for
            **directional insight and decision support** rather than precise prediction.
            """
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Sample Size",
            f"{summary['rows']:,}",
            help="Indicates analytical reliability"
        )

        m2.metric(
            "Variables",
            summary['cols'],
            help="Breadth of measured factors"
        )

        completeness = 100 - (
            summary['total_missing'] /
            max(1, summary['rows'] * summary['cols']) * 100
        )

        m3.metric(
            "Data Quality",
            f"{completeness:.1f}%",
            help="Higher quality improves insight confidence"
        )

        m4.metric(
            "Time Coverage",
            summary['date_range'] or "Not detected",
            help="Enables trend and change analysis"
        )
    
    # Executive Summary Card
    with st.container():
        st.success(f"**Insight:** {context['summary']}")
    
    # Signals
    c1, c2, c3 = st.columns(3)
    for i, signal in enumerate(context['key_signals']):
        col = [c1, c2, c3][i % 3]
        col.info(f"📌 {signal}")

    st.markdown("### 📌 Analyst Observations")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        insight_card(
            "Data Readiness",
            "High" if completeness > 85 else "Moderate",
            "Sufficient quality to support strategic conclusions"
        )

    with col_b:
        insight_card(
            "Analytical Leverage",
            "Strong",
            "Multiple variables allow for comparison and pattern discovery"
        )

    with col_c:
        insight_card(
            "Decision Utility",
            "Exploratory",
            "Best used to understand drivers and tradeoffs, not forecasts"
        )

    st.markdown("---")
    
    # --- PHASE 2: Interactive Deep Dives ---
    st.subheader("� Where an Expert Would Look Next")

    st.write(
        "Based on the structure and signals in your data, these areas are the most valuable to explore next."
    )
    
    # Dynamic Buttons based on recommendations
    actions = context.get('recommended_actions', [])
    cols = st.columns(len(actions))
    
    for idx, action in enumerate(actions):
        if cols[idx].button(f"� {action}", key=f"btn_{idx}"):
            st.session_state['active_deep_dive'] = action
            st.toast("Insight unlocked", icon="✨")
    
    # Render Active Module
    if 'active_deep_dive' in st.session_state:
        render_deep_dive_module(st.session_state['active_deep_dive'], summary)

def render_deep_dive_module(action_name, summary):
    st.markdown("---")
    st.markdown(f"### Deep Dive: {action_name}")
    
    st.info(
        f"""
        **Why this matters**

        Experienced analysts explore **{action_name.lower()}** at this stage to
        uncover structural drivers and hidden relationships that aren’t immediately obvious.
        """
    )
    
    # Logic to map action strings to chart types
    # This is a heuristic mapping based on keywords
    action = action_name.lower()
    
    if "trend" in action or "time" in action:
        st.caption("Visualizing volume and activity over the detected timeline.")
        fig = cg.create_trend_chart(summary)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("> **Strategist Note:** Look for seasonality or sudden drops that correlate with external business events.")
        else:
            st.warning("Insufficient time-series data for this view.")
            
    elif "category" in action or "compare" in action:
        st.caption("Comparing performance across primary segments.")
        fig = cg.create_categorical_chart(summary)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("> **Strategist Note:** Pareto principle often applies—focus resources on the top performing segments.")
        else:
            st.warning("No clear categorical segments found.")
            
    elif "numeric" in action or "distribution" in action:
        st.caption("Analyzing statistical spread of key variables.")
        # Currently we don't have a numeric distribution chart in the new cg, 
        # let's fallback or just show stats
        st.write("**Key Numeric Distributions**")
        stats = summary.get('numeric_stats', {})
        st.dataframe(pd.DataFrame(stats).T)
        st.markdown("> **Strategist Note:** Check the 'min' and 'max' columns for outliers that might skew average performance.")
        
    else:
        st.info("Displaying general statistical overview.")
        st.json(summary['numeric_stats'])

if __name__ == "__main__":
    main()
