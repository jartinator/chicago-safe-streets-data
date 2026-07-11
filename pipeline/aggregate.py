"""Aggregate joined data into the versioned static files the site consumes.

Reads raw/* (pull modules or fixtures) plus raw/crashes_joined.json (spatial_join.py)
and writes every contract file into site/data/. This module owns the published
schemas — see SCHEMA.md; do not add/rename output keys without bumping
CONTRACT_VERSION in config.py and updating SCHEMA.md.

Usage: python aggregate.py
"""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

import geopandas as gpd
from shapely.geometry import Point, shape

from config import (RAW_DIR, SITE_DATA_DIR, METRIC_CRS, OUTPUT_CRS,
                    FACILITY_CATEGORY_MAP, FACILITY_CATEGORIES,
                    INJURY_SEVERITY_MAP, CONTRACT_VERSION)
from socrata import write_json
from spatial_join import _first_key


def severity(rec):
    return INJURY_SEVERITY_MAP.get((rec.get("most_severe_injury") or "").upper(), "unknown")


def flag(rec, key):
    return (rec.get(key) or "").upper() == "Y"


def facility_category(raw_label, unmatched):
    cat = FACILITY_CATEGORY_MAP.get((raw_label or "").upper().strip())
    if cat is None:
        unmatched[raw_label or "(blank)"] += 1
        return "other"
    return cat


