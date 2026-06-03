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

# Premium Modern Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Premium Cards */
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
        transition: transform 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
    }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] {
        background-color: #fafbfc;
        border-right: 1px solid rgba(0,0,0,0.04);
    }

    /* Container Polish */
    .block-container {
        padding-top: 3rem;
        max-width: 1200px;
    }
    
    /* Button Polish */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

def insight_card(title, value, interpretation):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 12px;
            border: 1px solid rgba(0,0,0,0.04);
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        ">
            <span style="font-size: 0.85em; color: #888; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">{title}</span><br>
            <span style="font-size: 1.6em; font-weight: 700; color: #2c3e50;">{value}</span><br>
            <div style="margin-top: 8px; font-size: 0.9em; color: #6c757d; line-height: 1.4;">{interpretation}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------
# 2. Main Logic
# -----------------
def main():
    # Subtle Header
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("## 🌉")
    with col2:
        st.title("InsightBridge AI")
    
    if 'analysis_state' not in st.session_state:
        st.session_state['analysis_state'] = 'landing'

    # Sidebar for Reset
    with st.sidebar:
        st.caption("Control Panel")
        if st.button("New Analysis"):
            for key in ['summary_data', 'file_name', 'ai_context', 'active_deep_dive']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Main Router
    if 'summary_data' not in st.session_state:
        render_onboarding()
    else:
        render_expert_interface()

def render_onboarding():
    st.markdown("### Executive Business Analytics")
    st.markdown("Turning complex data into clear, strategic decisions. Securely.")
    
    st.markdown("---")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### Option 1: Upload Data")
        uploaded_file = st.file_uploader("📂 Drop CSV file", type=["csv"], help="Max 200MB")
        if uploaded_file:
            process_and_load(uploaded_file, uploaded_file.name)
            
    with c2:
        st.markdown("#### Option 2: No Data?")
        st.write("Test the platform instantly with a synthetic retail dataset.")
        if st.button("⚡ Try Sample Data", type="primary"):
            with st.spinner("Generating Synthetic Data..."):
                sample_file = dl.generate_synthetic_csv()
                process_and_load(sample_file, "Sample Retail Data")

def process_and_load(file_buffer, name):
    st.session_state['file_name'] = name
    
    with st.spinner("🔍 Profiling Data Structure..."):
        summary = dl.process_uploaded_file(file_buffer)
        if summary is None:
            st.error("Failed to process the file. Please check the format and try again.")
            return
        st.session_state['summary_data'] = summary
        
    with st.spinner("🧠 Synthesizing Intelligence..."):
         ai = AIEngine()
         context = ai.analyze_dataset_context(summary)
         st.session_state['ai_context'] = context
    
    st.rerun()

