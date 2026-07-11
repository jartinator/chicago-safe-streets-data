"""Pull the Traffic Crashes - People dataset from Chicago Data Portal.

Filters to BICYCLE person_type on and after CRASH_START_DATE (or --since override),
selects a fixed column set for analysis, and saves to pipeline/raw/people_bicycle.json.

Idempotent: re-running overwrites cleanly. Exit code 1 if no rows fetched.
"""
import argparse
import sys
from datetime import datetime

from config import DATASETS, CRASH_START_DATE, RAW_DIR
from socrata import fetch_all, write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull Traffic Crashes - People data for bicycles from Socrata."
    )
    parser.add_argument(
        "--since",
        type=str,
        default=CRASH_START_DATE,
        help=f"Crash start date (YYYY-MM-DD, default {CRASH_START_DATE})",
    )
    args = parser.parse_args()

    # Construct the SoQL where clause: person_type='BICYCLE' AND crash_date >= since
    since_iso = f"{args.since}T00:00:00"
    where = f"person_type='BICYCLE' AND crash_date>='{since_iso}'"

    # Select exactly these columns
    select = "crash_record_id,crash_date,person_type,injury_classification,age,sex,safety_equipment"

    # Fetch all matching rows
    dataset_id = DATASETS["people"]
    print(f"Fetching people_bicycle: {dataset_id}", file=sys.stderr)
    rows = list(fetch_all(dataset_id, select=select, where=where))

    if not rows:
        print("people_bicycle: 0 rows")
        sys.exit(1)

    # Write to JSON
    output_path = RAW_DIR / "people_bicycle.json"
    write_json(output_path, rows)

    # Extract date range from crash_date field
    dates = [row.get("crash_date") for row in rows if row.get("crash_date")]
    if dates:
        dates_sorted = sorted(dates)
        min_date = dates_sorted[0]
        max_date = dates_sorted[-1]
        print(f"people_bicycle: {len(rows)} rows, {min_date}..{max_date}")
    else:
        print(f"people_bicycle: {len(rows)} rows")


if __name__ == "__main__":
    main()
