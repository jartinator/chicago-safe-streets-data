"""Pull Aldermanic Menu Program spending from Ward Wise (wardwisechicago.org).

The city only publishes menu-program spending as quarterly PDFs (no structured
feed) — Ward Wise, a Chi Hack Night volunteer project, states it exposes a
public JSON API over the same data (2005-present) at /api/spendingitems.

Every endpoint returned HTTP 500 during verification (2026-07-11) — treated as
a temporary/maintenance gap in a small volunteer project, not a permanent
absence (same posture as Mellow Bike Map, see DECISIONS.md). A failure here is
non-fatal: it warns and leaves raw/menu_spending.json absent, and aggregate.py
falls back to a stub layer for that run.

Idempotent: re-running overwrites cleanly.
"""
import argparse
import sys

import requests

from config import RAW_DIR, WARD_WISE_API_URL
from socrata import write_json


def main():
    argparse.ArgumentParser(
        description="Pull aldermanic menu spending from the Ward Wise API."
    ).parse_args()

    try:
        resp = requests.get(f"{WARD_WISE_API_URL}/spendingitems", timeout=60)
        resp.raise_for_status()
        items = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"WARNING: menu_spending pull failed ({exc}) — menu_spending.json will "
              f"ship as a stub this run. See DECISIONS.md.", file=sys.stderr)
        return

    output_path = RAW_DIR / "menu_spending.json"
    write_json(output_path, items)
    print(f"menu_spending: {len(items)} spending items")


if __name__ == "__main__":
    main()
