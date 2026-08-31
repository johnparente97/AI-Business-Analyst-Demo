import pandas as pd
import numpy as np
from utils.ai_engine import AIEngine
from utils.data_profile import generate_full_profile


def test_ai_engine_fallback_initialization():
    engine = AIEngine()
    assert engine.provider in ("fallback", "openai", "huggingface")
    status = engine.get_provider_status()
    assert "provider" in status
    assert "label" in status


def test_ai_engine_analyze_dataset_context():
    engine = AIEngine()
    summary_data = {
        "rows": 1000,
        "cols": 3,
        "numeric_stats": {
            "sales": {"min": 10, "max": 500, "mean": 250, "std": 50, "count": 1000, "missing": 0}
        },
        "categorical_stats": {
            "category": {"A": 500, "B": 300, "C": 200}
        },
        "missing_values": {"sales": 0, "category": 0},
        "total_missing": 0,
        "date_col": "date",
        "trend_data": {"2024-01-01": 100, "2024-01-02": 200}
    }

    res = engine.analyze_dataset_context(summary_data)
    assert isinstance(res, dict)
    assert "domain" in res
    assert "key_signals" in res
    assert "recommended_actions" in res
    assert "executive_synthesis" in res


def test_ai_engine_deep_dive_and_exec_summary():
    engine = AIEngine()
    df = pd.DataFrame({
        "sales": np.random.uniform(50, 500, 50),
        "profit": np.random.uniform(10, 100, 50),
        "region": np.random.choice(["East", "West"], 50)
    })
    profile = generate_full_profile(df)

    deep_dive = engine.deep_dive_analysis(df, profile, question="What is our highest profit region?")
    assert isinstance(deep_dive, dict)
    assert "summary" in deep_dive
    assert "trends" in deep_dive

    exec_summary = engine.generate_executive_summary(df, profile)
    assert isinstance(exec_summary, str)
    assert len(exec_summary) > 50
