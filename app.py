import streamlit as st
import pandas as pd
import utils.data_loader as dl
import utils.chart_generator as cg
from utils.ai_engine import AIEngine

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
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    
    /* Card Styling */
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Dark mode adjustment for cards */
    @media (prefers-color-scheme: dark) {
        .stMetric {
            background-color: #262730;
            box-shadow: 0 2px 5px rgba(255,255,255,0.05);
        }
    }
    
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .stAlert {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

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
    
    st.markdown("### Executive Business Analytics")
    st.markdown("Upload large datasets (up to 200MB) for instant processing, aggregation, and AI-driven strategic insights.")
    st.markdown("---")

    # File Upload
    uploaded_file = st.file_uploader("📂 Upload CSV Data", type=["csv"], help="Optimized for files up to 200MB")
    
    if uploaded_file is None:
        render_landing_info()
    else:
        # File Size Check
        uploaded_file.seek(0, 2)
        size_mb = uploaded_file.tell() / (1024 * 1024)
        uploaded_file.seek(0)
        
        if size_mb > 200:
            st.warning(f"⚠️ File size ({size_mb:.1f}MB) exceeds recommended simple analysis limit (200MB). Performance may vary.")
        
        # Process Stream
        if 'summary_data' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
            with st.spinner("Processing Dataset..."):
                summary = dl.process_uploaded_file(uploaded_file)
                st.session_state['summary_data'] = summary
                st.session_state['file_name'] = uploaded_file.name
        
        if st.session_state.get('summary_data'):
            render_dashboard(st.session_state['summary_data'])

def render_landing_info():
    st.info("👋 **Welcome!** Drag and drop a CSV file above to begin. No API keys or setup required.")
    
    st.markdown("""
    #### Capabilities:
    *   **Large File Support**: Efficiently processes up to 200MB CSVs using server-side streaming.
    *   **Secure & Private**: Raw data is **never** sent to AI models; only anonymous statistical summaries are analyzed.
    *   **Instant Aggregation**: Automatic calculation of trends, distributions, and data quality metrics.
    """)

def render_dashboard(summary):
    # 1. Top Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    if summary:
        m1.metric("Total Records", f"{summary['rows']:,}")
        m2.metric("Variables", summary['cols'])
        m3.metric("Missing Values", f"{summary['total_missing']:,}")
        m4.metric("Date Period", summary['date_range'])
    
    st.markdown("---")
    
    # 2. Visualizations (Auto-Generated)
    c1, c2 = st.columns(2)
    
    with c1:
        # Trend Chart
        fig_trend = cg.create_trend_chart(summary, title="📈 Activity Trends")
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No time-series data detected for trend analysis.")

    with c2:
        # Categorical Breakdown
        fig_cat = cg.create_categorical_chart(summary, title="📊 Primary Category Distribution")
        
        if fig_cat:
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Could not detect significant categorical distributions.")

    st.markdown("---")

    # 3. AI Executive Summary
    st.header("📝 Executive Strategic Analysis")
    
    # Initialize engine
    ai = AIEngine()
    
    # Generate content
    analysis_container = st.container()
    
    with analysis_container:
        with st.spinner("🤖 synthesizing strategic insights (this may take a moment)..."):
            try:
                # Pass summary statistics to AI
                obs = ai.generate_executive_summary(summary)
                st.markdown(obs)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()
