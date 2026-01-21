import streamlit as st
import pandas as pd
import utils.ui_components as ui
import utils.data_loader as dl
import utils.ai_engine as ai
import utils.chart_generator as cg
import time

# Page Configuration
st.set_page_config(
    page_title="InsightBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    local_css("assets/style.css")
except FileNotFoundError:
    st.warning("Style file not found. Please ensure assets/style.css exists.")

# Session State Initialization
if 'data_frame' not in st.session_state:
    st.session_state['data_frame'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Main App Layout
def main():
    if st.session_state['data_frame'] is None:
        render_landing_page()
    else:
        render_dashboard_view()

def render_landing_page():
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">InsightBridge AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Upload your data. Ask real business questions.<br>No dashboards. No SQL. Just insights.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("Upload your CSV to get started", type="csv")
        if uploaded_file is not None:
            with st.spinner("Analyzing your data..."):
                df = dl.load_csv(uploaded_file)
                if df is not None:
                    st.session_state['data_frame'] = df
                    st.success("Data successfully loaded!")
                    st.experimental_rerun()

def render_dashboard_view():
    st.title("InsightBridge Dashboard")
    
    # Dashboard Header: Data Summary
    df = st.session_state['data_frame']
    summary = dl.get_data_summary(df)
    
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ui.render_metric_card("Rows", summary['rows'])
        with col2:
            ui.render_metric_card("Columns", summary['cols'])
        with col3:
            ui.render_metric_card("Missing Values", summary['missing_values'])
        with col4:
            ui.render_metric_card("Date Range", summary['date_range'])
    
    st.markdown("---")
    
    # Split Layout
    left_col, right_col = st.columns([1, 1.5])
    
    with left_col:
        # Data Preview
        ui.render_dataframe_preview(df)
        
        st.write("---")
        
        # Executive Summary Button
        st.markdown("### 📋 Executive Reporting")
        if st.button("Generate Executive Summary", type="primary", use_container_width=True):
            with st.spinner("Preparing board-ready insights..."):
                time.sleep(2) # Demo effect
                st.session_state['show_executive_summary'] = True
        
        if st.session_state.get('show_executive_summary'):
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-top: 20px;">
                <h2 style="color: #2c3e50; margin-bottom: 0;">🚀 Executive Summary</h2>
                <p style="color: #7f8c8d; font-size: 0.9rem;">Generated on: Jan 21, 2026</p>
                <hr>
                
                <h4 style="color: #0F52BA;">Top 3 Insights</h4>
                <ul>
                    <li><strong>Revenue Growth:</strong> +12% YoY driven by Q3 marketing push.</li>
                    <li><strong>Customer Segments:</strong> Mobile users now account for 65% of traffic.</li>
                    <li><strong>Efficiency:</strong> Inventory holding costs reduced by 5% this quarter.</li>
                </ul>
                
                <h4 style="color: #d63031;">Critical Risks</h4>
                <ul>
                    <li><strong>Churn Alert:</strong> User retention dropped 2% in the last 30 days.</li>
                    <li><strong>Dependency:</strong> 40% of revenue tied to top 2 product lines.</li>
                </ul>
                
                <h4 style="color: #27ae60;">Recommended Actions (30-60-90)</h4>
                <ul>
                    <li><strong>30 Days:</strong> Launch win-back campaign for at-risk users.</li>
                    <li><strong>60 Days:</strong> optimize mobile checkout flow for higher conversion.</li>
                    <li><strong>90 Days:</strong> Diversify product catalog to mitigate dependency risk.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
    with right_col:
        st.markdown("### 💬 Talk to your Data")
        
        # Chat History Container
        chat_container = st.container()
        
        # Input Area
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Ask a question about your business...", placeholder="e.g., What are the top risks?")
            submit_button = st.form_submit_button("Send")
        
        # Preset Questions
        st.markdown("<div style='font-size: 0.8rem; color: #666; margin-bottom: 0.5rem;'>Or try these:</div>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("📈 Trends?", use_container_width=True):
                user_input = "What trends stand out?"
                submit_button = True
        with col_p2:
            if st.button("⚠️ Risks?", use_container_width=True):
                user_input = "What should I worry about?"
                submit_button = True
        with col_p3:
            if st.button("🎲 Surprise Me", use_container_width=True):
                import random
                options = [
                    "Where are we growing fastest?",
                    "What is the biggest risk right now?",
                    "Analyze the latest trends.",
                    "What actions should we take?"
                ]
                user_input = random.choice(options)
                submit_button = True
                
        # Handle Submission
        if submit_button and user_input:
            # Add user message to state
            st.session_state['chat_history'].append({"role": "user", "content": user_input})
            
            # Generate Response
            with st.spinner("Analyzing data..."):
                response = ai.generate_insight(user_input, df)
                
                # Generate Chart if requested
                chart_fig = None
                if response.get('chart_type'):
                    if response['chart_type'] == 'trend':
                        chart_fig = cg.create_trend_chart(df)
                    elif response['chart_type'] == 'distribution':
                        chart_fig = cg.create_distribution_chart(df)
                    elif response['chart_type'] == 'bar':
                        chart_fig = cg.create_bar_chart(df)
                
                message_data = {"role": "ai", "content": response['content']}
                if chart_fig:
                    message_data["chart"] = chart_fig
                
                st.session_state['chat_history'].append(message_data)
        
        # Display History
        with chat_container:
            for msg in st.session_state['chat_history']:
                ui.render_chat_message(msg['role'], msg['content'])
                if "chart" in msg and msg["chart"]:
                    st.plotly_chart(msg["chart"], use_container_width=True)
        
    if st.sidebar.button("Reset Demo"):
        st.session_state['data_frame'] = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()
