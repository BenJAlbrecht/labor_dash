"""
Functions to load BLS flat files into Pandas DF
https://download.bls.gov/pub/time.series/
"""
import pandas as pd
import requests
from io import StringIO

def read_bls(url):
    """
    :param url: (str) for the BLS flatfile
    :return: pandas dataframe
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://download.bls.gov/pub/time.series/"
    }

    # Fetch the file
    response = requests.get(url, headers = headers)
    response.raise_for_status()

    # Read content into DataFrame
    df = pd.read_csv(StringIO(response.text), sep = '\t', dtype = str)

    # Clean DF
    df = df.dropna(axis = 1, how = 'all') # Remove completely empty columns
    df.columns = df.columns.str.strip() # Trim whitespace from column names

    return df


"""
Function to load national LAUS data
"""
def get_laus():
    # Time series of the LAUS data
    laus_source_data = {
        # Seasonally adjusted all data
        "state_current_adjusted": "https://download.bls.gov/pub/time.series/la/la.data.1.CurrentS",
        # NSA all data
        "1990-1994": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU90-94",
        "1995-1999": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU95-99",
        "2000-2004": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU00-04",
        "2005-2009": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU05-09",
        "2010-2014": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU10-14",
        "2015-2019": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU15-19",
        "2020-2024": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU20-24",
        "2025-2029": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU25-29"
    }
    # Metadata for series, locations, and measures
    laus_meta_data = {
        "series": "https://download.bls.gov/pub/time.series/la/la.series",
        "area": "https://download.bls.gov/pub/time.series/la/la.area",
        "area_type": "https://download.bls.gov/pub/time.series/la/la.area_type",
        "measure": "https://download.bls.gov/pub/time.series/la/la.measure"
    }

    # Read all of the BLS data
    combined_df = pd.concat(
        [
            read_bls(url)
            for url in laus_source_data.values()
        ],
        ignore_index=True
    )

    # Remove redundant footnote_codes line
    combined_df = combined_df.drop("footnote_codes", axis = 1)

    # Get metadata df's
    laus_series = (
        read_bls(laus_meta_data["series"])
        .drop("footnote_codes", axis = 1)
    )
    laus_area = read_bls(laus_meta_data["area"])
    laus_area_type = read_bls(laus_meta_data["area_type"])
    laus_measure = read_bls(laus_meta_data["measure"])

    # Join metadata onto laus data
    laus_df = (
        combined_df
        .merge(laus_series, on = "series_id", how = "left")
        .merge(laus_area, on = ["area_code", "area_type_code"], how = "left")
        .merge(laus_area_type, on = "area_type_code", how = "left")
        .merge(laus_measure, on = "measure_code", how = "left")
    )

    return laus_df