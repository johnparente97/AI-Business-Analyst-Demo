"""
InsightBridge AI — Deep Data Profiling
Automatic dataset analysis: types, missing values, outliers, correlations, recommendations.
"""
import pandas as pd
import numpy as np
from collections import Counter


def generate_full_profile(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive data profile for a DataFrame.
    Returns a dict with all profiling results.
    """
    profile = {
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": {},
        "missing_summary": _analyze_missing(df),
        "duplicates": _analyze_duplicates(df),
        "numeric_summary": {},
        "categorical_summary": {},
        "correlation_matrix": None,
        "datetime_columns": [],
        "recommended_charts": [],
    }

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    datetime_cols = _detect_datetime_columns(df)

    # ── Per-Column Profiling ──
    for col in df.columns:
        col_profile = {
            "dtype": str(df[col].dtype),
            "missing_count": int(df[col].isna().sum()),
            "missing_pct": round(df[col].isna().mean() * 100, 2),
            "unique_count": int(df[col].nunique()),
            "unique_pct": round(df[col].nunique() / max(1, len(df)) * 100, 2),
        }

        if col in numeric_cols:
            col_profile["type"] = "numeric"
            col_profile["stats"] = _numeric_stats(df[col])
            col_profile["outliers"] = _detect_outliers_iqr(df[col])
        elif col in datetime_cols:
            col_profile["type"] = "datetime"
            col_profile["stats"] = _datetime_stats(df, col)
        elif col_profile["unique_pct"] > 90 and len(df) > 100:
            col_profile["type"] = "identifier"
        elif df[col].dtype == "bool" or df[col].nunique() == 2:
            col_profile["type"] = "boolean"
            col_profile["stats"] = _categorical_stats(df[col])
        else:
            col_profile["type"] = "categorical"
            col_profile["stats"] = _categorical_stats(df[col])

        profile["columns"][col] = col_profile

    # ── Numeric Summary ──
    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        profile["numeric_summary"] = desc
        # Correlation matrix
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            profile["correlation_matrix"] = corr

    # ── Categorical Summary ──
    for col in categorical_cols:
        top_cats = df[col].value_counts().head(15)
        profile["categorical_summary"][col] = {
            "top_values": top_cats.to_dict(),
            "unique_count": int(df[col].nunique()),
            "cardinality": "high" if df[col].nunique() > 50 else "medium" if df[col].nunique() > 10 else "low",
        }

    # ── Datetime Columns ──
    profile["datetime_columns"] = datetime_cols

    # ── Chart Recommendations ──
    profile["recommended_charts"] = _recommend_charts(df, numeric_cols, categorical_cols, datetime_cols)

    return profile


def _analyze_missing(df: pd.DataFrame) -> dict:
    """Analyze missing values across the DataFrame."""
    missing = df.isnull().sum()
    total_cells = len(df) * len(df.columns)
    total_missing = int(missing.sum())
    return {
        "total_missing": total_missing,
        "total_cells": total_cells,
        "completeness_pct": round((1 - total_missing / max(1, total_cells)) * 100, 2),
        "columns_with_missing": {
            col: {"count": int(v), "pct": round(v / len(df) * 100, 2)}
            for col, v in missing[missing > 0].items()
        },
    }


def _analyze_duplicates(df: pd.DataFrame) -> dict:
    """Detect duplicate rows."""
    dup_count = int(df.duplicated().sum())
    return {
        "duplicate_rows": dup_count,
        "duplicate_pct": round(dup_count / max(1, len(df)) * 100, 2),
        "is_clean": dup_count == 0,
    }


def _detect_datetime_columns(df: pd.DataFrame) -> list:
    """Auto-detect columns that contain datetime data."""
    dt_cols = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            dt_cols.append(col)
        elif df[col].dtype == "object":
            # Heuristic: check column name
            if any(kw in col.lower() for kw in ["date", "time", "timestamp", "created", "updated"]):
                try:
                    pd.to_datetime(df[col].dropna().head(50), errors="raise")
                    dt_cols.append(col)
                except (ValueError, TypeError, pd.errors.ParserError):
                    pass
    return dt_cols


def _numeric_stats(series: pd.Series) -> dict:
    """Compute detailed numeric statistics."""
    clean = series.dropna()
    if clean.empty:
        return {}
    stats = {
        "mean": round(float(clean.mean()), 4),
        "median": round(float(clean.median()), 4),
        "std": round(float(clean.std()), 4),
        "min": round(float(clean.min()), 4),
        "max": round(float(clean.max()), 4),
        "q25": round(float(clean.quantile(0.25)), 4),
        "q75": round(float(clean.quantile(0.75)), 4),
        "skew": round(float(clean.skew()), 4),
        "kurtosis": round(float(clean.kurtosis()), 4),
        "range": round(float(clean.max() - clean.min()), 4),
        "cv": round(float(clean.std() / clean.mean() * 100), 2) if clean.mean() != 0 else 0.0,
    }
    return stats


def _detect_outliers_iqr(series: pd.Series) -> dict:
    """Detect outliers using the IQR method."""
    clean = series.dropna()
    if clean.empty:
        return {"count": 0, "pct": 0.0, "lower_bound": 0, "upper_bound": 0}
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = clean[(clean < lower) | (clean > upper)]
    return {
        "count": int(len(outliers)),
        "pct": round(len(outliers) / len(clean) * 100, 2),
        "lower_bound": round(float(lower), 4),
        "upper_bound": round(float(upper), 4),
    }


def _datetime_stats(df: pd.DataFrame, col: str) -> dict:
    """Compute datetime column statistics."""
    try:
        dates = pd.to_datetime(df[col], errors="coerce").dropna()
        if dates.empty:
            return {}
        return {
            "min_date": str(dates.min().date()),
            "max_date": str(dates.max().date()),
            "range_days": int((dates.max() - dates.min()).days),
            "unique_dates": int(dates.dt.date.nunique()),
        }
    except Exception:
        return {}


def _categorical_stats(series: pd.Series) -> dict:
    """Compute categorical column statistics."""
    clean = series.dropna()
    if clean.empty:
        return {}
    vc = clean.value_counts()
    top_5 = vc.head(5)
    return {
        "top_values": {str(k): int(v) for k, v in top_5.items()},
        "top_pct": {str(k): round(v / len(clean) * 100, 2) for k, v in top_5.items()},
        "unique_count": int(clean.nunique()),
        "mode": str(vc.index[0]) if len(vc) > 0 else "N/A",
    }


def _recommend_charts(df, numeric_cols, categorical_cols, datetime_cols) -> list:
    """Suggest chart types based on data composition."""
    recommendations = []

    if datetime_cols and numeric_cols:
        recommendations.append({
            "type": "time_series",
            "title": "📈 Time Series Trends",
            "description": f"Plot {numeric_cols[0]} over {datetime_cols[0]}",
            "columns": [datetime_cols[0], numeric_cols[0]],
        })

    if len(numeric_cols) >= 2:
        recommendations.append({
            "type": "correlation",
            "title": "🔥 Correlation Heatmap",
            "description": "Discover relationships between numeric variables",
            "columns": numeric_cols[:8],
        })
        recommendations.append({
            "type": "scatter",
            "title": "🔬 Scatter Analysis",
            "description": f"Compare {numeric_cols[0]} vs {numeric_cols[1]}",
            "columns": [numeric_cols[0], numeric_cols[1]],
        })

    if numeric_cols:
        recommendations.append({
            "type": "distribution",
            "title": "📊 Distribution Analysis",
            "description": "Examine value distributions and outliers",
            "columns": numeric_cols[:4],
        })

    if categorical_cols and numeric_cols:
        recommendations.append({
            "type": "categorical",
            "title": "📋 Category Breakdown",
            "description": f"Compare {numeric_cols[0]} across {categorical_cols[0]}",
            "columns": [categorical_cols[0], numeric_cols[0]],
        })

    if categorical_cols:
        recommendations.append({
            "type": "pie",
            "title": "🍩 Composition Analysis",
            "description": f"Value distribution of {categorical_cols[0]}",
            "columns": [categorical_cols[0]],
        })

    return recommendations
