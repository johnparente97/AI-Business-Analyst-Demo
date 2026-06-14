"""
InsightBridge AI — Reporting & Export
Executive summary generation, CSV export, and profile reports.
"""
import pandas as pd
import io
from datetime import datetime


def generate_data_quality_report(profile: dict) -> str:
    """Generate a data quality section as Markdown."""
    missing = profile.get("missing_summary", {})
    dups = profile.get("duplicates", {})

    lines = ["## 📋 Data Quality Report\n"]
    lines.append(f"- **Total Cells**: {missing.get('total_cells', 0):,}")
    lines.append(f"- **Data Completeness**: {missing.get('completeness_pct', 100)}%")
    lines.append(f"- **Missing Values**: {missing.get('total_missing', 0):,}")
    lines.append(f"- **Duplicate Rows**: {dups.get('duplicate_rows', 0)} ({dups.get('duplicate_pct', 0):.1f}%)")

    cols_missing = missing.get("columns_with_missing", {})
    if cols_missing:
        lines.append("\n### Columns with Missing Values\n")
        lines.append("| Column | Missing Count | Missing % |")
        lines.append("|--------|--------------|-----------|")
        for col, info in sorted(cols_missing.items(), key=lambda x: x[1]["pct"], reverse=True):
            lines.append(f"| {col} | {info['count']:,} | {info['pct']:.1f}% |")

    return "\n".join(lines)


def generate_column_profile_report(profile: dict) -> str:
    """Generate a column-by-column profile as Markdown."""
    lines = ["## 🔬 Column Profile\n"]

    for col_name, col_info in profile.get("columns", {}).items():
        col_type = col_info.get("type", "unknown")
        icon = {"numeric": "🔢", "categorical": "🏷️", "datetime": "📅", "boolean": "✅", "identifier": "🔑"}.get(col_type, "📊")
        lines.append(f"### {icon} {col_name}")
        lines.append(f"- **Type**: {col_type.capitalize()}")
        lines.append(f"- **Missing**: {col_info.get('missing_count', 0):,} ({col_info.get('missing_pct', 0):.1f}%)")
        lines.append(f"- **Unique Values**: {col_info.get('unique_count', 0):,} ({col_info.get('unique_pct', 0):.1f}%)")

        stats = col_info.get("stats", {})
        if col_type == "numeric" and stats:
            lines.append(f"- **Mean**: {stats.get('mean', 0):,.4f}")
            lines.append(f"- **Median**: {stats.get('median', 0):,.4f}")
            lines.append(f"- **Std Dev**: {stats.get('std', 0):,.4f}")
            lines.append(f"- **Range**: [{stats.get('min', 0):,.4f}, {stats.get('max', 0):,.4f}]")
            lines.append(f"- **Skewness**: {stats.get('skew', 0):.4f}")
            outliers = col_info.get("outliers", {})
            if outliers.get("count", 0) > 0:
                lines.append(f"- **Outliers**: {outliers['count']} ({outliers['pct']:.1f}%)")

        elif col_type == "categorical" and stats:
            top_vals = stats.get("top_values", {})
            if top_vals:
                top_str = ", ".join(f'"{k}" ({v:,})' for k, v in list(top_vals.items())[:5])
                lines.append(f"- **Top Values**: {top_str}")

        elif col_type == "datetime" and stats:
            lines.append(f"- **Range**: {stats.get('min_date', 'N/A')} → {stats.get('max_date', 'N/A')}")
            lines.append(f"- **Span**: {stats.get('range_days', 0)} days")

        lines.append("")

    return "\n".join(lines)


def export_cleaned_csv(df: pd.DataFrame, drop_duplicates: bool = True,
                       selected_columns: list = None) -> bytes:
    """Export a cleaned DataFrame as CSV bytes."""
    export_df = df.copy()

    if selected_columns:
        export_df = export_df[[c for c in selected_columns if c in export_df.columns]]

    if drop_duplicates:
        export_df = export_df.drop_duplicates()

    buffer = io.BytesIO()
    export_df.to_csv(buffer, index=False)
    return buffer.getvalue()


def export_summary_as_markdown(summary_text: str, dataset_name: str = "Dataset") -> bytes:
    """Export an executive summary as a Markdown file."""
    header = f"""# InsightBridge AI — Executive Report

**Dataset**: {dataset_name}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Tool**: InsightBridge AI — Automated Business Analytics

---

"""
    full_text = header + summary_text
    return full_text.encode("utf-8")


def export_profile_report(profile: dict, dataset_name: str = "Dataset") -> bytes:
    """Export the full data profile as a Markdown file."""
    header = f"""# InsightBridge AI — Data Profile Report

**Dataset**: {dataset_name}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Rows**: {profile.get('shape', {}).get('rows', 0):,}
**Columns**: {profile.get('shape', {}).get('columns', 0)}

---

"""
    quality = generate_data_quality_report(profile)
    columns = generate_column_profile_report(profile)

    full_text = header + quality + "\n\n" + columns
    return full_text.encode("utf-8")
