"""CLI script to build the dashboard HTML.

Usage::

    python -m dashboard.build
"""

import pathlib

import load_bls as bls
from .charts import create_unemployment_chart

DOCS_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs"


def build_dashboard():
    """Fetch BLS data, build charts, and write ``docs/index.html``."""
    print("Fetching unemployment rate data from BLS...")
    unrate = bls.get_unrate()

    print(f"  {len(unrate)} observations loaded.")
    fig = create_unemployment_chart(unrate)

    DOCS_DIR.mkdir(exist_ok=True)

    out_path = DOCS_DIR / "index.html"
    fig.write_html(str(out_path), include_plotlyjs="cdn")
    print(f"Wrote {out_path}")

    nojekyll = DOCS_DIR / ".nojekyll"
    nojekyll.touch()
    print(f"Wrote {nojekyll}")


if __name__ == "__main__":
    build_dashboard()
