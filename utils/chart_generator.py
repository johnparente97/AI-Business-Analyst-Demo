import plotly.express as px
import pandas as pd
import streamlit as st

def create_trend_chart(summary_data, title="📈 Activity Over Time"):
    """
    Creates a line chart showing trends over time using aggregated trend data.
    """
    if not summary_data or not summary_data.get("trend_sorted"):
        return None
        
    trend_dict = summary_data["trend_sorted"]
    
    # specific fix for the issue where only one point exists or data is sparse
    if len(trend_dict) < 2:
        return None

    df = pd.DataFrame(list(trend_dict.items()), columns=['Date', 'Records'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    fig = px.line(df, x='Date', y='Records', title=title, markers=True)
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    return fig

def create_categorical_chart(summary_data, title="📊 Top Categories"):
    """
    Creates a bar chart for the most prominent categorical column.
    """
    if not summary_data or not summary_data.get("categorical_stats"):
        return None

    # Find the categorical column with the most interesting distribution (most entries)
    # Or just pick the first one for now
    best_col = None
    max_count = 0
    
    cat_stats = summary_data["categorical_stats"]
    
    for col, counter in cat_stats.items():
        # Heuristic: Pick column with at least 2 distinct values, but not unique for every row (ID-like)
        # Since we only keep top 50, we can check the sum of counts
        total_tracked = sum(counter.values())
        if total_tracked > max_count:
            max_count = total_tracked
            best_col = col

    if not best_col:
        return None
        
    # Get top 10 items
    top_items = cat_stats[best_col].most_common(10)
    
    df = pd.DataFrame(top_items, columns=[best_col, 'Count'])
    
    fig = px.bar(df, x=best_col, y='Count', title=f"{title}: {best_col}", text='Count')
    fig.update_traces(textposition='outside')
    fig.update_layout(template="plotly_white")
    return fig

def create_numeric_distribution(summary_data, title="🔢 Numeric Ranges"):
    """
    Visualizes Min/Max/Average for numeric columns.
    """
    if not summary_data or not summary_data.get("numeric_stats"):
        return None
        
    # Create a summary DF for plotting
    data = []
    
    # Show max 5 cols to avoid crowding
    num_cols = list(summary_data["numeric_stats"].keys())[:5]
    
    for col in num_cols:
        stats = summary_data["numeric_stats"][col]
        # We can plot the Mean with Error bars for Min/Max? 
        # Or just a bar chart of Averages if scales are similar? 
        # A box plot is impossible without raw data. 
        # Let's do a simple Bar chart of Means, normalized? 
        # Actually min/max/mean is hard to plot on one chart if scales differ wildly (e.g. Age vs Salary).
        # Let's skip mixing columns and just do the FIRST numeric column's stats if we want.
        pass
        
    return None # Skipping numeric viz for now as it's hard to do generically without raw data
