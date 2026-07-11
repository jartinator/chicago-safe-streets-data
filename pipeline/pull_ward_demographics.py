"""Pull ward-level population from the ACS 5-Year by-Ward dataset.

Used as the density denominator for ward_safety_index.json (crashes-per-capita)
so wards can be compared fairly rather than by raw count. The city publishes
this dataset pre-aggregated to the current 2023 ward remap (confirmed via the
"acs_year"/"ward"/"total_population" fields, live 2026-07-11) — no manual
census-tract-to-ward spatial join needed.

Idempotent: re-running overwrites cleanly. Exit code 1 if no rows fetched.
"""
import argparse
import sys

from config import DATASETS, RAW_DIR
from socrata import fetch_all, write_json


def main():
    argparse.ArgumentParser(
        description="Pull ACS 5-Year by-ward population from Socrata."
    ).parse_args()

    dataset_id = DATASETS["acs_ward"]
    print(f"Fetching ward_demographics: {dataset_id}", file=sys.stderr)
    select = "acs_year,ward,total_population"
    rows = list(fetch_all(dataset_id, select=select))

    if not rows:
        print("ward_demographics: 0 rows")
        sys.exit(1)

    # Dataset is "Most Recent Year" (one row per ward already), but keep only
    # the latest acs_year per ward defensively in case that ever changes.
    latest = {}
    for r in rows:
        w = str(r.get("ward"))
        yr = r.get("acs_year")
        if w not in latest or (yr or "") > (latest[w].get("acs_year") or ""):
            latest[w] = r

    output_path = RAW_DIR / "ward_demographics.json"
    write_json(output_path, list(latest.values()))

    years = sorted({r.get("acs_year") for r in latest.values() if r.get("acs_year")})
    print(f"ward_demographics: {len(latest)} wards, acs_year(s) {years}")


if __name__ == "__main__":
    main()
