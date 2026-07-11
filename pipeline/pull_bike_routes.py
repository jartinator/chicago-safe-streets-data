"""Pull the CDOT Bike Routes line layer from Chicago Data Portal Socrata dataset.

Fetches the complete bike routes geometry (hvv9-38ut) as GeoJSON and saves to
pipeline/raw/bike_routes.geojson with all properties intact. The facility-type
taxonomy is mapped downstream; this module only fetches and archives.
"""
import argparse
from config import DATASETS, RAW_DIR
from socrata import fetch_geojson, write_json


def main():
    """Fetch and save bike routes, printing feature count and facility type summary."""
    parser = argparse.ArgumentParser(
        description="Pull CDOT Bike Routes from Chicago Data Portal."
    )
    parser.parse_args()

    # Fetch the bike routes GeoJSON
    dataset_id = DATASETS["bike_routes"]
    geojson = fetch_geojson(dataset_id)

    # Save to raw directory
    output_path = RAW_DIR / "bike_routes.geojson"
    write_json(output_path, geojson)

    # Print summary
    features = geojson.get("features", [])
    feature_count = len(features)

    # Find the facility/route type property (case-insensitive search)
    facility_type_key = None
    facility_types = set()

    if features:
        first_feature = features[0]
        properties = first_feature.get("properties", {})

        # Check for facility/route type keys (case-insensitive)
        for candidate_key in ["displayroute", "displayrou", "bikeroute", "type"]:
            for actual_key in properties.keys():
                if actual_key.lower() == candidate_key.lower():
                    facility_type_key = actual_key
                    break
            if facility_type_key:
                break

        # Collect all distinct values for this key
        if facility_type_key:
            for feature in features:
                props = feature.get("properties", {})
                if facility_type_key in props:
                    facility_types.add(props[facility_type_key])

    # Print summary line
    if facility_type_key:
        distinct_types = ", ".join(sorted(facility_types))
        print(f"Feature count: {feature_count}, facility types: {distinct_types}")
    else:
        print(f"Feature count: {feature_count}, facility type property not found")


if __name__ == "__main__":
    main()
