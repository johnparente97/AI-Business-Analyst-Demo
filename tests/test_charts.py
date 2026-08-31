import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.charts import (
    create_time_series,
    create_trend_chart,
    create_correlation_heatmap,
    create_distribution_chart,
    create_box_plot,
    create_scatter_plot,
    create_categorical_chart,
    create_pie_chart,
    create_missing_values_chart
)


def test_charts():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=50, freq="D"),
        "sales": np.random.uniform(100, 1000, 50),
        "profit": np.random.uniform(10, 200, 50),
        "region": np.random.choice(["East", "West", "North", "South"], 50)
    })
    # Add a column with missing values
    df["status"] = ["active" if i % 2 == 0 else np.nan for i in range(50)]

    # Time series
    ts_fig = create_time_series(df, "date", "sales")
    assert isinstance(ts_fig, go.Figure)

    # Trend chart
    summary_data = {
        "trend_sorted": {"2024-01-01": 10, "2024-01-02": 20, "2024-01-03": 15}
    }
    trend_fig = create_trend_chart(summary_data)
    assert isinstance(trend_fig, go.Figure)

    # Correlation heatmap
    corr_fig = create_correlation_heatmap(df)
    assert isinstance(corr_fig, go.Figure)

    # Distribution
    dist_fig = create_distribution_chart(df, "sales")
    assert isinstance(dist_fig, go.Figure)

    # Box plot
    box_fig = create_box_plot(df, ["sales", "profit"])
    assert isinstance(box_fig, go.Figure)

    # Scatter plot
    scatter_fig = create_scatter_plot(df, "sales", "profit", color_col="region")
    assert isinstance(scatter_fig, go.Figure)

    # Categorical chart
    cat_fig = create_categorical_chart(df=df, column="region")
    assert isinstance(cat_fig, go.Figure)

    # Pie chart
    pie_fig = create_pie_chart(df, "region")
    assert isinstance(pie_fig, go.Figure)

    # Missing values chart
    missing_fig = create_missing_values_chart(df)
    assert isinstance(missing_fig, go.Figure)
