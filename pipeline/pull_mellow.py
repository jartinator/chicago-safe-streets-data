"""Pull the Mellow Bike Map crowdsourced low-stress-route layer.

Fetches the public GeoJSON export from mellowbikemap.com (the open-source
jeancochrane/mellow-bike-map project, MIT licensed) and saves it to
pipeline/raw/mellow_routes.geojson untouched. The API returns bare
MultiLineString geometry with no properties; exploding into per-segment
LineStrings and assigning the crowdsourced data_tier happens in aggregate.py,
same split as pull_bike_routes.py/aggregate.py.

Unlike the Socrata pulls, this is a single small third-party app with no
uptime guarantee, so a failure here is non-fatal: it warns and leaves
raw/mellow_routes.geojson absent, and aggregate.py falls back to the stub
layer rather than failing the whole pipeline run.
"""
import argparse
import sys

import requests

from config import MELLOW_API_URL, RAW_DIR
from socrata import write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull the Mellow Bike Map route layer from mellowbikemap.com."
    )
    parser.parse_args()

    try:
        resp = requests.get(MELLOW_API_URL, timeout=60)
        resp.raise_for_status()
        geojson = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"WARNING: mellow pull failed ({exc}) — mellow_routes.geojson will "
              f"ship as a stub this run. See DECISIONS.md.", file=sys.stderr)
        return

    output_path = RAW_DIR / "mellow_routes.geojson"
    write_json(output_path, geojson)
    print(f"Feature count: {len(geojson.get('features', []))}")


if __name__ == "__main__":
    main()
