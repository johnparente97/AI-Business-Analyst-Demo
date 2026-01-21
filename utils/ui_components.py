import streamlit as st

def render_metric_card(label, value, help_text=None, delta=None):
    """
    Renders a styled metric card using Streamlit native metric for better mobile support,
    wrapped in a custom container class.
    """
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label=label, value=value, delta=delta, help=help_text)
        st.markdown('</div>', unsafe_allow_html=True)

def render_dataframe_preview(df):
    """
    Renders a clean preview of the dataframe in an expander.
    """
    with st.expander("📊 Data Preview & Statistics", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Showing first 10 rows of {len(df)} total entries.")

