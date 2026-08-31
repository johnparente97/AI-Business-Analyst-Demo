import io
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from utils.data_loader import generate_synthetic_csv, process_uploaded_file


def test_generate_synthetic_csv():
    buf = generate_synthetic_csv()
    assert buf is not None
    assert isinstance(buf, io.BytesIO)
    df = pd.read_csv(buf)
    assert len(df) == 5000
    assert "Date" in df.columns
    assert "Category" in df.columns
    assert "Region" in df.columns
    assert "Sales Amount" in df.columns
    assert "Profit" in df.columns
    assert df["Sales Amount"].dtype in (np.float64, float)


@patch("streamlit.progress")
@patch("streamlit.error")
def test_process_uploaded_file_synthetic(mock_error, mock_progress):
    mock_bar = MagicMock()
    mock_progress.return_value = mock_bar

    buf = generate_synthetic_csv()
    summary = process_uploaded_file(buf)

    assert summary is not None
    assert summary["rows"] == 5000
    assert summary["cols"] == 5
    assert "Sales Amount" in summary["numeric_stats"]
    assert "Profit" in summary["numeric_stats"]
    assert "Category" in summary["categorical_stats"]
    assert summary["date_col"] == "Date"
    assert len(summary["trend_data"]) > 0
    assert summary["sample_data"] is not None


@patch("streamlit.progress")
@patch("streamlit.error")
def test_process_uploaded_file_empty(mock_error, mock_progress):
    mock_bar = MagicMock()
    mock_progress.return_value = mock_bar

    empty_buf = io.BytesIO(b"")
    empty_buf.name = "empty.csv"
    res = process_uploaded_file(empty_buf)
    assert res is None
    assert mock_error.called
