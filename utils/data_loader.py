import pandas as pd
import streamlit as st
import numpy as np
from collections import Counter
import io

def process_uploaded_file(uploaded_file):
    """
    Reads a CSV file in chunks and computes aggregated statistics and visualization data.
    Returns a dictionary containing the analysis results.
    """
    CHUNK_SIZE = 100_000
    
    # Initialize accumulators
    summary = {
        "rows": 0,
        "cols": 0,
        "column_info": {}, # {name: dtype}
        "numeric_stats": {}, # {col: {min, max, sum, sum_sq, count, missing}}
        "categorical_stats": {}, # {col: Counter()}
        "missing_values": {}, # {col: count}
        "total_missing": 0,
        "date_col": None,
        "trend_data": {}, # {date_str: count}
        "trend_type": None, # 'daily' or 'raw'
        "sample_data": None # First few rows for preview
    }
    
    processed_first_chunk = False
    numeric_cols = []
    categorical_cols = []
    date_cols = []
    
    # Check total size for progress bar
    uploaded_file.seek(0, 2)
    total_size = uploaded_file.tell()
    uploaded_file.seek(0)
    
    progress_bar = st.progress(0, text="Processing data chunks...")
    bytes_read = 0
    
    try:
        # Iterate through chunks
        for chunk in pd.read_csv(uploaded_file, chunksize=CHUNK_SIZE):
            # Update bytes read for progress calculation (approximate)
            bytes_read += chunk.memory_usage(deep=True).sum() # This is memory size, not file size, but good enough proxy for progress if normalized carefully or just mapped to iteration if we knew row count. 
            # Actually, read_csv doesn't tell us bytes read easily. Let's just update progress based on a rough estimate or just keep it spinning/pulsing if precise byte tracking is hard.
            # However, standard practice: just increment strictly. 
            # Let's use a simpler progress update:
            current_prog = min(bytes_read / (total_size * 2), 0.95) # Heuristic
            progress_bar.progress(current_prog, text=f"Processing {summary['rows']:,} rows...")

            # 1. logical type detection (only on first chunk to set schema)
            if not processed_first_chunk:
                summary["sample_data"] = chunk.head(5)
                summary["cols"] = len(chunk.columns)
                summary["column_info"] = {c: str(chunk[c].dtype) for c in chunk.columns}
                
                # Detect types
                for col in chunk.columns:
                    if pd.api.types.is_numeric_dtype(chunk[col]):
                        numeric_cols.append(col)
                        summary["numeric_stats"][col] = {
                            "min": float('inf'), "max": float('-inf'), 
                            "sum": 0.0, "sum_sq": 0.0, "count": 0, "missing": 0
                        }
                    elif pd.api.types.is_datetime64_any_dtype(chunk[col]):
                         date_cols.append(col)
                    else:
                        # Try to detect date strings
                        if "date" in col.lower() or "time" in col.lower():
                            try:
                                # Test conversion
                                pd.to_datetime(chunk[col].head(100), errors='raise')
                                date_cols.append(col)
                            except:
                                categorical_cols.append(col)
                                summary["categorical_stats"][col] = Counter()
                        else:
                            categorical_cols.append(col)
                            summary["categorical_stats"][col] = Counter()

                if date_cols:
                    summary["date_col"] = date_cols[0]

                processed_first_chunk = True

            # 2. Process Numeric Cols
            for col in numeric_cols:
                # Handle missing before conversion
                n_missing = chunk[col].isna().sum()
                summary["numeric_stats"][col]["missing"] += int(n_missing)
                summary["missing_values"][col] = summary["missing_values"].get(col, 0) + int(n_missing)
                summary["total_missing"] += int(n_missing)

                # Operations on valid data
                valid = chunk[col].dropna()
                if not valid.empty:
                    summary["numeric_stats"][col]["min"] = min(summary["numeric_stats"][col]["min"], valid.min())
                    summary["numeric_stats"][col]["max"] = max(summary["numeric_stats"][col]["max"], valid.max())
                    s = valid.sum()
                    summary["numeric_stats"][col]["sum"] += s
                    summary["numeric_stats"][col]["sum_sq"] += (valid ** 2).sum()
                    summary["numeric_stats"][col]["count"] += len(valid)

            # 3. Process Categorical Cols (Top N tracking)
            for col in categorical_cols:
                # Limit memory: only track top 50 values per chunk, then merge? 
                # Better: just update counter, but prune if it gets too big to avoid OOM on high cardinality
                counts = chunk[col].value_counts().head(50).to_dict() # Only keep top 50 local
                summary["categorical_stats"][col].update(counts)
                
                # Prune global counter to top 50 to prevent unbounded growth
                if len(summary["categorical_stats"][col]) > 100:
                    summary["categorical_stats"][col] = Counter(dict(summary["categorical_stats"][col].most_common(50)))
                    
                n_missing = chunk[col].isna().sum()
                summary["missing_values"][col] = summary["missing_values"].get(col, 0) + int(n_missing)
                summary["total_missing"] += int(n_missing)

            # 4. Process Date/Trend (Volume over time)
            if summary["date_col"]:
                d_col = summary["date_col"]
                # Convert to datetime
                dates = pd.to_datetime(chunk[d_col], errors='coerce').dropna()
                if not dates.empty:
                    # Resample to Daily counts
                    daily_counts = dates.dt.floor('D').value_counts()
                    for date_val, count in daily_counts.items():
                        d_str = date_val.strftime('%Y-%m-%d')
                        summary["trend_data"][d_str] = summary["trend_data"].get(d_str, 0) + count

            summary["rows"] += len(chunk)

        # Post-Processing
        progress_bar.progress(1.0, text="Finalizing analysis...")
        
        # Calculate Final Numeric Stats (Mean, Std)
        for col in numeric_cols:
            stats = summary["numeric_stats"][col]
            if stats["count"] > 0:
                stats["mean"] = stats["sum"] / stats["count"]
                # Variance = (SumSq - (Sum^2)/N) / N
                variance = (stats["sum_sq"] - (stats["sum"]**2)/stats["count"]) / stats["count"]
                stats["std"] = np.sqrt(variance) if variance > 0 else 0.0
            else:
                stats["mean"] = 0
                stats["std"] = 0

        # Sort Trend Data
        if summary["trend_data"]:
             sorted_dates = sorted(summary["trend_data"].keys())
             summary["trend_sorted"] = {k: summary["trend_data"][k] for k in sorted_dates}
             # determine range
             summary["date_range"] = f"{sorted_dates[0]} to {sorted_dates[-1]}"
        else:
            summary["date_range"] = "N/A"
            summary["trend_sorted"] = {}

        progress_bar.empty()
        return summary

    except Exception as e:
        progress_bar.empty()
        st.error(f"Error processing file: {e}")
        return None
