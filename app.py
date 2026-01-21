import streamlit as st
import pandas as pd
import utils.ui_components as ui
import utils.data_loader as dl
from utils.ai_engine import AIEngine
import utils.chart_generator as cg
import time

# Page Configuration
st.set_page_config(
    page_title="InsightBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    local_css("assets/style.css")
except FileNotFoundError:
    pass # CSS might be handled by index.html in dev

# Session State Initialization
if 'data_frame' not in st.session_state:
    st.session_state['data_frame'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'show_executive_summary' not in st.session_state:
    st.session_state['show_executive_summary'] = False

# Sidebar Configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=50)
    st.title("InsightBridge")
    st.markdown("---")
    
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("OpenAI API Key (Optional)", type="password", help="Enter your key for real insights. Leave empty for Demo Mode.")
    
    if api_key:
        st.success("Real AI Enabled ✅")
    else:
        st.info("Using Demo Mode 🟢")
        
    st.markdown("---")
    if st.button("🔄 Reset Demo", use_container_width=True):
        st.session_state['data_frame'] = None
        st.session_state['chat_history'] = []
        st.session_state['show_executive_summary'] = False
        st.rerun()

    st.markdown("---")
    st.markdown("Made with ❤️ by John Parente")

# Main Logic
def main():
    # Initialize AI Engine with Key
    ai_engine = AIEngine(api_key=api_key)

    if st.session_state['data_frame'] is None:
        render_landing_page()
    else:
        render_dashboard_view(ai_engine)

def render_landing_page():
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">InsightBridge AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Turn your clean data into clear direction.<br>Drop a CSV below to start analyzing.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("Upload CSV (Sales, Financials, etc.)", type="csv")
        if uploaded_file is not None:
            with st.spinner("Processing Data..."):
                df = dl.load_csv(uploaded_file)
                if df is not None:
                    st.session_state['data_frame'] = df
                    st.toast("Data Loaded Successfully!", icon="🚀")
                    time.sleep(1)
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard_view(ai_engine):
    st.title("📊 Executive Dashboard")
    
    df = st.session_state['data_frame']
    summary = dl.get_data_summary(df)
    
    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    if summary:
        ui.render_metric_card("Total Rows", summary['rows'])
        ui.render_metric_card("Variables", summary['cols'])
        ui.render_metric_card("Missing Values", summary['missing_values'])
        ui.render_metric_card("Date Range", summary['date_range'])
    
    st.markdown("---")
    
    # Main Workspace
    tab1, tab2 = st.tabs(["💬 Chat & Insights", "📋 Executive Report"])
    
    with tab1:
        col_chat_vis, col_data_prev = st.columns([2, 1])
        
        with col_chat_vis:
            st.markdown("### 🤖 Ask your Data")
            
            # Chat Container
            chat_box = st.container(height=400)
            
            with chat_box:
                if not st.session_state['chat_history']:
                    st.info("👋 Hi! I'm your AI Analyst. Ask me about **trends**, **risks**, or **opportunities**.")
                
                for msg in st.session_state['chat_history']:
                    with st.chat_message(msg['role']):
                        st.markdown(msg['content'])
                        if "chart" in msg and msg["chart"]:
                            st.plotly_chart(msg["chart"], use_container_width=True)

            # Input Action
            query = st.chat_input("Ask a question about your business...")
            
            if query:
                # User Message
                st.session_state['chat_history'].append({"role": "user", "content": query})
                with chat_box:
                    with st.chat_message("user"):
                        st.markdown(query)
                
                # AI Message
                with chat_box:
                    with st.chat_message("assistant"):
                        with st.spinner("Analyzing..."):
                            response = ai_engine.analyze(query, df)
                            
                            st.markdown(response['content'])
                            
                            chart_fig = None
                            if response.get('chart_type'):
                                if response['chart_type'] == 'trend':
                                    chart_fig = cg.create_trend_chart(df)
                                elif response['chart_type'] == 'distribution':
                                    chart_fig = cg.create_distribution_chart(df)
                                elif response['chart_type'] == 'bar':
                                    chart_fig = cg.create_bar_chart(df)
                                
                                if chart_fig:
                                    st.plotly_chart(chart_fig, use_container_width=True)
                            
                            # Save history
                            msg_data = {"role": "assistant", "content": response['content']}
                            if chart_fig:
                                msg_data["chart"] = chart_fig
                            st.session_state['chat_history'].append(msg_data)

        with col_data_prev:
            ui.render_dataframe_preview(df)
            st.markdown("### 💡 Suggestions")
            if st.button("📈 Analyze Trends", use_container_width=True):
                # Trigger via simulation logic or just a quick method
                pass # Use chat input flow naturally
            
            if st.button("⚠️ Identify Risks", use_container_width=True):
                pass
            
            if st.button("🎲 Surprise Me", use_container_width=True):
                pass
                
    with tab2:
        if st.button("Generate New Report", type="primary"):
            with st.spinner("Compiling Board Report..."):
                time.sleep(1) # Polish delay
                st.session_state['show_executive_summary'] = True
        
        if st.session_state['show_executive_summary']:
             st.markdown("""
            <div class="metric-card">
                <h2 style="color: #2c3e50; margin-bottom: 0;">🚀 Executive Summary</h2>
                <p style="color: #7f8c8d; font-size: 0.9rem;">Generated Automatically by InsightBridge</p>
                <hr style="margin: 1rem 0;">
                
                <h4 style="color: #0F52BA;">Key Intelligence</h4>
                <ul>
                    <li><strong>Revenue Growth:</strong> +12% YoY driven by Q3 marketing push.</li>
                    <li><strong>Customer Segments:</strong> Mobile users now account for 65% of traffic.</li>
                    <li><strong>Efficiency:</strong> Inventory holding costs reduced by 5% this quarter.</li>
                </ul>
                
                <h4 style="color: #d63031;">Risk Matrix</h4>
                <ul>
                    <li><strong>Churn Alert:</strong> User retention dropped 2% in the last 30 days.</li>
                    <li><strong>Dependency:</strong> 40% of revenue tied to top 2 product lines.</li>
                </ul>
                
                <h4 style="color: #27ae60;">Strategic Roadmap (Recommended)</h4>
                <ul>
                    <li><strong>Immediate:</strong> Launch win-back campaign for at-risk users.</li>
                    <li><strong>Mid-Term:</strong> Optimize mobile checkout flow for higher conversion.</li>
                    <li><strong>Long-Term:</strong> Diversify product catalog to mitigate dependency risk.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
