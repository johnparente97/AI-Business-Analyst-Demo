import pandas as pd
import numpy as np
from utils.data_profile import generate_full_profile


def test_generate_full_profile_basic():
    df = pd.DataFrame({
        "id": range(100),
        "sales": np.random.uniform(10, 500, 100),
        "cost": np.random.uniform(5, 200, 100),
        "category": np.random.choice(["A", "B", "C"], 100),
        "active": np.random.choice([True, False], 100),
        "created_at": pd.date_range("2024-01-01", periods=100, freq="D")
    })
    # inject some NaNs
    df.loc[0:4, "sales"] = np.nan

    profile = generate_full_profile(df)

    assert profile["shape"]["rows"] == 100
    assert profile["shape"]["columns"] == 6
    assert "sales" in profile["columns"]
    assert profile["columns"]["sales"]["type"] == "numeric"
    assert profile["columns"]["sales"]["missing_count"] == 5
    assert profile["missing_summary"]["total_missing"] == 5
    assert profile["correlation_matrix"] is not None
    assert len(profile["recommended_charts"]) > 0


def test_generate_full_profile_empty():
    df = pd.DataFrame()
    profile = generate_full_profile(df)
    assert profile["shape"]["rows"] == 0
    assert profile["shape"]["columns"] == 0
    assert profile["missing_summary"]["total_missing"] == 0
