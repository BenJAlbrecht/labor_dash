"""
Functions to transform BLS DataFrames into simple, usable time series.

CPS data:
    1) Unemployment Rate
"""

import pandas as pd

from .loaders import get_national_cps


def get_unrate():
    """Return the national seasonally-adjusted unemployment rate as a time series.

    Calls :func:`get_national_cps`, filters to the "(Seas) Unemployment Rate"
    series, and converts values to numeric.

    Returns
    -------
    pandas.DataFrame
        Columns include ``date``, ``value`` (float), and CPS metadata.
    """
    cps = get_national_cps()

    unrate = cps.loc[cps["series_title"] == "(Seas) Unemployment Rate"].copy()
    unrate["value"] = (
        unrate["value"]
        .replace("-", pd.NA)
        .pipe(pd.to_numeric, errors="coerce")
    )

    return unrate
