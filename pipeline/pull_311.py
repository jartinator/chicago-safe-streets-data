"""Pull bike-related 311 service requests from the unified Chicago 311 dataset.

311 is a self-report proxy, biased toward wards with engaged 311 users — published
downstream with data_tier "proxy".

Fetches all service requests from the unified 311 dataset (v6vf-nfxy, Dec 2018-)
matching bike-related type substrings (BIKE, BICYCLE), saves results to
pipeline/raw/sr311_bike.json.

Idempotent: re-running overwrites cleanly. Exit code 1 if no rows fetched.

Use --list-types to inspect the live sr_type taxonomy and see counts for types
matching the bike substrings, without fetching rows.
"""
import argparse
import sys
from datetime import datetime

from config import DATASETS, RAW_DIR, SR311_TYPE_SUBSTRINGS, SR311_START_DATE
from socrata import fetch_all, write_json


def build_where_clause(type_substrings, since_date):
    """Build a SoQL where clause for bike-related 311 requests.

    Args:
        type_substrings: list of strings to match (case-insensitive) in sr_type
        since_date: ISO date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)

    Returns:
        SoQL where clause string
    """
    # Build OR'd LIKE conditions for each substring
    or_conditions = " OR ".join(
        f"upper(sr_type) like '%{sub.upper()}%'"
        for sub in type_substrings
    )

    # Combine with date filter
    where = f"({or_conditions}) AND created_date >= '{since_date}T00:00:00'"
    return where


def list_types(type_substrings):
    """Query and print sr_type taxonomy for bike-related requests, grouped with counts."""
    dataset_id = DATASETS["sr311"]

    # Query sr_type with counts, no date filter
    select = "sr_type,count(sr_number)"
    group = "sr_type"

    # Build where clause for type filtering only (no date filter for list)
    or_conditions = " OR ".join(
        f"upper(sr_type) like '%{sub.upper()}%'"
        for sub in type_substrings
    )
    where = f"({or_conditions})"

    print(f"Querying sr_type taxonomy matching {type_substrings}...", file=sys.stderr)

    rows = list(fetch_all(dataset_id, select=select, where=where, group=group, log=None))

    if not rows:
        print("No matching sr_type found")
        return

    # Sort by count descending, then by sr_type
    rows_sorted = sorted(
        rows,
        key=lambda r: (-int(r.get("count_sr_number", 0)), r.get("sr_type", ""))
    )

    for row in rows_sorted:
        sr_type = row.get("sr_type", "")
        count = row.get("count_sr_number", 0)
        print(f"  {sr_type}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Pull bike-related 311 Service Requests from Chicago Data Portal."
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Override start date (YYYY-MM-DD format, default from config)",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="Query and list all sr_type values matching bike substrings with counts, then exit",
    )
    args = parser.parse_args()

    if args.list_types:
        list_types(SR311_TYPE_SUBSTRINGS)
        sys.exit(0)

    # Determine start date
    since_date = args.since if args.since else SR311_START_DATE

    # Validate date format
    try:
        datetime.strptime(since_date, "%Y-%m-%d")
    except ValueError:
        print(f"Error: --since must be in YYYY-MM-DD format, got {since_date}", file=sys.stderr)
        sys.exit(1)

    # Build where clause
    where = build_where_clause(SR311_TYPE_SUBSTRINGS, since_date)

    # Select exactly these columns
    select = (
        "sr_number,sr_type,created_date,status,closed_date,"
        "street_address,ward,community_area,latitude,longitude"
    )

    dataset_id = DATASETS["sr311"]
    print(f"Fetching sr311_bike: {dataset_id}", file=sys.stderr)
    rows = list(fetch_all(dataset_id, select=select, where=where))

    if not rows:
        print("sr311_bike: 0 rows")
        sys.exit(1)

    # Write to JSON
    output_path = RAW_DIR / "sr311_bike.json"
    write_json(output_path, rows)

    # Extract distinct sr_type values
    sr_types = set()
    for row in rows:
        sr_type = row.get("sr_type")
        if sr_type:
            sr_types.add(sr_type)

    distinct_types = len(sr_types)

    # Extract date range
    dates = [row.get("created_date") for row in rows if row.get("created_date")]
    min_date = max_date = None
    if dates:
        dates_sorted = sorted(dates)
        min_date = dates_sorted[0]
        max_date = dates_sorted[-1]

    # Summary line: rows pulled, distinct sr_type count, min/max created_date
    date_range = f"{min_date}..{max_date}" if min_date else "N/A"
    print(f"sr311_bike: {len(rows)} rows, {distinct_types} distinct types, {date_range}")


if __name__ == "__main__":
    main()
