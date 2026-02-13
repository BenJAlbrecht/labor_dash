"""
Functions to load BLS flat files into Pandas DataFrames.
https://download.bls.gov/pub/time.series/
"""

import pandas as pd
import requests
from io import StringIO

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BLS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://download.bls.gov/pub/time.series/",
}

_LAUS_DATA_URLS = {
    "state_current_adjusted": "https://download.bls.gov/pub/time.series/la/la.data.1.CurrentS",
    "1990-1994": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU90-94",
    "1995-1999": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU95-99",
    "2000-2004": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU00-04",
    "2005-2009": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU05-09",
    "2010-2014": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU10-14",
    "2015-2019": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU15-19",
    "2020-2024": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU20-24",
    "2025-2029": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU25-29",
}

_LAUS_META_URLS = {
    "series": "https://download.bls.gov/pub/time.series/la/la.series",
    "area": "https://download.bls.gov/pub/time.series/la/la.area",
    "area_type": "https://download.bls.gov/pub/time.series/la/la.area_type",
    "measure": "https://download.bls.gov/pub/time.series/la/la.measure",
}

_CPS_DATA_URL = "https://download.bls.gov/pub/time.series/ln/ln.data.1.AllData"
_CPS_SERIES_URL = "https://download.bls.gov/pub/time.series/ln/ln.series"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _drop_footnotes(df):
    """Drop the ``footnote_codes`` column if it exists."""
    return df.drop(columns="footnote_codes", errors="ignore")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def read_bls(url):
    """Fetch a BLS tab-separated flat file and return a cleaned DataFrame.

    Parameters
    ----------
    url : str
        Full URL to a BLS flat file.

    Returns
    -------
    pandas.DataFrame
        All columns are strings with whitespace stripped.
    """
    response = requests.get(url, headers=_BLS_HEADERS)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text), sep='\t', dtype=str)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda col: col.str.strip())
    df = df.dropna(axis=1, how="all")

    return df


def get_laus():
    """Load state-level LAUS data with area and measure metadata.

    Concatenates 9 BLS time-period files (NSA 1990-2029 + seasonally adjusted
    current) and joins with area, area-type, measure, and series metadata.

    Returns
    -------
    pandas.DataFrame
        Combined LAUS data enriched with metadata columns.
    """
    combined_df = _drop_footnotes(
        pd.concat(
            [read_bls(url) for url in _LAUS_DATA_URLS.values()],
            ignore_index=True,
        )
    )

    laus_series = _drop_footnotes(read_bls(_LAUS_META_URLS["series"]))
    laus_area = read_bls(_LAUS_META_URLS["area"])
    laus_area_type = read_bls(_LAUS_META_URLS["area_type"])
    laus_measure = read_bls(_LAUS_META_URLS["measure"])

    laus_df = (
        combined_df
        .merge(laus_series, on="series_id", how="left")
        .merge(laus_area, on=["area_code", "area_type_code"], how="left")
        .merge(laus_area_type, on="area_type_code", how="left")
        .merge(laus_measure, on="measure_code", how="left")
    )

    return laus_df


def get_national_cps():
    """Load national CPS data with series metadata.

    Fetches the main CPS data file and series metadata, joins them, filters
    out quarterly data, and creates an ISO 8601 date column.

    Returns
    -------
    pandas.DataFrame
        CPS data with ``date`` as the first column.
    """
    cps_data_df = _drop_footnotes(read_bls(_CPS_DATA_URL))
    cps_series = read_bls(_CPS_SERIES_URL)

    cps_df = cps_data_df.merge(cps_series, on="series_id", how="left")

    # Remove quarterly data
    cps_df = cps_df.loc[
        (cps_df["periodicity_code"] != "Q") & (cps_df["period"] != "M13")
    ]

    # Create date column and place it first
    cps_df["date"] = pd.to_datetime(
        cps_df["year"].astype(str) + "-" + cps_df["period"].str[1:] + "-01"
    )
    cps_df = cps_df[["date"] + [c for c in cps_df.columns if c != "date"]]

    return cps_df
