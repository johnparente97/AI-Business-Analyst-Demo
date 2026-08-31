"""
InsightBridge AI — Public Data Source Connectors
Free, no-API-key-required data connectors for the Public Data Explorer.
Includes resilience, retries with exponential backoff, and caching.
"""
from __future__ import annotations

import io
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

try:
    import streamlit as st
    cache_data_decorator = st.cache_data(ttl=3600, show_spinner=False)
except Exception:
    def cache_data_decorator(func):
        return func


def _get_http_session(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Session:
    """Create a requests session with automated retries and backoff."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 InsightBridgeAI/1.0",
        "Accept": "application/json, text/csv, */*",
    })
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


_HTTP_SESSION = _get_http_session()


# ─── Source Registry ──────────────────────────────────────────────────────────

SOURCES: List[Dict[str, Any]] = [
    {
        "id": "world_bank",
        "name": "World Bank Open Data",
        "category": "🌍 Economic / Market",
        "description": "Global economic indicators — GDP, population, trade, poverty, education, and more.",
        "url": "https://data.worldbank.org",
        "requires_key": False,
    },
    {
        "id": "cdc",
        "name": "CDC Open Data (SODA API)",
        "category": "🏥 Health & Wellness",
        "description": "U.S. public health datasets — leading causes of death, obesity, vaccination rates.",
        "url": "https://data.cdc.gov",
        "requires_key": False,
    },
    {
        "id": "census",
        "name": "U.S. Census Bureau",
        "category": "👥 Demographic / Census",
        "description": "Population, income, housing, and employment data for U.S. states and counties.",
        "url": "https://www.census.gov/data.html",
        "requires_key": False,
    },
    {
        "id": "csv_url",
        "name": "CSV from URL",
        "category": "🔗 Custom",
        "description": "Load any publicly accessible CSV file by pasting its URL.",
        "url": "",
        "requires_key": False,
    },
    {
        "id": "fred",
        "name": "FRED (Federal Reserve)",
        "category": "📈 Economic / Market",
        "description": "U.S. economic time series — unemployment, inflation, interest rates, GDP.",
        "url": "https://fred.stlouisfed.org",
        "requires_key": True,
    },
]


def get_available_sources() -> List[Dict[str, Any]]:
    """
    Return the registry of available public data sources.

    Returns:
        List[Dict[str, Any]]: List of source metadata dictionaries.
    """
    return SOURCES


# ─── World Bank ───────────────────────────────────────────────────────────────

WORLD_BANK_INDICATORS: Dict[str, str] = {
    "GDP (current US$)": "NY.GDP.MKTP.CD",
    "GDP per capita (current US$)": "NY.GDP.PCAP.CD",
    "GDP growth (annual %)": "NY.GDP.MKTP.KD.ZG",
    "Population, total": "SP.POP.TOTL",
    "Population growth (annual %)": "SP.POP.GROW",
    "Life expectancy at birth": "SP.DYN.LE00.IN",
    "Inflation, consumer prices (annual %)": "FP.CPI.TOTL.ZG",
    "Unemployment, total (% of labor force)": "SL.UEM.TOTL.ZS",
    "CO2 emissions (metric tons per capita)": "EN.ATM.CO2E.PC",
    "Internet users (% of population)": "IT.NET.USER.ZS",
    "Trade (% of GDP)": "NE.TRD.GNFS.ZS",
    "Foreign direct investment, net inflows (% of GDP)": "BX.KLT.DINV.WD.GD.ZS",
}

WORLD_BANK_REGIONS: Dict[str, str] = {
    "World": "WLD",
    "United States": "USA",
    "United Kingdom": "GBR",
    "China": "CHN",
    "India": "IND",
    "Germany": "DEU",
    "Japan": "JPN",
    "Brazil": "BRA",
    "France": "FRA",
    "Canada": "CAN",
    "Australia": "AUS",
    "South Africa": "ZAF",
    "Mexico": "MEX",
    "Nigeria": "NGA",
    "Indonesia": "IDN",
    "All Countries": "all",
}


@cache_data_decorator
def fetch_world_bank_data(
    indicator_name: str,
    country_code: str = "WLD",
    start_year: int = 2000,
    end_year: int = 2023,
) -> Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
    """
    Fetch historical time series from the World Bank API.

    Args:
        indicator_name: User-friendly name or code for the indicator.
        country_code: ISO3 country code (or 'WLD' for world aggregate).
        start_year: Beginning calendar year.
        end_year: Ending calendar year.

    Returns:
        Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
            (DataFrame, metadata_dict) on success, or (None, error_message) on failure.
    """
    indicator_id = WORLD_BANK_INDICATORS.get(indicator_name, indicator_name)
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}"
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": 500,
    }

    try:
        resp = _HTTP_SESSION.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if len(data) < 2 or not data[1]:
            return None, "No data returned for this indicator/country combination."

        records = [
            {
                "Country": item.get("country", {}).get("value", ""),
                "Country Code": item.get("countryiso3code", ""),
                "Year": int(item.get("date", 0)),
                "Value": item.get("value"),
                "Indicator": item.get("indicator", {}).get("value", ""),
            }
            for item in data[1]
        ]

        df = pd.DataFrame(records)
        df = df.dropna(subset=["Value"]).sort_values("Year").reset_index(drop=True)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

        metadata = {
            "source_name": "World Bank Open Data",
            "source_url": f"https://data.worldbank.org/indicator/{indicator_id}",
            "indicator": indicator_name,
            "country": country_code,
            "date_range": f"{start_year}–{end_year}",
            "records": len(df),
        }
        return df, metadata

    except requests.exceptions.RequestException as e:
        return None, f"World Bank API error: {str(e)}"
    except (KeyError, ValueError, IndexError) as e:
        return None, f"Failed to parse World Bank response: {str(e)}"


# ─── CDC Open Data (SODA API) ────────────────────────────────────────────────

CDC_DATASETS: Dict[str, str] = {
    "NCHS - Leading Causes of Death: United States": "bi63-dtpu",
    "Nutrition, Physical Activity, and Obesity": "hn4x-zwk7",
    "U.S. Vaccination Coverage & Health Survey": "fhky-rtsk",
    "COVID-19 Hospitalizations and Death Trends": "9bhg-hcku",
    "Death Rates for U.S. Leading Causes": "w9j2-ggv5",
}


@cache_data_decorator
def fetch_cdc_data(
    dataset_name: str,
    limit: int = 5000,
) -> Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
    """
    Fetch public health data from the CDC SODA API.

    Args:
        dataset_name: Display name or endpoint ID of the CDC dataset.
        limit: Max record count to retrieve.

    Returns:
        Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
            (DataFrame, metadata_dict) on success, or (None, error_message) on failure.
    """
    dataset_id = CDC_DATASETS.get(dataset_name, dataset_name)
    url = f"https://data.cdc.gov/resource/{dataset_id}.json"
    params = {"$limit": limit}

    try:
        resp = _HTTP_SESSION.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return None, "No data returned from CDC. The dataset may have moved."

        df = pd.DataFrame(data)

        # Convert numeric-looking columns efficiently
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

        metadata = {
            "source_name": "CDC Open Data",
            "source_url": f"https://data.cdc.gov/d/{dataset_id}",
            "dataset": dataset_name,
            "records": len(df),
            "columns": len(df.columns),
        }
        return df, metadata

    except requests.exceptions.RequestException as e:
        return None, f"CDC API error: {str(e)}"
    except (ValueError, KeyError) as e:
        return None, f"Failed to parse CDC response: {str(e)}"


# ─── U.S. Census Bureau ──────────────────────────────────────────────────────

CENSUS_VARIABLES: Dict[str, str] = {
    "Total Population": "B01001_001E",
    "Median Household Income": "B19013_001E",
    "Total Housing Units": "B25001_001E",
    "Median Age": "B01002_001E",
    "Poverty Status (Below Poverty Level)": "B17001_002E",
}


@cache_data_decorator
def fetch_census_data(
    variable_names: List[str],
    year: int = 2022,
) -> Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
    """
    Fetch demographic indicators from the U.S. Census Bureau ACS 5-Year API.

    Args:
        variable_names: List of friendly Census variable names.
        year: Survey year (default 2022).

    Returns:
        Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
            (DataFrame, metadata_dict) on success, or (None, error_message) on failure.
    """
    var_ids = [CENSUS_VARIABLES.get(v, v) for v in variable_names]
    get_vars = ",".join(["NAME"] + var_ids)
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {"get": get_vars, "for": "state:*"}

    try:
        resp = _HTTP_SESSION.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if len(data) < 2:
            return None, "No data returned from Census API."

        headers = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=headers)

        # Rename variable IDs to friendly names
        rename_map = {v: k for k, v in CENSUS_VARIABLES.items() if v in df.columns}
        df = df.rename(columns=rename_map)

        for col in df.columns:
            if col not in ["NAME", "state"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.rename(columns={"NAME": "State"})

        metadata = {
            "source_name": "U.S. Census Bureau (ACS 5-Year)",
            "source_url": "https://data.census.gov",
            "variables": variable_names,
            "year": year,
            "records": len(df),
        }
        return df, metadata

    except requests.exceptions.RequestException as e:
        return None, f"Census API error: {str(e)}"
    except (ValueError, KeyError, IndexError) as e:
        return None, f"Failed to parse Census response: {str(e)}"


# ─── CSV from URL ─────────────────────────────────────────────────────────────

@cache_data_decorator
def fetch_csv_from_url(url: str) -> Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
    """
    Fetch and parse a CSV file from a publicly accessible URL.

    Args:
        url: Direct link to the CSV resource.

    Returns:
        Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
            (DataFrame, metadata_dict) on success, or (None, error_message) on failure.
    """
    try:
        resp = _HTTP_SESSION.get(url, timeout=20, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "html" in content_type.lower() and "csv" not in url.lower():
            return None, "The URL returned HTML, not a CSV file. Check the URL."

        df = pd.read_csv(io.StringIO(resp.text))

        if df.empty:
            return None, "The CSV file is empty."

        metadata = {
            "source_name": "Custom CSV URL",
            "source_url": url,
            "records": len(df),
            "columns": len(df.columns),
        }
        return df, metadata

    except pd.errors.ParserError:
        return None, "Failed to parse the file as CSV. Check that the URL points to valid CSV data."
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"


# ─── FRED (Federal Reserve) ──────────────────────────────────────────────────

FRED_SERIES: Dict[str, str] = {
    "Unemployment Rate": "UNRATE",
    "Consumer Price Index (CPI)": "CPIAUCSL",
    "Federal Funds Rate": "FEDFUNDS",
    "Real GDP": "GDPC1",
    "10-Year Treasury Rate": "DGS10",
    "S&P 500 Index": "SP500",
    "Housing Starts": "HOUST",
    "Personal Consumption Expenditures": "PCE",
}


@cache_data_decorator
def fetch_fred_data(
    series_name: str,
    api_key: str,
    start_date: str = "2000-01-01",
) -> Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
    """
    Fetch economic time series from the FRED API.

    Args:
        series_name: Friendly name or FRED series identifier.
        api_key: FRED API token.
        start_date: Earliest observation date (YYYY-MM-DD).

    Returns:
        Tuple[Optional[pd.DataFrame], Union[Dict[str, Any], str]]:
            (DataFrame, metadata_dict) on success, or (None, error_message) on failure.
    """
    series_id = FRED_SERIES.get(series_name, series_name)
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
    }

    try:
        resp = _HTTP_SESSION.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        observations = data.get("observations", [])
        if not observations:
            return None, "No observations returned from FRED."

        df = pd.DataFrame(observations)
        df = df[["date", "value"]].copy()
        df.columns = ["Date", series_name]
        df["Date"] = pd.to_datetime(df["Date"])
        df[series_name] = pd.to_numeric(df[series_name], errors="coerce")
        df = df.dropna().reset_index(drop=True)

        metadata = {
            "source_name": "Federal Reserve Economic Data (FRED)",
            "source_url": f"https://fred.stlouisfed.org/series/{series_id}",
            "series": series_name,
            "start_date": start_date,
            "records": len(df),
        }
        return df, metadata

    except requests.exceptions.RequestException as e:
        return None, f"FRED API error: {str(e)}"
    except (ValueError, KeyError) as e:
        return None, f"Failed to parse FRED response: {str(e)}"
