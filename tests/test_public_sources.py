"""
Unit tests for public data source connectors.
"""
import io
import pandas as pd
from unittest.mock import MagicMock, patch

from utils.public_sources import (
    get_available_sources,
    fetch_world_bank_data,
    fetch_cdc_data,
    fetch_census_data,
    fetch_csv_from_url,
    fetch_fred_data,
)


def test_get_available_sources():
    sources = get_available_sources()
    assert isinstance(sources, list)
    assert len(sources) >= 4
    source_ids = [s["id"] for s in sources]
    assert "world_bank" in source_ids
    assert "cdc" in source_ids
    assert "census" in source_ids


@patch("utils.public_sources._HTTP_SESSION.get")
def test_fetch_world_bank_data_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"page": 1, "pages": 1, "per_page": 500, "total": 2},
        [
            {"country": {"value": "World"}, "countryiso3code": "WLD", "date": "2020", "value": 85000000000000, "indicator": {"value": "GDP (current US$)"}},
            {"country": {"value": "World"}, "countryiso3code": "WLD", "date": "2021", "value": 96000000000000, "indicator": {"value": "GDP (current US$)"}},
        ]
    ]
    mock_get.return_value = mock_resp

    df, metadata = fetch_world_bank_data("GDP (current US$)", "WLD", 2020, 2021)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "Year" in df.columns
    assert "Value" in df.columns
    assert isinstance(metadata, dict)
    assert metadata["source_name"] == "World Bank Open Data"


@patch("utils.public_sources._HTTP_SESSION.get")
def test_fetch_cdc_data_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"year": "2021", "locationdesc": "California", "datavalue": "24.5"},
        {"year": "2021", "locationdesc": "New York", "datavalue": "22.1"},
    ]
    mock_get.return_value = mock_resp

    df, metadata = fetch_cdc_data("NCHS - Leading Causes of Death: United States", limit=10)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert isinstance(metadata, dict)
    assert metadata["source_name"] == "CDC Open Data"


@patch("utils.public_sources._HTTP_SESSION.get")
def test_fetch_census_data_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        ["NAME", "B01001_001E", "state"],
        ["California", "39000000", "06"],
        ["Texas", "29000000", "48"],
    ]
    mock_get.return_value = mock_resp

    df, metadata = fetch_census_data(["Total Population"], year=2022)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "State" in df.columns
    assert "Total Population" in df.columns
    assert isinstance(metadata, dict)


@patch("utils.public_sources._HTTP_SESSION.get")
def test_fetch_csv_from_url_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/csv"}
    mock_resp.text = "Region,Sales,Profit\nNorth,100,20\nSouth,150,30\n"
    mock_get.return_value = mock_resp

    df, metadata = fetch_csv_from_url("https://example.com/data.csv")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["Region", "Sales", "Profit"]
    assert isinstance(metadata, dict)


@patch("utils.public_sources._HTTP_SESSION.get")
def test_fetch_fred_data_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "observations": [
            {"date": "2023-01-01", "value": "3.4"},
            {"date": "2023-02-01", "value": "3.6"},
        ]
    }
    mock_get.return_value = mock_resp

    df, metadata = fetch_fred_data("Unemployment Rate", api_key="dummy_key", start_date="2023-01-01")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "Date" in df.columns
    assert "Unemployment Rate" in df.columns
    assert isinstance(metadata, dict)
