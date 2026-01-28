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
        padding-top: 3rem;
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
    st.markdown("Upload your dataset to instantly generate clear summaries, visual trends, and strategic insights.")
    st.markdown("---")

    # File Upload
    uploaded_file = st.file_uploader("📂 Upload CSV Data", type=["csv"], help="Max 200MB")
    
    if uploaded_file is None:
        render_landing_info()
    else:
        with st.spinner("Processing Data..."):
            df = dl.load_csv(uploaded_file)
            
        if df is not None:
            render_dashboard(df)

def render_landing_info():
    st.info("👋 **Welcome!** Drag and drop a CSV file above to begin. No API keys or setup required.")
    
    st.markdown("""
    #### What you get:
    *   **Auto-Diagnostics**: Detects rows, columns, and numeric trends.
    *   **Visual Intelligence**: Automatically generates relevant charts.
    *   **Executive Summary**: AI-powered analysis of your business context.
    """)

def render_dashboard(df):
    # 1. Calculate Stats
    summary = dl.get_data_summary(df)
    
    # 2. Top Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    if summary:
        m1.metric("Rows", f"{summary['rows']:,}")
        m2.metric("Variables", summary['cols'])
        m3.metric("Missing Values", summary['missing_values'])
        m4.metric("Date Range", summary['date_range'])
    
    st.markdown("---")
    
    # 3. Visualizations (Auto-Generated)
    c1, c2 = st.columns(2)
    
    with c1:
        # Trend Chart (if dates exist)
        fig_trend = cg.create_trend_chart(df, title="📈 Key Trends Over Time")
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No date column detected for trend analysis.")

    with c2:
        # Distribution or Comparison
        fig_dist = cg.create_bar_chart(df, title="📊 Category Performance")
        if not fig_dist:
             fig_dist = cg.create_distribution_chart(df, title="🔢 Numeric Distribution")
        
        if fig_dist:
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("Could not auto-detect simple categories or numeric distributions.")

    st.markdown("---")

    # 4. AI Executive Summary
    st.header("📝 Executive Analysis")
    
    # Initialize engine
    ai = AIEngine()
    
    # Generate content
    # We use a container to clearly update after thinking
    analysis_container = st.container()
    
    with analysis_container:
        with st.spinner("🤖 Analyzing business implications..."):
            try:
                # Pass df and summary statistics to AI
                obs = ai.generate_executive_summary(df, summary)
                st.markdown(obs)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()
