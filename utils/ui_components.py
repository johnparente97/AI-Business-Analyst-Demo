import streamlit as st

def render_metric_card(label, value, help_text=None):
    """
    Renders a styled metric card.
    """
    st.markdown(f"""
    <div class="stCard" style="padding: 1rem; text-align: center;">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div style="font-size: 0.8rem; color: #888;">{help_text}</div>' if help_text else ''}
    </div>
    """, unsafe_allow_html=True)

def render_chat_message(role, content):
    """
    Renders a chat message with appropriate styling.
    """
    if role == "user":
        st.markdown(f'<div class="chat-bubble-user">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{content}</div>', unsafe_allow_html=True)

def render_dataframe_preview(df):
    """
    Renders a clean preview of the dataframe.
    """
    st.markdown("### Data Preview")
    st.dataframe(df.head(), use_container_width=True)

