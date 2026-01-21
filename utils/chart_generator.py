import plotly.express as px
import pandas as pd
import streamlit as st

def create_trend_chart(df, date_col=None, value_col=None, title="Trend Analysis"):
    """
    Creates a line chart showing trends over time.
    """
    if df is None:
        return None
        
    # Auto-detect columns if not provided
    if not date_col or not value_col:
        date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c]) or 'date' in c.lower()]
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        
        if date_cols and num_cols:
            date_col = date_cols[0]
            value_col = num_cols[0]
        else:
            return None # Cannot generate chart without proper data

    # Ensure date is sorted
    df = df.sort_values(by=date_col)
    
    fig = px.line(df, x=date_col, y=value_col, title=title, markers=True)
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    return fig

def create_distribution_chart(df, col=None, title="Distribution"):
    """
    Creates a histogram for distribution analysis.
    """
    if df is None:
        return None
        
    if not col:
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if num_cols:
            col = num_cols[0]
        else:
            return None

    fig = px.histogram(df, x=col, title=title, nbins=20)
    fig.update_layout(template="plotly_white")
    return fig

def create_bar_chart(df, cat_col=None, val_col=None, title="Comparison"):
    """
    Creates a bar chart for categorical comparison.
    """
    # Simple heuristic to find categorical and numerical columns
    if not cat_col or not val_col:
        cat_cols = [c for c in df.columns if df[c].dtype == 'object']
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        
        if cat_cols and num_cols:
            cat_col = cat_cols[0]
            # Aggregate if too many unique values
            if df[cat_col].nunique() > 10:
                top_n = df[cat_col].value_counts().nlargest(10).index
                df = df[df[cat_col].isin(top_n)]
            
            val_col = num_cols[0]
        else:
            return None

    # Group by to ensure unique bars
    chart_df = df.groupby(cat_col)[val_col].sum().reset_index().sort_values(by=val_col, ascending=False)

    fig = px.bar(chart_df, x=cat_col, y=val_col, title=title)
    fig.update_layout(template="plotly_white")
    return fig
