import pandas as pd
import streamlit as st
import io

@st.cache_data
def load_csv(uploaded_file):
    """
    Loads CSV and returns a pandas DataFrame.
    """
    try:
        # Check if it's an uploaded file (has seek) or string
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
            
        df = pd.read_csv(uploaded_file)
        
        # Basic cleanup: Standardize headers
        df.columns = [c.strip() for c in df.columns]
        
        # Optimization: Downcast floats/ints if possible (optional, good for huge files)
        # For now, just ensuring it's efficient
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def get_data_summary(df):
    """
    Returns a dictionary with dataset metadata.
    """
    if df is None:
        return None
        
    summary = {
        "rows": len(df),
        "cols": len(df.columns),
        "missing_values": df.isnull().sum().sum(),
        "date_range": "N/A"
    }
    
    # Attempt to find a date column
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            summary["date_range"] = f"{df[col].min().date()} to {df[col].max().date()}"
            break
        # Heuristic check for date strings if not typed
        elif "date" in col.lower() or "time" in col.lower():
            try:
                converted = pd.to_datetime(df[col], errors='coerce').dropna()
                if not converted.empty:
                    summary["date_range"] = f"{converted.min().date()} to {converted.max().date()}"
                    break
            except:
                pass
                
    return summary
