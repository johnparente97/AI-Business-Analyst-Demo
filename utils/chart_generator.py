import plotly.express as px
import pandas as pd
import streamlit as st
import numpy as np

# Premium Color Palette
COLOR_PRIMARY = "#5e17eb" # Indigo
COLOR_SECONDARY = "#00d2be" # Teal

def create_trend_chart(summary_data, title="📈 Activity Trends"):
    """
    Creates a line chart showing trends over time using aggregated trend data.
    """
    if not summary_data or not summary_data.get("trend_sorted"):
        return None
        
    trend_dict = summary_data["trend_sorted"]
    
    if len(trend_dict) < 2:
        return None

    df = pd.DataFrame(list(trend_dict.items()), columns=['Date', 'Records'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Intelligent Title
    direction = _calculate_trend_direction(df['Records'])
    full_title = f"{title} <span style='font-size: 14px; color: grey;'>({direction})</span>"
    
    fig = px.area(df, x='Date', y='Records', title=full_title)
    fig.update_traces(line_color=COLOR_PRIMARY, fill_color="rgba(94, 23, 235, 0.1)")
    
    _apply_premium_layout(fig)
    return fig

def create_categorical_chart(summary_data, title="📊 Top Categories"):
    """
    Creates a bar chart for the most prominent categorical column.
    """
    if not summary_data or not summary_data.get("categorical_stats"):
        return None

    # Find interesting col
    best_col = None
    max_count = 0
    cat_stats = summary_data["categorical_stats"]
    
    for col, counter in cat_stats.items():
        total_tracked = sum(counter.values())
        if total_tracked > max_count:
            max_count = total_tracked
            best_col = col

    if not best_col:
        return None
        
    # Get top 10 items
    top_items = cat_stats[best_col].most_common(10)
    df = pd.DataFrame(top_items, columns=[best_col, 'Count'])
    
    # Horizontal bar for better readability
    fig = px.bar(df, x='Count', y=best_col, title=f"{title}: {best_col}", orientation='h', text='Count')
    fig.update_traces(marker_color=COLOR_SECONDARY, textposition='outside')
    
    # Sort bars
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    _apply_premium_layout(fig)
    return fig

def _calculate_trend_direction(series):
    """
    Simple heuristic to determine trend direction.
    """
    if len(series) < 5:
        return "Stable"
    
    # Linear fit
    x = np.arange(len(series))
    y = series.values
    z = np.polyfit(x, y, 1)
    slope = z[0]
    
    if slope > 0.5:
        return "Trending Up ↗"
    elif slope < -0.5:
        return "Trending Down ↘"
    else:
        return "Stable →"

def _apply_premium_layout(fig):
    """
    Applies a clean, modern style to Plotly figures.
    """
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Inter, sans-serif", size=12),
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=18, family="Inter, sans-serif", color="#333"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f2f6", zeroline=False)
    )
