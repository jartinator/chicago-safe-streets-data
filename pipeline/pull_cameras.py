"""Pull speed-camera and red-light-camera violation records from Chicago Socrata.

Aggregates daily violation records per camera into a summary with total violations
and date range. Camera data is a sparse proxy for aggressive driving, biased toward
camera locations — published downstream with data_tier "proxy".

Each dataset has one row per camera per day with a violation count. Columns differ
slightly: speed cameras use "address" while red-light cameras use "intersection".
Aggregates in Python to one record per camera, using the most recent non-null
lat/lng seen for each camera. Saves results to pipeline/raw/cameras.json.

Idempotent: re-running overwrites cleanly. Exit code 1 if no rows fetched.
"""
import argparse
import sys
from collections import defaultdict
from datetime import datetime

from config import DATASETS, RAW_DIR
from socrata import fetch_all, write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull camera violation data from Chicago Data Portal."
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Filter to violations on or after this date (YYYY-MM-DD format)",
    )
    args = parser.parse_args()

    # Build where clause for optional date filter
    where_clause = None
    if args.since:
        where_clause = f"violation_date >= '{args.since}'"

    # Aggregate cameras by camera_id
    cameras = {}  # camera_id -> dict with aggregated data
    total_violations = 0
    all_dates = []

    # Pull speed cameras
    dataset_id = DATASETS["speed_cameras"]
    print(
        f"Fetching speed cameras: {dataset_id}",
        file=sys.stderr,
    )
    select = "address,camera_id,violation_date,violations,latitude,longitude"
    for row in fetch_all(dataset_id, select=select, where=where_clause):
        camera_id = row.get("camera_id")
        if not camera_id:
            continue

        key = (camera_id, "speed")
        if key not in cameras:
            cameras[key] = {
                "camera_id": camera_id,
                "kind": "speed",
                "address": row.get("address"),
                "lat": None,
                "lng": None,
                "violations_total": 0,
                "first_date": None,
                "last_date": None,
            }

        # Accumulate violations
        violations_count = row.get("violations")
        if violations_count:
            try:
                cameras[key]["violations_total"] += int(violations_count)
                total_violations += int(violations_count)
            except (ValueError, TypeError):
                pass

        # Track date range
        violation_date = row.get("violation_date")
        if violation_date:
            all_dates.append(violation_date)
            # Update first/last dates
            if not cameras[key]["first_date"] or violation_date < cameras[key]["first_date"]:
                cameras[key]["first_date"] = violation_date
            if not cameras[key]["last_date"] or violation_date > cameras[key]["last_date"]:
                cameras[key]["last_date"] = violation_date

        # Keep most recent non-null lat/lng
        lat = row.get("latitude")
        lng = row.get("longitude")
        if lat is not None and lng is not None:
            try:
                cameras[key]["lat"] = float(lat)
                cameras[key]["lng"] = float(lng)
            except (ValueError, TypeError):
                pass

    # Pull red-light cameras
    dataset_id = DATASETS["red_light_cameras"]
    print(
        f"Fetching red-light cameras: {dataset_id}",
        file=sys.stderr,
    )
    select = "intersection,camera_id,violation_date,violations,latitude,longitude"
    for row in fetch_all(dataset_id, select=select, where=where_clause):
        camera_id = row.get("camera_id")
        if not camera_id:
            continue

        key = (camera_id, "red_light")
        if key not in cameras:
            cameras[key] = {
                "camera_id": camera_id,
                "kind": "red_light",
                "address": row.get("intersection"),
                "lat": None,
                "lng": None,
                "violations_total": 0,
                "first_date": None,
                "last_date": None,
            }

        # Accumulate violations
        violations_count = row.get("violations")
        if violations_count:
            try:
                cameras[key]["violations_total"] += int(violations_count)
                total_violations += int(violations_count)
            except (ValueError, TypeError):
                pass

        # Track date range
        violation_date = row.get("violation_date")
        if violation_date:
            all_dates.append(violation_date)
            # Update first/last dates
            if not cameras[key]["first_date"] or violation_date < cameras[key]["first_date"]:
                cameras[key]["first_date"] = violation_date
            if not cameras[key]["last_date"] or violation_date > cameras[key]["last_date"]:
                cameras[key]["last_date"] = violation_date

        # Keep most recent non-null lat/lng
        lat = row.get("latitude")
        lng = row.get("longitude")
        if lat is not None and lng is not None:
            try:
                cameras[key]["lat"] = float(lat)
                cameras[key]["lng"] = float(lng)
            except (ValueError, TypeError):
                pass

    if not cameras:
        print("cameras: 0 rows")
        sys.exit(1)

    # Convert to list and sort by camera_id for determinism
    camera_list = sorted(cameras.values(), key=lambda x: (x["kind"], x["camera_id"]))

    # Write to JSON
    output_path = RAW_DIR / "cameras.json"
    write_json(output_path, camera_list)

    # Compute summary statistics
    speed_count = sum(1 for c in camera_list if c["kind"] == "speed")
    red_light_count = sum(1 for c in camera_list if c["kind"] == "red_light")

    min_date = max_date = None
    if all_dates:
        all_dates_sorted = sorted(all_dates)
        min_date = all_dates_sorted[0]
        max_date = all_dates_sorted[-1]

    date_range = f"{min_date}..{max_date}" if min_date else "N/A"

    # Summary line
    print(
        f"cameras: {speed_count} speed, {red_light_count} red-light, "
        f"{total_violations} violations, {date_range}"
    )


if __name__ == "__main__":
    main()