def render_expert_interface():
    summary = st.session_state['summary_data']
    context = st.session_state['ai_context']
    
    # --- PHASE 1: Domain Assessment ---
    st.subheader(f"📑 Executive Assessment: {context.get('domain', 'General Purpose')}")
    
    # --- PHASE 2: Executive Synthesis (New) ---
    synthesis = context.get('executive_synthesis', {})
    if synthesis:
        st.markdown(
            """
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 12px; margin-bottom: 25px; border-left: 5px solid #00d2be;">
                <h3 style="margin-top: 0; font-size: 1.2em; color: #2c3e50;">🎙️ Executive Synthesis</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        cA, cB = st.columns(2)
        with cA:
            st.markdown(f"**🧐 Observation**\n\n{synthesis.get('observation', 'Analyzing data structure...')}")
        with cB:
            st.markdown(f"**💡 Strategic Implication**\n\n{synthesis.get('implication', 'Identifying value levers...')}")
        st.markdown("---")

    # --- PHASE 3: Variable Intelligence (New) ---
    var_intel = context.get('variable_intelligence', [])
    if var_intel:
        st.subheader("🧬 Variable Anatomy")
        st.caption("Auto-classification of key drivers within your dataset.")
        
        # Format as neat dataframe
        df_intel = pd.DataFrame(var_intel)
        if not df_intel.empty:
            st.dataframe(
                df_intel, 
                column_config={
                    "column": "Variable Name",
                    "role": st.column_config.SelectboxColumn("Detected Role", width="medium"),
                    "description": st.column_config.TextColumn("Analyst Note", width="large")
                },
                hide_index=True,
                use_container_width=True
            )
        st.markdown("---")

    # --- PHASE 4: Strategic Signals ---
    st.subheader("📌 Analyst Observations")
    if summary and context:
        col_a, col_b, col_c = st.columns(3)
        completeness = 100 - (summary['total_missing'] / max(1, summary['rows'] * summary['cols']) * 100)
        
        with col_a:
            insight_card(
                "Data Confidence",
                f"{completeness:.0f}%",
                "High data integrity supports reliable decision making." if completeness > 90 else "Moderate integrity; consider data cleaning."
            )

        with col_b:
            insight_card(
                "Metric Dimensionality",
                f"{summary['cols']} Variables",
                "Wide scope allows for multi-factor correlation." if summary['cols'] > 10 else "Focused dataset for specific KPI tracking."
            )

        with col_c:
            insight_card(
                "Temporal Depth",
                "Detected" if summary['date_range'] != "N/A" else "Static",
                f"Coverage from {summary['date_range']} allows trend identification." if summary['date_range'] != 'N/A' else "Snapshot data suitable for distribution analysis."
            )
            
    st.markdown("---")

    # --- PHASE 4b: Key Signals ---
    key_signals = context.get('key_signals', [])
    if key_signals:
        st.subheader("🔑 Key Signals")
        for signal in key_signals:
            st.markdown(f"- {signal}")
        st.markdown("---")

    # --- PHASE 4c: Data Preview ---
    sample_df = summary.get('sample_data')
    if sample_df is not None and not sample_df.empty:
        with st.expander("👁️ Data Preview (First 5 Rows)", expanded=False):
            st.dataframe(sample_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- PHASE 5: Deep Dives ---
    st.subheader("🧭 Recommended Next Steps")

    st.write(
        "Based on the signals in your data, our expert system recommends exploring these specific areas."
    )
    
    actions = context.get('recommended_actions', [])
    if not actions:
        st.info("No specific actions recommended for this dataset. Try uploading a more detailed file.")
        return
    
    cols = st.columns(len(actions))
    
    for idx, action in enumerate(actions):
        if cols[idx].button(f"🔎 {action}", key=f"btn_{idx}", help="Click to analyze"):
            st.session_state['active_deep_dive'] = action
    
    # Render Active Module
    if 'active_deep_dive' in st.session_state:
        render_deep_dive_module(st.session_state['active_deep_dive'], summary)

def render_deep_dive_module(action_name, summary):
    st.markdown("---")
    st.markdown(f"### Deep Dive: {action_name}")
    
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; border-left: 4px solid #5e17eb; margin-bottom: 20px;">
            <strong>Analyst Context</strong><br>
            Exploring <em>{action_name}</em> helps uncover structural drivers and hidden anomalies that aggregate statistics often miss.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Logic to map action strings to chart types
    action = action_name.lower()
    
    if "trend" in action or "time" in action:
        fig = cg.create_trend_chart(summary)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Insufficient time-series data for this view.")
            
    elif "category" in action or "compare" in action:
        fig = cg.create_categorical_chart(summary)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No clear categorical segments found.")
        
    else:
        # Distribution analysis for numeric columns
        st.info("Displaying statistical distribution overview.")
        numeric_stats = summary.get('numeric_stats', {})
        if numeric_stats:
            # Create a summary comparison chart
            import plotly.graph_objects as go
            cols_list = list(numeric_stats.keys())[:6]  # Limit to 6 columns
            means = [numeric_stats[c].get('mean', 0) for c in cols_list]
            stds = [numeric_stats[c].get('std', 0) for c in cols_list]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Mean', x=cols_list, y=means,
                marker_color='#5e17eb',
                error_y=dict(type='data', array=stds, visible=True, color='#888')
            ))
            fig.update_layout(
                title="Numeric Variable Distribution (Mean ± Std Dev)",
                template="plotly_white",
                font=dict(family="Inter, sans-serif", size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f0f2f6", zeroline=False),
                margin=dict(l=40, r=40, t=60, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.json(summary.get('numeric_stats', {}))

if __name__ == "__main__":
    main()
