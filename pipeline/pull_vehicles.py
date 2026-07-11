"""Pull vehicle units from Traffic Crashes - Vehicles dataset for cyclist-involved crashes.

Reads pipeline/raw/people_bicycle.json (crash_record_id list from prior cyclist data pull),
dedupes the crash IDs, fetches matching vehicle/unit records from the Vehicles dataset
(id 68nd-jvt3), and saves to pipeline/raw/vehicles_cyclist.json.

Idempotent: re-running overwrites cleanly. Exit code 1 if file missing or no rows fetched.
"""
import argparse
import json
import sys
from collections import Counter

from config import DATASETS, RAW_DIR
from socrata import fetch_by_ids, write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull vehicle units involved in cyclist crashes from Socrata."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of crash IDs to fetch (for smoke-testing)",
    )
    args = parser.parse_args()

    # Read crash_record_id list from prior people_bicycle pull
    input_path = RAW_DIR / "people_bicycle.json"
    if not input_path.exists():
        print(f"vehicles_cyclist: ERROR - {input_path} not found. Run pull_people.py first.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path) as f:
            people_rows = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"vehicles_cyclist: ERROR - Failed to read {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not people_rows:
        print("vehicles_cyclist: ERROR - people_bicycle.json is empty. Run pull_people.py first.", file=sys.stderr)
        sys.exit(1)

    # Extract and dedupe crash_record_id values
    crash_ids = set()
    for row in people_rows:
        if "crash_record_id" in row and row["crash_record_id"]:
            crash_ids.add(row["crash_record_id"])

    if not crash_ids:
        print("vehicles_cyclist: ERROR - No crash_record_id values found in people_bicycle.json.", file=sys.stderr)
        sys.exit(1)

    crash_ids = list(crash_ids)

    # Apply --limit if requested (for smoke-testing)
    if args.limit:
        crash_ids = crash_ids[:args.limit]

    # Select exactly these columns
    select = "crash_record_id,unit_no,unit_type,vehicle_type,make,model,vehicle_year,travel_direction,maneuver,first_contact_point"

    # Fetch matching vehicle records by crash_record_id
    dataset_id = DATASETS["vehicles"]
    print(f"Fetching vehicles_cyclist for {len(crash_ids)} crash IDs from {dataset_id}", file=sys.stderr)
    rows = list(fetch_by_ids(dataset_id, "crash_record_id", crash_ids, select=select))

    if not rows:
        print("vehicles_cyclist: 0 rows")
        sys.exit(1)

    # Write to JSON
    output_path = RAW_DIR / "vehicles_cyclist.json"
    write_json(output_path, rows)

    # Generate summary: top 3 unit_type breakdown
    unit_types = Counter(row.get("unit_type") for row in rows if row.get("unit_type"))
    top_3 = unit_types.most_common(3)
    breakdown = ", ".join(f"{unit_type}: {count}" for unit_type, count in top_3)

    print(f"vehicles_cyclist: {len(crash_ids)} ids requested, {len(rows)} rows returned ({breakdown})")


if __name__ == "__main__":
    main()
