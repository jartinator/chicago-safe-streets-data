"""One-shot live refresh of the road-coverage metrics from committed site data.

Pulls ONLY the street centerline layer (pull_street_centerlines.py) and joins
it against the already-committed bike_routes.geojson / wards.geojson, so the
coverage numbers (road_network.json, the per-ward coverage fields in
ward_safety_index.json, meta.json's street_centerlines source) can publish
without a multi-hour full pipeline run. All numbers come from the exact same
aggregate.py functions as the live path — no logic drift. The weekly
`python run_all.py` recomputes everything from scratch and remains canonical.

Run refresh_reporting.py AFTER this script — it rebuilds findings.json from
the road_network.json written here.

Provenance guard: same as refresh_reporting — refuses to touch fixture data.

Usage: python refresh_coverage.py [--skip-pull]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

from aggregate import (build_road_network, load_street_centerlines,
                       ward_bikeway_miles_by_category, ward_coverage_fields)
from config import RAW_DIR, SITE_DATA_DIR, CONTRACT_VERSION, OUTPUT_CRS
from refresh_reporting import guard_provenance
from socrata import write_json

HERE = Path(__file__).resolve().parent


def _load(name):
    return json.loads((SITE_DATA_DIR / name).read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skip-pull", action="store_true",
                    help="reuse an existing raw/street_centerlines.geojson")
    args = ap.parse_args()

    guard_provenance(_load("meta.json"))

    if not (args.skip_pull and (RAW_DIR / "street_centerlines.geojson").exists()):
        subprocess.run([sys.executable, str(HERE / "pull_street_centerlines.py")],
                       cwd=HERE, check=True)

    streets_gdf = load_street_centerlines()
    if streets_gdf is None:
        raise SystemExit("refresh_coverage: no usable street centerlines")

    routes_gj = _load("bike_routes.geojson")
    wards_gj = _load("wards.geojson")
    wards_gdf = gpd.GeoDataFrame.from_features(wards_gj["features"], crs=OUTPUT_CRS)
    wards_gdf["ward"] = wards_gdf["ward"].astype(str)
    wards_gdf = wards_gdf[["ward", "geometry"]]

    as_of = datetime.now(timezone.utc).date().isoformat()
    road_network = build_road_network(streets_gdf, wards_gdf, routes_gj, as_of)
    write_json(SITE_DATA_DIR / "road_network.json", road_network)

    road_miles = {r["ward"]: r["road_miles"] for r in road_network["wards"]}
    cats_by_ward = ward_bikeway_miles_by_category(routes_gj, wards_gdf)

    wsi = _load("ward_safety_index.json")
    for rec in wsi["wards"]:
        rec.update(ward_coverage_fields(cats_by_ward.get(rec["ward"], {}),
                                        road_miles.get(rec["ward"])))
    write_json(SITE_DATA_DIR / "ward_safety_index.json", wsi)

    meta = _load("meta.json")
    meta["contract_version"] = CONTRACT_VERSION
    entry = {"id": "street_centerlines",
             "name": "Street Center Lines (surface-street grid)",
             "tier": "real", "records": int(len(streets_gdf)), "date_range": None}
    ids = [s.get("id") for s in meta["sources"]]
    if "street_centerlines" in ids:
        meta["sources"][ids.index("street_centerlines")] = entry
    else:  # same position as aggregate.py's list: right after bike_routes
        pos = ids.index("bike_routes") + 1 if "bike_routes" in ids else len(ids)
        meta["sources"].insert(pos, entry)
    write_json(SITE_DATA_DIR / "meta.json", meta)

    cw = road_network["citywide"]
    print(f"refresh_coverage: {cw['road_miles']} road mi, "
          f"{cw['onstreet_bikeway_miles']} on-street bikeway mi -> "
          f"{cw['pct_with_bike_infra']}% coverage across {len(road_miles)} wards")
    print("  now run: python refresh_reporting.py  (rebuilds findings.json)")


if __name__ == "__main__":
    main()
