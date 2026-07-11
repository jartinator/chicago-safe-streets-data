"""Pull Chicago ward boundary polygons (2023 remap) from Socrata as GeoJSON.

Fetches the full FeatureCollection from the Socrata dataset id configured in config.py
and saves to pipeline/raw/wards.geojson, preserving all properties.

Idempotent: re-running overwrites cleanly. Exit code 1 if no features fetched.

If the dataset id 404s, search the Chicago Data Portal for "Boundaries - Wards (2023-)"
and update the "wards" entry in DATASETS (config.py).
"""
import argparse
import sys

from config import DATASETS, RAW_DIR
from socrata import fetch_geojson, write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull Chicago ward boundaries (2023) from Socrata."
    )
    parser.parse_args()

    # Fetch the full GeoJSON FeatureCollection
    dataset_id = DATASETS["wards"]
    print(f"Fetching wards: {dataset_id}", file=sys.stderr)
    geojson = fetch_geojson(dataset_id)

    features = geojson.get("features", [])
    if not features:
        print("wards: 0 features")
        sys.exit(1)

    # Write to GeoJSON
    output_path = RAW_DIR / "wards.geojson"
    write_json(output_path, geojson)

    # Check for ward-number property on first feature (case-insensitive key check)
    first_feature = features[0]
    properties = first_feature.get("properties", {})
    prop_keys_lower = {k.lower(): k for k in properties.keys()}
    has_ward_number = "ward" in prop_keys_lower or "ward_id" in prop_keys_lower

    # Build summary line
    count = len(features)
    ward_msg = "ward number property found" if has_ward_number else "NO ward number property"
    summary = f"wards: {count} features, {ward_msg}"

    # Add warning if count != 50
    if count != 50:
        summary += f" WARNING: expected 50 wards — dataset id may have changed, see config.py"

    print(summary)


if __name__ == "__main__":
    main()
