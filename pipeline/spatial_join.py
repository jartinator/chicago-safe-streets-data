"""Join cyclist crash points to their containing ward and nearest bikeway segment.

The spatial join is the backbone of every drill-down view (ward -> corridor ->
intersection). Method per the frozen design:
- geopandas; project to EPSG:26916 (UTM 16N) for distance ops, publish EPSG:4326.
- Ward join: point-within-polygon.
- Bikeway join: sjoin_nearest with max_distance=NEAREST_SEGMENT_MAX_DISTANCE_M (30 m);
  crashes beyond the threshold keep segment_id = null.

Inputs (from pull_* modules or make_fixtures.py):
  raw/crashes_cyclist.json, raw/wards.geojson, raw/bike_routes.geojson
Output:
  raw/crashes_joined.json — crash rows + {ward, segment_id, seg_distance_m}

Usage: python spatial_join.py
"""
import argparse
import json
import sys

import geopandas as gpd
from shapely.geometry import Point

from config import RAW_DIR, METRIC_CRS, OUTPUT_CRS, NEAREST_SEGMENT_MAX_DISTANCE_M
from socrata import write_json


def _first_key(props, candidates):
    lower = {k.lower(): k for k in props}
    for c in candidates:
        if c in lower:
            return lower[c]
    return None


def load_routes():
    gj = json.loads((RAW_DIR / "bike_routes.geojson").read_text())
    gdf = gpd.GeoDataFrame.from_features(gj["features"], crs=OUTPUT_CRS)
    props = gj["features"][0]["properties"] if gj["features"] else {}
    id_key = _first_key(props, ["objectid", "objectid_1", "segment_id", "id"])
    gdf["segment_id"] = (gdf[id_key].astype(str) if id_key
                         else [str(i + 1) for i in range(len(gdf))])
    return gdf[["segment_id", "geometry"]]


def load_wards():
    gj = json.loads((RAW_DIR / "wards.geojson").read_text())
    gdf = gpd.GeoDataFrame.from_features(gj["features"], crs=OUTPUT_CRS)
    props = gj["features"][0]["properties"] if gj["features"] else {}
    ward_key = _first_key(props, ["ward", "ward_id"])
    if not ward_key:
        sys.exit("wards.geojson has no ward/ward_id property")
    gdf["ward"] = gdf[ward_key].astype(str)
    return gdf[["ward", "geometry"]]


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()

    crashes = json.loads((RAW_DIR / "crashes_cyclist.json").read_text())
    total_in = len(crashes)
    located = [c for c in crashes if c.get("latitude") and c.get("longitude")]

    pts = gpd.GeoDataFrame(
        located,
        geometry=[Point(float(c["longitude"]), float(c["latitude"])) for c in located],
        crs=OUTPUT_CRS,
    )
    wards = load_wards()
    routes = load_routes()

    pts_m = pts.to_crs(METRIC_CRS)
    joined = gpd.sjoin(pts_m, wards.to_crs(METRIC_CRS), how="left", predicate="within")
    joined = joined.drop(columns=["index_right"])
    joined = gpd.sjoin_nearest(
        joined, routes.to_crs(METRIC_CRS), how="left",
        max_distance=NEAREST_SEGMENT_MAX_DISTANCE_M, distance_col="seg_distance_m",
    )
    # sjoin_nearest can duplicate a point equidistant to two segments; keep first.
    joined = joined[~joined.index.duplicated(keep="first")]

    out = []
    for _, row in joined.iterrows():
        rec = {k: row.get(k) for k in located[0].keys()}
        ward = row.get("ward")
        seg = row.get("segment_id")
        dist = row.get("seg_distance_m")
        rec["ward"] = None if ward is None or ward != ward else str(ward)
        rec["segment_id"] = None if seg is None or seg != seg else str(seg)
        rec["seg_distance_m"] = None if dist is None or dist != dist else round(float(dist), 1)
        out.append(rec)

    write_json(RAW_DIR / "crashes_joined.json", out)

    no_ward = sum(1 for r in out if not r["ward"])
    no_seg = sum(1 for r in out if not r["segment_id"])
    by_ward = {}
    for r in out:
        if r["ward"]:
            by_ward[r["ward"]] = by_ward.get(r["ward"], 0) + 1
    top5 = sorted(by_ward.items(), key=lambda kv: -kv[1])[:5]
    print(f"spatial_join: {total_in} crashes in, {len(out)} located and joined "
          f"({total_in - len(located)} missing coords)")
    print(f"  unmatched ward: {no_ward} ({100 * no_ward / max(len(out), 1):.1f}%), "
          f"beyond {NEAREST_SEGMENT_MAX_DISTANCE_M}m of any bikeway: {no_seg} "
          f"({100 * no_seg / max(len(out), 1):.1f}%)")
    print(f"  top-5 wards by crash count: {top5}")


if __name__ == "__main__":
    main()
