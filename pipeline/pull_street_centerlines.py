"""Pull the Street Center Lines layer from the Chicago Data Portal.

Fetches the tabular Socrata copy (pr57-gg9e, "transportation") — the canonical
6imu-meau map view returns empty SODA rows and a truncated geospatial export
(verified 2026-07-12) — paging the SODA rows with a slim $select and archiving
them as a GeoJSON FeatureCollection at raw/street_centerlines.geojson.
Class/status filtering is mapped downstream (aggregate.py); this module only
fetches and archives.

Idempotent: re-running overwrites cleanly. Exit code 1 if no rows fetched.
"""
import argparse
import sys
from collections import Counter

from config import DATASETS, RAW_DIR
from socrata import fetch_all, write_json

SELECT = "trans_id,the_geom,class,status,street_nam,street_typ,pre_dir,length"


def main():
    parser = argparse.ArgumentParser(
        description="Pull Chicago street center lines from the Chicago Data Portal."
    )
    parser.parse_args()

    feats = []
    classes = Counter()
    dataset_id = DATASETS["street_centerlines"]
    print(f"Fetching street_centerlines: {dataset_id}", file=sys.stderr)
    for row in fetch_all(dataset_id, select=SELECT, order=":id"):
        geom = row.get("the_geom")
        if not geom:
            continue
        props = {k: v for k, v in row.items() if k != "the_geom"}
        feats.append({"type": "Feature", "geometry": geom, "properties": props})
        classes[row.get("class") or "(blank)"] += 1

    if not feats:
        print("street_centerlines: 0 features")
        sys.exit(1)

    write_json(RAW_DIR / "street_centerlines.geojson",
               {"type": "FeatureCollection", "features": feats})
    hist = ", ".join(f"{c}:{n}" for c, n in sorted(classes.items()))
    print(f"street_centerlines: {len(feats)} segments; class counts: {hist}")


if __name__ == "__main__":
    main()
