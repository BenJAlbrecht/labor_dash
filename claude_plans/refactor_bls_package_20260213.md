# Plan: Refactor load_BLS into a Proper Python Package

## Context

The `load_BLS/` module works but has non-standard naming, inconsistent docstrings, repeated patterns, an incomplete function, and no package tooling (`pyproject.toml`, `requirements.txt`). The goal is to refactor for readability and make it a proper installable Python package — without changing what data is scraped or the shape of outputs.

---

## Step 1: Rename `load_BLS/` → `load_bls/`

Rename the directory to PEP 8 compliant lowercase. Update all import references in:
- `main.py` (`from load_BLS.load_bls import ...` → `from load_bls import ...`)
- `test.ipynb` (`from load_BLS import ...` → `from load_bls import ...`)
- `CLAUDE.md`

**Files:** `load_BLS/` (rename), `main.py`, `test.ipynb`, `CLAUDE.md`

---

## Step 2: Create `pyproject.toml`

Add a minimal `pyproject.toml` at repo root with:
- Package metadata (name: `load-bls`, version: `0.1.0`)
- Dependencies: `pandas`, `requests`
- Python version requirement: `>=3.10`
- Build system: `setuptools`

**Files:** `pyproject.toml` (new)

---

## Step 3: Refactor `load_bls/load_bls.py` → `load_bls/loaders.py`

Rename the file to avoid the redundant `load_bls.load_bls` import path. The public API becomes `from load_bls import get_laus, read_bls, get_national_cps`.

Refactoring changes (same inputs/outputs):

1. **Extract module-level constant** for the BLS HTTP headers (currently rebuilt on every `read_bls()` call)
2. **Extract BLS URL constants** — move the LAUS and CPS URL dicts to module-level named constants for clarity
3. **Add a `_drop_footnotes()` helper** — the `footnote_codes` column drop is repeated 3 times; DRY it up with a small private helper that drops the column only if it exists
4. **Clean up `get_national_cps()`** — remove unnecessary single-entry dict wrappers for URLs; use direct string variables instead
5. **Improve column reordering** — replace the `pop/insert` pattern with a cleaner approach
6. **Convert block comments to proper docstrings** — `get_laus` and `get_national_cps` have comments above the `def` instead of docstrings inside it
7. **Consistent formatting** — remove spaces around `=` in keyword args per PEP 8

**File:** `load_bls/loaders.py` (renamed from `load_bls/load_bls.py`)

---

## Step 4: Complete `load_bls/time_series.py`

Rename `time_series_functions.py` → `time_series.py` (shorter, clearer).

Complete `get_unrate()` based on the pattern in `test.ipynb`:
- Call `get_national_cps()`
- Filter by `series_title == "(Seas) Unemployment Rate"` and `period != 'M13'`
- Convert `value` column to numeric (replace `"-"` with `pd.NA`, then `pd.to_numeric`)
- Return the filtered DataFrame

Fix the broken import (`import load_bls` → relative import `from .loaders import get_national_cps`).

**File:** `load_bls/time_series.py` (renamed from `time_series_functions.py`)

---

## Step 5: Update `load_bls/__init__.py`

Update the import source from `.load_bls` → `.loaders` and add the new `get_unrate` export from `.time_series`.

```python
from .loaders import get_laus, read_bls, get_national_cps
from .time_series import get_unrate

__all__ = ["get_laus", "read_bls", "get_national_cps", "get_unrate"]
```

**File:** `load_bls/__init__.py`

---

## Step 6: Create plan record file

Create `claude_plans/refactor_bls_package_20260213.md` with a copy of this plan for project records.

**Files:** `claude_plans/` (new dir), `claude_plans/refactor_bls_package_20260213.md` (new)

---

## Summary of file changes

| Action | Path |
|--------|------|
| Delete | `load_BLS/load_bls.py` |
| Delete | `load_BLS/time_series_functions.py` |
| Delete | `load_BLS/__init__.py` |
| Create | `load_bls/__init__.py` |
| Create | `load_bls/loaders.py` |
| Create | `load_bls/time_series.py` |
| Create | `pyproject.toml` |
| Create | `claude_plans/refactor_bls_package_20260213.md` |
| Edit   | `main.py` |
| Edit   | `test.ipynb` |
| Edit   | `CLAUDE.md` |

---

## Verification

1. `python main.py` — should print the same 5-row head of LAUS current data
2. Run `test.ipynb` cells — `get_national_cps()` should return the same DataFrame; unemployment rate plot should render identically
3. `from load_bls import get_unrate` — should return a clean numeric unemployment rate time series
4. `pip install -e .` — package should install cleanly in editable mode

---

## Status: Implemented 2026-02-13
