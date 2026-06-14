"""
InsightBridge AI — Public Data Source Connectors
Free, no-API-key-required data sources for the Public Data Explorer.
"""
import pandas as pd
import requests
import streamlit as st
import io


# ─── Source Registry ──────────────────────────────────────────────────────────

SOURCES = [
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
        "description": "U.S. public health datasets — chronic disease indicators, vaccination rates, mortality stats.",
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


def get_available_sources() -> list:
    """Return the list of available public data sources."""
    return SOURCES


# ─── World Bank ───────────────────────────────────────────────────────────────

WORLD_BANK_INDICATORS = {
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

WORLD_BANK_REGIONS = {
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


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_world_bank_data(indicator_name: str, country_code: str = "WLD",
                          start_year: int = 2000, end_year: int = 2023) -> tuple:
    """
    Fetch data from the World Bank API.
    Returns (DataFrame, metadata_dict) or (None, error_msg).
    """
    indicator_id = WORLD_BANK_INDICATORS.get(indicator_name, indicator_name)
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}"
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": 500,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if len(data) < 2 or not data[1]:
            return None, "No data returned for this indicator/country combination."

        records = []
        for item in data[1]:
            records.append({
                "Country": item.get("country", {}).get("value", ""),
                "Country Code": item.get("countryiso3code", ""),
                "Year": int(item.get("date", 0)),
                "Value": item.get("value"),
                "Indicator": item.get("indicator", {}).get("value", ""),
            })

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

CDC_DATASETS = {
    "U.S. Chronic Disease Indicators (CDI)": "g4ie-h725",
    "COVID-19 Case Surveillance": "vbim-akqf",
    "Nutrition, Physical Activity, and Obesity": "hn4x-zwk7",
    "Behavioral Risk Factor Data (BRFSS - Tobacco Use)": "wsas-xwh5",
    "National Health Interview Survey (Summary Health)": "fhky-rtsk",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cdc_data(dataset_name: str, limit: int = 5000) -> tuple:
    """
    Fetch data from CDC's SODA API.
    Returns (DataFrame, metadata_dict) or (None, error_msg).
    """
    dataset_id = CDC_DATASETS.get(dataset_name, dataset_name)
    url = f"https://data.cdc.gov/resource/{dataset_id}.json"
    params = {"$limit": limit}

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return None, "No data returned from CDC. The dataset may have moved."

        df = pd.DataFrame(data)

        # Try to convert numeric-looking columns
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

CENSUS_VARIABLES = {
    "Total Population": "B01001_001E",
    "Median Household Income": "B19013_001E",
    "Total Housing Units": "B25001_001E",
    "Median Age": "B01002_001E",
    "Poverty Status (Below Poverty Level)": "B17001_002E",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_census_data(variable_names: list, year: int = 2022) -> tuple:
    """
    Fetch data from the U.S. Census Bureau ACS API.
    Returns (DataFrame, metadata_dict) or (None, error_msg).
    """
    var_ids = [CENSUS_VARIABLES.get(v, v) for v in variable_names]
    get_vars = ",".join(["NAME"] + var_ids)
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {"get": get_vars, "for": "state:*"}

    try:
        resp = requests.get(url, params=params, timeout=15)
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

        # Convert numeric columns
        for col in df.columns:
            if col not in ["NAME", "state"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.rename(columns={"NAME": "State"})

        metadata = {
            "source_name": "U.S. Census Bureau (ACS 5-Year)",
            "source_url": f"https://data.census.gov",
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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_csv_from_url(url: str) -> tuple:
    """
    Fetch a CSV file from any public URL.
    Returns (DataFrame, metadata_dict) or (None, error_msg).
    """
    try:
        resp = requests.get(url, timeout=20, stream=True)
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
        return None, "Failed to parse the file as CSV. Check the URL points to a valid CSV."
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"


# ─── FRED (Optional — requires free API key) ─────────────────────────────────

FRED_SERIES = {
    "Unemployment Rate": "UNRATE",
    "Consumer Price Index (CPI)": "CPIAUCSL",
    "Federal Funds Rate": "FEDFUNDS",
    "Real GDP": "GDPC1",
    "10-Year Treasury Rate": "DGS10",
    "S&P 500 Index": "SP500",
    "Housing Starts": "HOUST",
    "Personal Consumption Expenditures": "PCE",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred_data(series_name: str, api_key: str,
                    start_date: str = "2000-01-01") -> tuple:
    """
    Fetch data from FRED API (requires free API key).
    Returns (DataFrame, metadata_dict) or (None, error_msg).
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
        resp = requests.get(url, params=params, timeout=15)
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
