"""
InsightBridge AI — High-Performance Streaming Data Loader
Processes datasets up to 200MB in chunked streaming fashion to prevent memory exhaustion.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
import io
import random
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import streamlit as st
except ImportError:
    st = None


def generate_synthetic_csv() -> io.BytesIO:
    """
    Generate a realistic enterprise retail sales dataset as an in-memory CSV buffer.

    Returns:
        io.BytesIO: In-memory buffer containing the synthetic CSV data.
    """
    rows = 5000

    # 1. Date Range (Last 6 months)
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(180)]
    col_dates = [random.choice(dates) for _ in range(rows)]

    # 2. Categories
    categories = ["Electronics", "Home & Garden", "Fashion", "Sports", "Beauty"]
    col_cats = [random.choice(categories) for _ in range(rows)]

    # 3. Regions
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    col_regions = [random.choice(regions) for _ in range(rows)]

    # 4. Metrics (Sales, Profit)
    col_sales = [round(random.uniform(50.0, 1500.0), 2) for _ in range(rows)]
    col_profit = [round(s * random.uniform(0.1, 0.4), 2) for s in col_sales]

    df = pd.DataFrame({
        "Date": col_dates,
        "Category": col_cats,
        "Region": col_regions,
        "Sales Amount": col_sales,
        "Profit": col_profit,
    })

    # Intentionally add sparse missing values for testing data quality routines
    mask = np.random.choice([True, False], size=rows, p=[0.02, 0.98])
    df.loc[mask, "Region"] = np.nan

    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    buffer.name = "sample_retail_data.csv"
    return buffer


def process_uploaded_file(uploaded_file: Any) -> Optional[Dict[str, Any]]:
    """
    Read a CSV file in chunked streams and compute aggregate statistics and time series data.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like object.

    Returns:
        Optional[Dict[str, Any]]: Summary dictionary with statistics, or None if processing fails.
    """
    chunk_size = 100_000

    summary: Dict[str, Any] = {
        "rows": 0,
        "cols": 0,
        "column_info": {},
        "numeric_stats": {},
        "categorical_stats": {},
        "missing_values": {},
        "total_missing": 0,
        "date_col": None,
        "trend_data": {},
        "trend_type": None,
        "sample_data": None,
    }

    processed_first_chunk = False
    numeric_cols: List[str] = []
    categorical_cols: List[str] = []
    date_cols: List[str] = []

    progress_bar = None
    if st is not None:
        try:
            progress_bar = st.progress(0, text="Processing data chunks...")
        except Exception:
            progress_bar = None

    chunk_count = 0

    try:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
            chunk_count += 1
            if progress_bar is not None:
                current_prog = min(chunk_count / 50.0, 0.95)
                progress_bar.progress(current_prog, text=f"Processing {summary['rows']:,} rows...")

            # 1. Schema detection on first chunk
            if not processed_first_chunk:
                summary["sample_data"] = chunk.head(5)
                summary["cols"] = len(chunk.columns)
                summary["column_info"] = {c: str(chunk[c].dtype) for c in chunk.columns}

                for col in chunk.columns:
                    if pd.api.types.is_numeric_dtype(chunk[col]):
                        numeric_cols.append(col)
                        summary["numeric_stats"][col] = {
                            "min": float("inf"),
                            "max": float("-inf"),
                            "sum": 0.0,
                            "sum_sq": 0.0,
                            "count": 0,
                            "missing": 0,
                        }
                    elif pd.api.types.is_datetime64_any_dtype(chunk[col]):
                        date_cols.append(col)
                    else:
                        if "date" in col.lower() or "time" in col.lower():
                            try:
                                pd.to_datetime(chunk[col].head(100), errors="raise")
                                date_cols.append(col)
                            except (ValueError, TypeError, pd.errors.ParserError):
                                categorical_cols.append(col)
                                summary["categorical_stats"][col] = Counter()
                        else:
                            categorical_cols.append(col)
                            summary["categorical_stats"][col] = Counter()

                if date_cols:
                    summary["date_col"] = date_cols[0]

                processed_first_chunk = True

            # 2. Process numeric columns
            for col in numeric_cols:
                n_missing = int(chunk[col].isna().sum())
                summary["numeric_stats"][col]["missing"] += n_missing
                summary["missing_values"][col] = summary["missing_values"].get(col, 0) + n_missing
                summary["total_missing"] += n_missing

                valid = chunk[col].dropna()
                if not valid.empty:
                    summary["numeric_stats"][col]["min"] = min(
                        summary["numeric_stats"][col]["min"], float(valid.min())
                    )
                    summary["numeric_stats"][col]["max"] = max(
                        summary["numeric_stats"][col]["max"], float(valid.max())
                    )
                    s = float(valid.sum())
                    summary["numeric_stats"][col]["sum"] += s
                    summary["numeric_stats"][col]["sum_sq"] += float((valid ** 2).sum())
                    summary["numeric_stats"][col]["count"] += len(valid)

            # 3. Process categorical columns with bounded Counter size
            for col in categorical_cols:
                counts = chunk[col].value_counts().head(50).to_dict()
                summary["categorical_stats"][col].update(counts)

                if len(summary["categorical_stats"][col]) > 100:
                    summary["categorical_stats"][col] = Counter(
                        dict(summary["categorical_stats"][col].most_common(50))
                    )

                n_missing = int(chunk[col].isna().sum())
                summary["missing_values"][col] = summary["missing_values"].get(col, 0) + n_missing
                summary["total_missing"] += n_missing

            # 4. Process temporal trend aggregation
            if summary["date_col"]:
                d_col = summary["date_col"]
                dates = pd.to_datetime(chunk[d_col], errors="coerce").dropna()
                if not dates.empty:
                    daily_counts = dates.dt.floor("D").value_counts()
                    for date_val, count in daily_counts.items():
                        d_str = date_val.strftime("%Y-%m-%d")
                        summary["trend_data"][d_str] = summary["trend_data"].get(d_str, 0) + int(count)

            summary["rows"] += len(chunk)

        if progress_bar is not None:
            progress_bar.progress(1.0, text="Finalizing analysis...")

        # Calculate final numeric stats (mean, std)
        for col in numeric_cols:
            stats = summary["numeric_stats"][col]
            if stats["count"] > 0:
                stats["mean"] = stats["sum"] / stats["count"]
                variance = max(0.0, (stats["sum_sq"] - (stats["sum"] ** 2) / stats["count"]) / stats["count"])
                stats["std"] = float(np.sqrt(variance))
            else:
                stats["mean"] = 0.0
                stats["std"] = 0.0

        # Sort trend data
        if summary["trend_data"]:
            sorted_dates = sorted(summary["trend_data"].keys())
            summary["trend_sorted"] = {k: summary["trend_data"][k] for k in sorted_dates}
            summary["date_range"] = f"{sorted_dates[0]} to {sorted_dates[-1]}"
        else:
            summary["date_range"] = "N/A"
            summary["trend_sorted"] = {}

        if progress_bar is not None:
            progress_bar.empty()
        return summary

    except Exception as e:
        if progress_bar is not None:
            progress_bar.empty()
        if st is not None:
            try:
                st.error(f"Error processing file: {e}")
            except Exception:
                pass
        return None