def tercile_bands(counts_by_key):
    vals = sorted(counts_by_key.values())
    if not vals:
        return {}
    lo = vals[max(0, len(vals) // 3 - 1)]
    hi = vals[max(0, 2 * len(vals) // 3 - 1)]
    return {k: ("low" if v <= lo else "medium" if v <= hi else "high")
            for k, v in counts_by_key.items()}


def build_crash_geojson(crashes):
    feats = []
    for c in crashes:
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point",
                         "coordinates": [round(float(c["longitude"]), 6),
                                         round(float(c["latitude"]), 6)]},
            "properties": {
                "crash_id": c["crash_record_id"],
                "date": c.get("crash_date"),
                "injury_severity": severity(c),
                "dooring": flag(c, "dooring_i"),
                "hit_and_run": flag(c, "hit_and_run_i"),
                "crash_type": c.get("first_crash_type"),
                "lighting": c.get("lighting_condition"),
                "street": " ".join(str(c.get(k) or "") for k in
                                   ("street_no", "street_direction", "street_name")).strip(),
                "ward": c.get("ward"),
                "segment_id": c.get("segment_id"),
                "data_tier": "real",
            },
        })
    return {"type": "FeatureCollection", "features": feats}


def build_routes(crashes):
    gj = json.loads((RAW_DIR / "bike_routes.geojson").read_text())
    gdf = gpd.GeoDataFrame.from_features(gj["features"], crs=OUTPUT_CRS)
    props = gj["features"][0]["properties"] if gj["features"] else {}
    id_key = _first_key(props, ["objectid", "objectid_1", "segment_id", "id"])
    street_key = _first_key(props, ["st_name", "street", "street_nam", "name"])
    type_key = _first_key(props, ["displayroute", "displayrou", "bikeroute", "type", "facility"])

    seg_crashes = Counter(c["segment_id"] for c in crashes if c.get("segment_id"))
    lengths = gdf.to_crs(METRIC_CRS).geometry.length

    unmatched = Counter()
    feats = []
    for i, (_, row) in enumerate(gdf.iterrows()):
        seg_id = str(row[id_key]) if id_key else str(i + 1)
        raw_type = str(row[type_key]) if type_key else ""
        feats.append({
            "type": "Feature",
            "geometry": row.geometry.__geo_interface__,
            "properties": {
                "segment_id": seg_id,
                "street": (str(row[street_key]) if street_key else "").upper(),
                "facility_type_raw": raw_type,
                "facility_category": facility_category(raw_type, unmatched),
                "length_m": round(float(lengths.iloc[i]), 1),
                "crashes_within_30m": seg_crashes.get(seg_id, 0),
                "data_tier": "real",
            },
        })
    if unmatched:
        print(f"  WARNING unmatched facility labels (mapped to 'other'): {dict(unmatched)}"
              " — extend FACILITY_CATEGORY_MAP in config.py")
    return {"type": "FeatureCollection", "features": feats}


def point_in_ward_counts(rows, wards_gdf):
    """Count arbitrary lat/lng rows per ward (for 311, which has unreliable ward fields)."""
    located = [r for r in rows if r.get("latitude") and r.get("longitude")]
    if not located:
        return {}, []
    # Geometry-only frame: raw rows may carry their own (unreliable) "ward" key,
    # which must not collide with the ward polygons' column in the join.
    pts = gpd.GeoDataFrame(
        geometry=[Point(float(r["longitude"]), float(r["latitude"])) for r in located],
        crs=OUTPUT_CRS,
    )
    joined = gpd.sjoin(pts.to_crs(METRIC_CRS), wards_gdf.to_crs(METRIC_CRS),
                       how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")]
    counts = Counter()
    tagged = []
    for (_, row), rec in zip(joined.iterrows(), located):
        w = row.get("ward")
        w = None if w is None or w != w else str(w)
        if w:
            counts[w] += 1
        tagged.append((w, rec))
    return dict(counts), tagged


def build_wards(crashes, sr311_by_ward):
    gj = json.loads((RAW_DIR / "wards.geojson").read_text())
    gdf = gpd.GeoDataFrame.from_features(gj["features"], crs=OUTPUT_CRS)
    props = gj["features"][0]["properties"] if gj["features"] else {}
    ward_key = _first_key(props, ["ward", "ward_id"])

    per_ward = defaultdict(lambda: {"crashes": 0, "injuries": 0, "fatalities": 0})
    for c in crashes:
        w = c.get("ward")
        if not w:
            continue
        sev = severity(c)
        per_ward[w]["crashes"] += 1
        if sev in ("fatal", "incapacitating", "non_incapacitating"):
            per_ward[w]["injuries"] += 1
        if sev == "fatal":
            per_ward[w]["fatalities"] += 1

    bands = tercile_bands({w: v["crashes"] for w, v in per_ward.items()})
    feats = []
    for _, row in gdf.iterrows():
        w = str(row[ward_key])
        stats = per_ward.get(w, {"crashes": 0, "injuries": 0, "fatalities": 0})
        feats.append({
            "type": "Feature",
            "geometry": row.geometry.__geo_interface__,
            "properties": {
                "ward": w,
                "alderman": None,  # see aldermen.json — filled from official lookup, never invented
                "cyclist_crashes": stats["crashes"],
                "injuries": stats["injuries"],
                "fatalities": stats["fatalities"],
                "complaints_311": sr311_by_ward.get(w, 0),
                "density_band": bands.get(w, "low"),
                "data_tier": "real",
            },
        })
    return {"type": "FeatureCollection", "features": feats}, gdf.assign(ward=gdf[ward_key].astype(str))[["ward", "geometry"]]


def build_corridors(routes_gj, crashes):
    by_street = defaultdict(lambda: {"segments": 0, "length_m": 0.0, "crashes": 0,
                                     "facility_mix": Counter()})
    seg_street = {}
    for f in routes_gj["features"]:
        p = f["properties"]
        street = p["street"] or "(unnamed)"
        d = by_street[street]
        d["segments"] += 1
        d["length_m"] += p["length_m"]
        d["facility_mix"][p["facility_category"]] += p["length_m"]
        seg_street[p["segment_id"]] = street
    for c in crashes:
        street = seg_street.get(c.get("segment_id"))
        if street:
            by_street[street]["crashes"] += 1
    out = []
    for street, d in by_street.items():
        km = d["length_m"] / 1000
        out.append({
            "street": street,
            "segments": d["segments"],
            "length_m": round(d["length_m"], 1),
            "crashes": d["crashes"],
            "crashes_per_km": round(d["crashes"] / km, 2) if km >= 0.2 else None,
            "facility_mix": {k: round(v, 1) for k, v in d["facility_mix"].items()},
            "data_tier": "real",
        })
    out.sort(key=lambda r: -(r["crashes_per_km"] or 0))
    return out


def build_intersections(crashes, cell_m=100):
    """Grid-cluster crash points (~cell_m cells) and emit the top hotspots."""
    cells = defaultdict(list)
    for c in crashes:
        lat, lng = float(c["latitude"]), float(c["longitude"])
        key = (round(lat * 111_320 / cell_m), round(lng * 83_000 / cell_m))
        cells[key].append(c)
    out = []
    for recs in cells.values():
        if len(recs) < 2:
            continue
        lat = sum(float(r["latitude"]) for r in recs) / len(recs)
        lng = sum(float(r["longitude"]) for r in recs) / len(recs)
        streets = Counter((r.get("street_name") or "").strip() for r in recs)
        label = streets.most_common(1)[0][0] or "unnamed"
        out.append({"lat": round(lat, 6), "lng": round(lng, 6),
                    "label": f"near {label.title()}", "crashes": len(recs),
                    "data_tier": "real"})
    out.sort(key=lambda r: -r["crashes"])
    return out[:25]


def build_findings(crashes, routes_gj, corridors, wards_gj):
    findings = []
    cat_len = Counter()
    cat_crashes = Counter()
    for f in routes_gj["features"]:
        p = f["properties"]
        cat_len[p["facility_category"]] += p["length_m"]
        cat_crashes[p["facility_category"]] += p["crashes_within_30m"]
    per_km = {c: (cat_crashes[c] / (cat_len[c] / 1000)) for c in cat_len if cat_len[c] > 500}
    if "painted" in per_km and "protected" in per_km and per_km["protected"] > 0:
        ratio = per_km["painted"] / per_km["protected"]
        findings.append({
            "id": "painted-vs-protected",
            "title": "Crash density: painted vs. protected lanes",
            "stat": f"{ratio:.1f}x",
            "description": (f"Painted-only bike lanes see {per_km['painted']:.1f} cyclist crashes "
                            f"per km vs {per_km['protected']:.1f} on protected lanes — "
                            f"{ratio:.1f}x the density, raw counts not normalized by ridership."),
            "caveat": "Raw counts overrepresent high-traffic corridors; no volume normalization. "
                      "Dooring crashes are undercounted citywide.",
            "map_state": {"screen": "map", "layers": ["crashes", "infrastructure"], "filters": {}},
            "data_tier": "real",
        })
    top = [c for c in corridors if c["crashes_per_km"]][:5]
    if top:
        findings.append({
            "id": "top-corridors",
            "title": "Highest crash-density corridors",
            "stat": top[0]["street"].title(),
            "description": "Top corridors by cyclist crashes per km of bikeway: " +
                           "; ".join(f"{c['street'].title()} ({c['crashes_per_km']}/km)" for c in top) + ".",
            "caveat": "Raw counts, not normalized by bike volume. Dooring is undercounted.",
            "map_state": {"screen": "map", "layers": ["crashes", "infrastructure"],
                          "corridor": top[0]["street"], "filters": {}},
            "data_tier": "real",
        })
    ward_counts = {f["properties"]["ward"]: f["properties"]["cyclist_crashes"]
                   for f in wards_gj["features"]}
    total = sum(ward_counts.values())
    top_wards = sorted(ward_counts.items(), key=lambda kv: -kv[1])[:5]
    if total:
        share = 100 * sum(v for _, v in top_wards) / total
        findings.append({
            "id": "ward-concentration",
            "title": "Ward concentration",
            "stat": f"{share:.0f}%",
            "description": (f"5 of 50 wards account for {share:.0f}% of located cyclist crashes: "
                            + ", ".join(f"Ward {w} ({v})" for w, v in top_wards) + "."),
            "caveat": "Ward totals reflect where people ride most, not only where streets are worst.",
            "map_state": {"screen": "map", "layers": ["crashes", "wards"],
                          "ward": top_wards[0][0], "filters": {}},
            "data_tier": "real",
        })
    doorings = sum(1 for c in crashes if flag(c, "dooring_i"))
    findings.append({
        "id": "dooring-undercount",
        "title": "Dooring: the number that is too low",
        "stat": str(doorings),
        "description": (f"Only {doorings} crashes carry a dooring flag. Dooring is structurally "
                        "excluded from 'reportable' crash records unless damage/injury thresholds "
                        "are met, so true dooring risk — especially on painted-lane corridors — "
                        "is higher than any number on this site."),
        "caveat": "Structural undercount; treat as a floor, never a rate.",
        "map_state": {"screen": "map", "layers": ["crashes"], "filters": {"dooring": True}},
        "data_tier": "real",
    })
    vehicles_path = RAW_DIR / "vehicles_cyclist.json"
    if vehicles_path.exists():
        vt = Counter((v.get("vehicle_type") or "UNKNOWN")
                     for v in json.loads(vehicles_path.read_text()))
        vt.pop("UNKNOWN", None)
        top3 = vt.most_common(3)
        if top3:
            findings.append({
                "id": "vehicle-types",
                "title": "What cyclists collide with",
                "stat": top3[0][0].title(),
                "description": "Most common motor-vehicle unit types in cyclist crashes: " +
                               ", ".join(f"{k.title()} ({v})" for k, v in top3) + ".",
                "caveat": "Unit types as recorded by responding officers; fleet mix not normalized.",
                "map_state": {"screen": "table", "layers": [], "filters": {}},
                "data_tier": "real",
            })
    return findings


def build_mellow(raw_gj):
    """Tag Mellow Bike Map's features with segment ids, lengths, and data_tier.

    The public API returns one MultiLineString per route_type (sidewalk/street/
    route/path), each with thousands of parts — kept intact rather than exploded
    into individual LineStrings (that would mean tens of thousands of separate
    Leaflet layers). Leaflet natively draws a MultiLineString's nested coordinate
    array as one efficient multi-part polyline; network.js relies on that.
    """
    gdf = gpd.GeoDataFrame(geometry=[shape(f["geometry"]) for f in raw_gj["features"]],
                           crs=OUTPUT_CRS)
    lengths = gdf.to_crs(METRIC_CRS).geometry.length
    feats = []
    for f, geom, length in zip(raw_gj["features"], gdf.geometry, lengths):
        route_type = (f.get("properties") or {}).get("type") or "unknown"
        feats.append({
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "segment_id": f"mellow-{route_type}",
                "route_type": route_type,
                "length_m": round(float(length), 1),
                "data_tier": "crowdsourced",
            },
        })
    return {"type": "FeatureCollection", "features": feats}


def stub_layer(status_note):
    return {"type": "FeatureCollection", "features": [],
            "properties": {"status": "no_data_yet", "note": status_note}}


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    crashes = json.loads((RAW_DIR / "crashes_joined.json").read_text())
    provenance = ((RAW_DIR / "PROVENANCE").read_text().strip()
                  if (RAW_DIR / "PROVENANCE").exists() else "socrata")

    crash_gj = build_crash_geojson(crashes)
    routes_gj = build_routes(crashes)

    sr311 = json.loads((RAW_DIR / "sr311_bike.json").read_text())
    wards_raw = json.loads((RAW_DIR / "wards.geojson").read_text())
    wards_tmp = gpd.GeoDataFrame.from_features(wards_raw["features"], crs=OUTPUT_CRS)
    wkey = _first_key(wards_raw["features"][0]["properties"], ["ward", "ward_id"])
    wards_tmp["ward"] = wards_tmp[wkey].astype(str)
    sr311_by_ward, sr311_tagged = point_in_ward_counts(sr311, wards_tmp[["ward", "geometry"]])

    wards_gj, _ = build_wards(crashes, sr311_by_ward)
    corridors = build_corridors(routes_gj, crashes)
    intersections = build_intersections(crashes)
    findings = build_findings(crashes, routes_gj, corridors, wards_gj)

    ward_311 = defaultdict(lambda: {"total": 0, "by_type": Counter()})
    for w, rec in sr311_tagged:
        if w:
            ward_311[w]["total"] += 1
            ward_311[w]["by_type"][rec.get("sr_type") or "unknown"] += 1
    ward_311_out = {
        "data_tier": "proxy",
        "note": "311 requests are self-reported and biased toward wards with engaged 311 users.",
        "wards": [{"ward": w, "total": d["total"], "by_type": dict(d["by_type"])}
                  for w, d in sorted(ward_311.items(), key=lambda kv: -kv[1]["total"])],
    }

    cameras = json.loads((RAW_DIR / "cameras.json").read_text())
    cameras_out = {
        "data_tier": "proxy",
        "note": "Camera violations exist only at fixed camera locations — sparse and "
                "biased toward where cameras are installed, not where risk is highest.",
        "cameras": cameras,
    }

    mellow_raw_path = RAW_DIR / "mellow_routes.geojson"
    if mellow_raw_path.exists():
        mellow_gj = build_mellow(json.loads(mellow_raw_path.read_text()))
    else:
        mellow_gj = stub_layer(
            "Mellow Bike Map (crowdsourced low-stress streets) was not pulled this run "
            "(pull_mellow.py didn't run, or the source was unreachable). "
            "See CONTRIBUTING.md.")

    dates = sorted(c["date"] for c in (f["properties"] for f in crash_gj["features"]) if c["date"])
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_version": CONTRACT_VERSION,
        "provenance": provenance,
        "sources": [
            {"id": "crashes", "name": "Traffic Crashes (Crashes/People/Vehicles)",
             "tier": "real", "records": len(crash_gj["features"]),
             "date_range": [dates[0][:10], dates[-1][:10]] if dates else None},
            {"id": "bike_routes", "name": "CDOT Bike Routes", "tier": "real",
             "records": len(routes_gj["features"]), "date_range": None},
            {"id": "sr311", "name": "311 Service Requests (bike-related)", "tier": "proxy",
             "records": len(sr311), "date_range": None},
            {"id": "cameras", "name": "Speed/Red-light Camera Violations", "tier": "proxy",
             "records": len(cameras), "date_range": None},
            {"id": "obstructions", "name": "Bike-lane Obstructions", "tier": "mock",
             "records": None, "date_range": None},
        ] + ([{"id": "mellow_routes", "name": "Mellow Bike Map (crowdsourced low-stress streets)",
               "tier": "crowdsourced", "records": len(mellow_gj["features"]), "date_range": None}]
             if mellow_gj["features"] else []),
    }

    write_json(SITE_DATA_DIR / "crashes_cyclist.geojson", crash_gj)
    write_json(SITE_DATA_DIR / "bike_routes.geojson", routes_gj)
    write_json(SITE_DATA_DIR / "wards.geojson", wards_gj)
    write_json(SITE_DATA_DIR / "ward_311.json", ward_311_out)
    write_json(SITE_DATA_DIR / "cameras.json", cameras_out)
    write_json(SITE_DATA_DIR / "corridors.json", corridors)
    write_json(SITE_DATA_DIR / "intersections.json", intersections)
    write_json(SITE_DATA_DIR / "findings.json", findings)
    write_json(SITE_DATA_DIR / "meta.json", meta)
    write_json(SITE_DATA_DIR / "planned_routes.geojson", stub_layer(
        "CDOT publishes planned bikeways only as PDF maps — no structured feed yet. "
        "See CONTRIBUTING.md to digitize and drop data in."))
    write_json(SITE_DATA_DIR / "mellow_routes.geojson", mellow_gj)

    aldermen_path = SITE_DATA_DIR / "aldermen.json"
    if not aldermen_path.exists():
        write_json(aldermen_path, {
            "note": "Names/contacts intentionally left null — fill from the official lookup; "
                    "never auto-generate. Lookup: https://www.chicago.gov/city/en/about/wards.html",
            "lookup_url": "https://www.chicago.gov/city/en/about/wards.html",
            "wards": [{"ward": str(w), "alderman": None, "email": None} for w in range(1, 51)],
        })

    print(f"aggregate: {len(crash_gj['features'])} crashes, {len(routes_gj['features'])} segments, "
          f"{len(wards_gj['features'])} wards, {len(corridors)} corridors, "
          f"{len(intersections)} hotspots, {len(findings)} findings -> site/data "
          f"(provenance={provenance})")


if __name__ == "__main__":
    main()
