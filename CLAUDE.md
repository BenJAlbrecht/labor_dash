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

# Build the dashboard HTML (outputs to docs/index.html)
python -m dashboard.build
```

No formal test framework is set up. Dependencies are listed in `pyproject.toml`: `pandas`, `plotly`, `requests`. Visualization also requires `matplotlib`.

## Architecture

The project follows a four-layer data pipeline:

1. **Generic loader** (`load_bls/loaders.py:read_bls`) — fetches any BLS tab-separated flat file URL into a cleaned DataFrame
2. **Domain-specific loaders** (`load_bls/loaders.py:get_laus`, `get_national_cps`) — combine multiple BLS files and enrich with metadata via joins
3. **Time series transformers** (`load_bls/time_series.py:get_unrate`) — extract specific indicators from loaded data
4. **Dashboard** (`dashboard/`) — builds interactive Plotly charts and exports static HTML for GitHub Pages

Public API is exported from `load_bls/__init__.py`: `get_laus`, `read_bls`, `get_national_cps`, `get_unrate`.

### Dashboard Module

- `dashboard/charts.py` — pure functions: DataFrame → Plotly Figure (e.g., `create_unemployment_chart`)
- `dashboard/build.py` — CLI script that fetches data, builds charts, and writes `docs/index.html` using `fig.write_html()` with `include_plotlyjs='cdn'`

### Hosting on GitHub Pages

The `docs/` folder is the GitHub Pages source directory. To enable:

1. Go to repo Settings → Pages → Source: main branch, `/docs` folder
2. Site URL will be `https://<username>.github.io/labor_dash/`
3. Rebuild with `python -m dashboard.build` and push to update the site

## Key Details

- BLS requests use a Mozilla User-Agent header to avoid being blocked
- `get_laus()` concatenates 9 separate time-period files (NSA 1990–2029 + seasonally adjusted current) and joins with area/measure/series metadata
- `get_national_cps()` filters out quarterly data and creates ISO 8601 date columns from BLS year+period format
- Raw BLS values are strings; conversion to numeric types happens downstream (see `test.ipynb` for pattern using `pd.to_numeric` with `errors='coerce'`)
- Visualization follows economist-style conventions: minimal spines, horizontal grid, BLS source attribution

## Claude Docs

All Claude-related documents live under `claude_docs/`:

- `claude_docs/plans/` — Claude-authored plan files (`.md`)
- `claude_docs/instructions/` — User-authored task instructions (`.txt`)

**Naming convention:** All files in both folders must end with a date suffix: `_YYYYMMDD` (e.g., `plan_refactor_20260224.md`, `add_cps_endpoint_20260224.txt`).
