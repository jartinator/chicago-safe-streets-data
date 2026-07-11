"""Pull cyclist-involved crashes from Traffic Crashes - Crashes dataset.

Reads crash_record_id values from pipeline/raw/people_bicycle.json (output of pull_people.py),
dedupes them, and fetches the full crash records for those ids from Socrata.
Saves results to pipeline/raw/crashes_cyclist.json.

Idempotent: re-running overwrites cleanly. Exit code 1 if no rows fetched or input missing.
"""
import argparse
import json
import sys

from config import DATASETS, RAW_DIR
from socrata import fetch_by_ids, write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull Traffic Crashes - Crashes data for cyclist-involved incidents."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit to N crash_record_ids for smoke-testing (default: all)",
    )
    args = parser.parse_args()

    # Read crash_record_ids from people_bicycle.json
    people_path = RAW_DIR / "people_bicycle.json"
    if not people_path.exists():
        print(
            f"Error: {people_path} not found. Run pull_people.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(people_path) as f:
        people_rows = json.load(f)

    # Extract and dedupe crash_record_ids
    ids = set()
    for row in people_rows:
        crash_id = row.get("crash_record_id")
        if crash_id:
            ids.add(crash_id)

    ids = sorted(ids)
    if args.limit:
        ids = ids[: args.limit]

    if not ids:
        print("crashes_cyclist: 0 ids to fetch")
        sys.exit(1)

    # Select exactly these columns
    select = (
        "crash_record_id,crash_date,latitude,longitude,"
        "most_severe_injury,injuries_fatal,injuries_incapacitating,"
        "injuries_non_incapacitating,injuries_reported_not_evident,"
        "first_crash_type,crash_type,prim_contributory_cause,"
        "lighting_condition,weather_condition,roadway_surface_cond,"
        "posted_speed_limit,traffic_control_device,hit_and_run_i,"
        "dooring_i,street_no,street_direction,street_name"
    )

    # Fetch crash records for those ids
    dataset_id = DATASETS["crashes"]
    print(f"Fetching crashes_cyclist: {dataset_id} ({len(ids)} ids)", file=sys.stderr)
    rows = list(fetch_by_ids(dataset_id, "crash_record_id", ids, select=select))

    if not rows:
        print(f"crashes_cyclist: 0 rows")
        sys.exit(1)

    # Write to JSON
    output_path = RAW_DIR / "crashes_cyclist.json"
    write_json(output_path, rows)

    # Extract date range and count missing lat/lon
    dates = [row.get("crash_date") for row in rows if row.get("crash_date")]
    min_date = max_date = None
    if dates:
        dates_sorted = sorted(dates)
        min_date = dates_sorted[0]
        max_date = dates_sorted[-1]

    missing_geo = sum(
        1 for row in rows
        if not row.get("latitude") or not row.get("longitude")
    )

    # Summary line
    date_range = f"{min_date}..{max_date}" if min_date else "N/A"
    print(
        f"crashes_cyclist: {len(ids)} ids, {len(rows)} rows, {date_range}, "
        f"{missing_geo} missing lat/lon"
    )


if __name__ == "__main__":
    main()
