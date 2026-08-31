import pandas as pd
from utils.reporting import (
    generate_data_quality_report,
    generate_column_profile_report,
    export_cleaned_csv,
    export_summary_as_markdown,
    export_profile_report
)
from utils.data_profile import generate_full_profile


def test_reporting():
    df = pd.DataFrame({
        "id": [1, 2, 2, 3],
        "name": ["A", "B", "B", "C"],
        "sales": [100.0, 200.0, 200.0, 300.0]
    })
    profile = generate_full_profile(df)

    quality_rep = generate_data_quality_report(profile)
    assert "Data Quality Report" in quality_rep

    col_rep = generate_column_profile_report(profile)
    assert "Column Profile" in col_rep

    cleaned_csv = export_cleaned_csv(df, drop_duplicates=True)
    assert isinstance(cleaned_csv, bytes)
    assert len(cleaned_csv) > 0

    summary_md = export_summary_as_markdown("## Summary\nGreat performance", "Test Dataset")
    assert isinstance(summary_md, bytes)
    assert b"InsightBridge AI" in summary_md

    profile_md = export_profile_report(profile, "Test Dataset")
    assert isinstance(profile_md, bytes)
    assert b"Data Profile Report" in profile_md
