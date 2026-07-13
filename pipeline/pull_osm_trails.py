"""Pull named off-street trails from the OpenStreetMap Overpass API.

CDOT's Bike Routes layer is on-street only, so the Lakefront Trail, 312 RiverRun,
North Shore Channel Trail, North Branch Trail (and peers) never appear. This
fetches named off-street ways from OSM and archives the raw Overpass response to
pipeline/raw/osm_trails.json untouched; build_osm_trails() in aggregate.py groups
them by name, assigns ids/lengths, and tags the crowdsourced tier — same
pull-archives / aggregate-shapes split as pull_mellow.py.

Like pull_mellow.py this is a single third-party service with no uptime SLA, so a
failure here is non-fatal: it warns and leaves raw/osm_trails.json absent, and
aggregate.py falls back to the stub layer rather than failing the whole run.
"""
import argparse
import sys

import requests

from config import OVERPASS_API_URL, OSM_TRAILS_QUERY, OSM_USER_AGENT, RAW_DIR
from socrata import write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull named off-street trails from the OSM Overpass API.")
    parser.parse_args()

    try:
        resp = requests.post(OVERPASS_API_URL, data={"data": OSM_TRAILS_QUERY},
                             headers={"User-Agent": OSM_USER_AGENT}, timeout=120)
        resp.raise_for_status()
        payload = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"WARNING: OSM trails pull failed ({exc}) — osm_trails.geojson will "
              f"ship as a stub this run. See CONTRIBUTING.md.", file=sys.stderr)
        return

    output_path = RAW_DIR / "osm_trails.json"
    write_json(output_path, payload)
    print(f"Element count: {len(payload.get('elements', []))}")


if __name__ == "__main__":
    main()
