# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**labor_dash** is a Python utility for loading and processing U.S. Bureau of Labor Statistics (BLS) labor market data. It fetches tab-separated flat files from BLS servers, enriches them with metadata, and prepares time series datasets for analysis and visualization.

## Running

```bash
# Run main entry point
python main.py

# Run Jupyter notebook for interactive analysis
jupyter notebook test.ipynb
```

No formal test framework is set up. Dependencies are listed in `pyproject.toml`: `pandas`, `requests`. Visualization also requires `matplotlib`.

## Architecture

The project follows a three-layer data pipeline:

1. **Generic loader** (`load_bls/loaders.py:read_bls`) — fetches any BLS tab-separated flat file URL into a cleaned DataFrame
2. **Domain-specific loaders** (`load_bls/loaders.py:get_laus`, `get_national_cps`) — combine multiple BLS files and enrich with metadata via joins
3. **Time series transformers** (`load_bls/time_series.py:get_unrate`) — extract specific indicators from loaded data

Public API is exported from `load_bls/__init__.py`: `get_laus`, `read_bls`, `get_national_cps`, `get_unrate`.

## Key Details

- BLS requests use a Mozilla User-Agent header to avoid being blocked
- `get_laus()` concatenates 9 separate time-period files (NSA 1990–2029 + seasonally adjusted current) and joins with area/measure/series metadata
- `get_national_cps()` filters out quarterly data and creates ISO 8601 date columns from BLS year+period format
- Raw BLS values are strings; conversion to numeric types happens downstream (see `test.ipynb` for pattern using `pd.to_numeric` with `errors='coerce'`)
- Visualization follows economist-style conventions: minimal spines, horizontal grid, BLS source attribution
