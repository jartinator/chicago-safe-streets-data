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
from datetime import datetime, timedelta, timezone

import geopandas as gpd
from shapely.geometry import Point, shape

from config import (RAW_DIR, SITE_DATA_DIR, SNAPSHOT_DIR, METRIC_CRS, OUTPUT_CRS,
                    FACILITY_CATEGORY_MAP, FACILITY_CATEGORIES,
                    INJURY_SEVERITY_MAP, CONTRACT_VERSION)
from council_merge import load_all_council_records
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
    """Empty GeoJSON FeatureCollection stub — for geometry layers only.

    For a non-geometry, dict-with-a-records-list layer (e.g. council_records.json),
    write a same-shaped "empty" function next to that layer's builder instead
    (see empty_council_records()) — this shape has no "data_tier" key at the
    top level, so a caller that reads one from the other will KeyError.
    """
    return {"type": "FeatureCollection", "features": [],
            "properties": {"status": "no_data_yet", "note": status_note}}


def ward_population():
    path = RAW_DIR / "ward_demographics.json"
    if not path.exists():
        return {}
    rows = json.loads(path.read_text())
    return {str(r["ward"]): float(r["total_population"]) for r in rows
            if r.get("total_population") is not None}


def ward_bikeway_miles(routes_gj, wards_gdf):
    """Total bikeway length per ward, in miles (lines clipped to ward polygons)."""
    if not routes_gj["features"]:
        return {}
    routes_gdf = gpd.GeoDataFrame.from_features(routes_gj["features"], crs=OUTPUT_CRS).to_crs(METRIC_CRS)
    wards_m = wards_gdf.to_crs(METRIC_CRS)[["ward", "geometry"]]
    overlaid = gpd.overlay(routes_gdf[["geometry"]], wards_m, how="intersection")
    miles = defaultdict(float)
    for _, row in overlaid.iterrows():
        if row.geometry is not None:
            miles[row["ward"]] += row.geometry.length / 1609.34
    return dict(miles)


def percentile_rank(values_by_key):
    """0-100 rank of each key's value among all keys with a non-null value (higher = worse)."""
    present = {k: v for k, v in values_by_key.items() if v is not None}
    if len(present) < 2:
        return {k: None for k in values_by_key}
    ordered = sorted(present.items(), key=lambda kv: kv[1])
    n = len(ordered)
    ranks = {k: round(100 * i / (n - 1), 1) for i, (k, _) in enumerate(ordered)}
    return {k: ranks.get(k) for k in values_by_key}


def crash_ward_dates(crashes):
    """{ward: [date, ...]} from crash dates, located crashes only.

    Takes the raw joined-crash records (crashes_joined.json shape), which key
    the date as "crash_date" — not build_crash_geojson()'s renamed "date".
    """
    out = defaultdict(list)
    for c in crashes:
        w = c.get("ward")
        d = c.get("crash_date")
        if not w or not d:
            continue
        out[w].append(d[:10])
    return out


def crash_trend(dates):
    """Trailing-12-months vs the prior 12 months, anchored to the latest crash date.

    Calendar-year buckets would compare a partial current year against a full
    prior year and call a mid-year pipeline run "improving" purely from having
    fewer months of data — a rolling window avoids that bias regardless of
    when the pipeline runs.
    """
    if not dates:
        return {"direction": "insufficient_data", "window_end": None,
                "recent_12mo": None, "prior_12mo": None, "pct_change": None}
    parsed = sorted(datetime.strptime(d, "%Y-%m-%d") for d in dates)
    anchor = parsed[-1]
    recent_start = anchor - timedelta(days=365)
    prior_start = anchor - timedelta(days=730)
    if parsed[0] > prior_start:
        return {"direction": "insufficient_data", "window_end": anchor.date().isoformat(),
                "recent_12mo": None, "prior_12mo": None, "pct_change": None}
    recent = sum(1 for d in parsed if d > recent_start)
    prior = sum(1 for d in parsed if prior_start < d <= recent_start)
    pct_change = round(100 * (recent - prior) / prior, 1) if prior > 0 else None
    direction = ("insufficient_data" if pct_change is None
                 else "improving" if pct_change <= -5
                 else "worsening" if pct_change >= 5
                 else "flat")
    return {"direction": direction, "window_end": anchor.date().isoformat(),
            "recent_12mo": recent, "prior_12mo": prior, "pct_change": pct_change}


def infra_growth_trend(wards_gdf):
    """Bikeway-mile growth per ward between the oldest and newest route snapshot."""
    snapshots = sorted(SNAPSHOT_DIR.glob("bike_routes_*.geojson")) if SNAPSHOT_DIR.exists() else []
    if len(snapshots) < 2:
        return {}, ("Only one bike-route snapshot exists so far — infrastructure growth trend "
                     "needs at least two pipeline runs over time to compare. Check back after "
                     "the next scheduled refresh.")
    oldest_gj = json.loads(snapshots[0].read_text())
    newest_gj = json.loads(snapshots[-1].read_text())
    oldest_miles = ward_bikeway_miles({"features": oldest_gj["features"]}, wards_gdf)
    newest_miles = ward_bikeway_miles({"features": newest_gj["features"]}, wards_gdf)
    out = {}
    for w in wards_gdf["ward"]:
        old_m, new_m = oldest_miles.get(w, 0.0), newest_miles.get(w, 0.0)
        pct = round(100 * (new_m - old_m) / old_m, 1) if old_m > 0 else None
        out[w] = {"miles_added": round(new_m - old_m, 2), "pct_growth": pct,
                  "since": snapshots[0].stem.replace("bike_routes_", "")}
    note = (f"Compared {snapshots[0].stem.replace('bike_routes_', '')} to "
            f"{snapshots[-1].stem.replace('bike_routes_', '')} ({len(snapshots)} snapshots total).")
    return out, note


def build_ward_safety_index(crashes, wards_gj, routes_gj, wards_gdf):
    pop = ward_population()
    miles = ward_bikeway_miles(routes_gj, wards_gdf)
    ward_dates = crash_ward_dates(crashes)
    infra_trend, infra_note = infra_growth_trend(wards_gdf)

    per_capita, per_mile = {}, {}
    for f in wards_gj["features"]:
        w = f["properties"]["ward"]
        crash_count = f["properties"]["cyclist_crashes"]
        p, m = pop.get(w), miles.get(w)
        per_capita[w] = round(crash_count / (p / 10_000), 2) if p and p > 0 else None
        per_mile[w] = round(crash_count / m, 2) if m and m > 0 else None

    capita_rank = percentile_rank(per_capita)
    mile_rank = percentile_rank(per_mile)

    records = []
    for f in wards_gj["features"]:
        w = f["properties"]["ward"]
        ranks = [r for r in (capita_rank.get(w), mile_rank.get(w)) if r is not None]
        blended = round(sum(ranks) / len(ranks), 1) if ranks else None
        records.append({
            "ward": w,
            "cyclist_crashes": f["properties"]["cyclist_crashes"],
            "population": pop.get(w),
            "bikeway_miles": round(miles[w], 2) if w in miles else None,
            "crashes_per_10k_pop": per_capita.get(w),
            "crashes_per_bikeway_mile": per_mile.get(w),
            "comparable_danger_score": blended,
            "crash_trend": crash_trend(ward_dates.get(w, [])),
            "infra_growth_trend": infra_trend.get(w),
            "data_tier": "derived",
        })
    # None (no score computable) sorts after every real score, including a real 0.
    records.sort(key=lambda r: (r["comparable_danger_score"] is None,
                                -(r["comparable_danger_score"] or 0)))
    return {
        "data_tier": "derived",
        "note": ("comparable_danger_score is a 0-100 blend of each ward's percentile rank on "
                 "crashes-per-10k-population and crashes-per-bikeway-mile (higher = more "
                 "dangerous relative to other wards). Population is missing for wards not "
                 "present in ward_demographics.json; bikeway_miles is 0 for wards with no "
                 "mapped bike infrastructure, which lowers crashes_per_bikeway_mile's "
                 "denominator and is a meaningful signal, not a data gap. " + infra_note),
        "wards": records,
    }


def load_name_to_ward():
    """{lowercased alderman name: ward} from the manually-filled aldermen.json.

    Built once in main() and threaded through both build_council_records() and
    build_aldermen_safety_record() — they used to each rebuild this
    independently from the same file.
    """
    aldermen_path = SITE_DATA_DIR / "aldermen.json"
    if not aldermen_path.exists():
        return {}
    aldermen = json.loads(aldermen_path.read_text())
    return {w["alderman"].strip().lower(): w["ward"] for w in aldermen.get("wards", [])
            if w.get("alderman")}


def empty_council_records():
    """Same {data_tier, note, records} shape as build_council_records()'s success
    path — NOT stub_layer()'s GeoJSON FeatureCollection shape, which main()
    can't read a "data_tier" key from. A fresh dict/list every call, not a
    shared module-level constant, so nothing downstream can ever mutate a
    value shared across pipeline runs within the same process.
    """
    return {
        "data_tier": "real",
        "topic_tag_tier": "derived",
        "note": ("Council legislative records were not pulled this run "
                 "(neither pull_council_records.py / Legistar nor pull_councilmatic.py / "
                 "Councilmatic ran, or both sources were unreachable). See CONTRIBUTING.md."),
        "records": [],
    }


def build_council_records(name_to_ward):
    records, meta = load_all_council_records(RAW_DIR)
    if not records:
        return empty_council_records(), []

    tags = {t["matter_id"]: t for t in
            json.loads((RAW_DIR / "safety_topic_tags.json").read_text())} \
        if (RAW_DIR / "safety_topic_tags.json").exists() else {}
    corrections = {t["matter_id"]: t for t in
                   json.loads((RAW_DIR / "safety_topic_corrections.json").read_text())} \
        if (RAW_DIR / "safety_topic_corrections.json").exists() else {}

    out = []
    for r in records:
        mid = r["matter_id"]
        if corrections.get(mid):
            tag, tag_source = corrections[mid], "manual_correction"
        elif tags.get(mid):
            tag, tag_source = tags[mid], tags[mid].get("tagged_by", "unknown")
        else:
            continue  # not yet classified this run
        sponsor_wards = sorted({name_to_ward[s.strip().lower()] for s in (r.get("sponsors") or [])
                                if s.strip().lower() in name_to_ward})
        rec = {
            "matter_id": mid,
            "title": r.get("title"),
            "type": r.get("type"),
            "status": r.get("status"),
            "intro_date": r.get("intro_date"),
            "sponsors": r.get("sponsors") or [],
            "sponsor_wards": sponsor_wards,
            "url": r.get("url"),
            "source": r.get("source", "legistar"),
            "topic_relevant": tag.get("topic_relevant", True),
            "topic_reason": tag.get("topic_reason", "(manual correction, no reason given)"),
            "topic_tagged_by": tag_source,
            "data_tier": "real",
            "topic_tag_tier": "derived",
        }
        if r.get("recorded_votes"):
            rec["recorded_votes"] = r["recorded_votes"]
        out.append(rec)
    out.sort(key=lambda r: r.get("intro_date") or "", reverse=True)

    if meta["has_councilmatic"]:
        note = (f"Merged from two sources: the Legistar Web API (historical, through "
                f"{meta['legistar_frozen_at']}) and DataMade's Chicago Councilmatic mirror "
                f"(current through {meta['councilmatic_latest']}), which covers the period "
                f"after Chicago's council left Legistar. Each record carries a `source`. "
                f"recorded_votes appears only on the rare bills with a recorded roll-call "
                f"split — most council actions pass by voice vote. sponsor_wards resolves "
                f"only when a sponsor's name exactly matches a manually-filled entry in "
                f"aldermen.json; empty means unresolved, not 'no sponsors'. "
                f"topic_relevant/topic_reason are automated tags (topic_tag_tier: derived) "
                f"— see topic_tagged_by ('llm' vs 'keyword_fallback').")
    else:
        note = (f"Sourced from the Legistar Web API, which is only current through "
                f"{meta['legistar_frozen_at']} (Chicago's council migrated to a new system "
                f"after that date — see DECISIONS.md). Councilmatic data was not available "
                f"this run, so records after that date are missing. sponsor_wards resolves "
                f"only when a sponsor's name exactly matches a manually-filled entry in "
                f"aldermen.json; empty means unresolved, not 'no sponsors'. "
                f"topic_relevant/topic_reason are automated tags (topic_tag_tier: derived) "
                f"— see topic_tagged_by ('llm' vs 'keyword_fallback').")

    return {
        "data_tier": "real",
        "topic_tag_tier": "derived",
        "note": note,
        "records": out,
    }, out


def build_aldermen_safety_record(council_records, name_to_ward):
    by_sponsor = defaultdict(lambda: {"relevant_count": 0, "total_count": 0, "records": []})

    # Count recorded 'no' votes on topic-relevant matters, per alderman name.
    no_votes_by_name = defaultdict(int)
    for r in council_records:
        if r.get("topic_relevant") and r.get("recorded_votes"):
            for name in r["recorded_votes"].get("no_voters", []):
                no_votes_by_name[name] += 1

    for r in council_records:
        for sponsor in r["sponsors"]:
            d = by_sponsor[sponsor]
            d["total_count"] += 1
            if r["topic_relevant"]:
                d["relevant_count"] += 1
            d["records"].append({
                "matter_id": r["matter_id"], "title": r["title"], "type": r["type"],
                "status": r["status"], "intro_date": r["intro_date"],
                "topic_relevant": r["topic_relevant"], "url": r["url"],
            })

    # Aldermen who only ever appear as a recorded 'no' voter (never sponsored)
    # must still be listed — otherwise the honest signal we added is invisible.
    for name in no_votes_by_name:
        by_sponsor[name]

    out = []
    for sponsor, d in sorted(by_sponsor.items(),
                             key=lambda kv: (-kv[1]["relevant_count"],
                                             -no_votes_by_name.get(kv[0], 0))):
        out.append({
            "sponsor_name": sponsor,
            "ward": name_to_ward.get(sponsor.strip().lower()),
            "safety_sponsorships": d["relevant_count"],
            "total_matched_sponsorships": d["total_count"],
            "recorded_no_votes": no_votes_by_name.get(sponsor, 0),
            "records": d["records"],
            "data_tier": "derived",
        })
    return {
        "data_tier": "derived",
        "note": ("Aggregate of Chicago City Council sponsorships on matters tagged "
                 "topic_relevant (see council_records.json), plus recorded_no_votes: the "
                 "count of the rare recorded roll-call votes where this member voted 'no' "
                 "on a topic-relevant matter. Most council street-safety actions pass by "
                 "voice vote with no individual vote recorded, so recorded_no_votes is "
                 "near-zero for nearly everyone by design, not omission. ward is null until "
                 "sponsor_name exactly matches the manually-filled aldermen.json "
                 "(DECISIONS.md #8) — never auto-matched by fuzzy name similarity."),
        "aldermen": out,
    }


def build_hearings():
    path = RAW_DIR / "hearings.json"
    if not path.exists():
        return {"data_tier": "real", "as_of": None, "structured_data_available": False,
                "note": "pull_hearings.py did not run this pipeline run.", "committees": []}
    raw = json.loads(path.read_text())
    raw["data_tier"] = "real"
    return raw


def build_menu_spending():
    path = RAW_DIR / "menu_spending.json"
    if not path.exists():
        return {"data_tier": "proxy", "note": (
            "Ward Wise (wardwisechicago.org), the only structured source for aldermanic menu "
            "spending, was unreachable this run (the city itself only publishes PDF reports). "
            "See CONTRIBUTING.md."), "wards": {}}
    items = json.loads(path.read_text())
    by_ward = defaultdict(lambda: {"total_spent": 0.0, "items": 0})
    bike_keywords = ("bike", "bicycle", "traffic calming", "speed hump", "crosswalk",
                      "curb", "pedestrian")
    for item in items:
        w = str(item.get("ward")) if item.get("ward") is not None else None
        if not w:
            continue
        cost_val = item.get("cost")
        if cost_val is None:
            cost_val = item.get("amount")
        cost = float(cost_val) if cost_val is not None else 0.0
        category = str(item.get("category") or "").lower()
        by_ward[w]["total_spent"] += cost
        by_ward[w]["items"] += 1
        if any(kw in category for kw in bike_keywords):
            by_ward[w]["bike_safety_spent"] = by_ward[w].get("bike_safety_spent", 0.0) + cost
    return {
        "data_tier": "proxy",
        "note": ("Ward Wise (Chi Hack Night volunteer project) structuring the city's "
                 "PDF-only Aldermanic Menu Program reports. Not independently verified against "
                 "the source PDFs by this pipeline."),
        "wards": {w: {"total_spent": round(d["total_spent"], 2), "items": d["items"],
                      "bike_safety_spent": round(d.get("bike_safety_spent", 0.0), 2)}
                 for w, d in by_ward.items()},
    }


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

    wards_gj, wards_gdf = build_wards(crashes, sr311_by_ward)
    corridors = build_corridors(routes_gj, crashes)
    intersections = build_intersections(crashes)
    findings = build_findings(crashes, routes_gj, corridors, wards_gj)

    ward_safety_index = build_ward_safety_index(crashes, wards_gj, routes_gj, wards_gdf)
    name_to_ward = load_name_to_ward()
    council_records_out, council_records_list = build_council_records(name_to_ward)
    aldermen_safety_record = build_aldermen_safety_record(council_records_list, name_to_ward)
    hearings_out = build_hearings()
    menu_spending_out = build_menu_spending()

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
             if mellow_gj["features"] else []) + [
            {"id": "ward_safety_index", "name": "Ward Safety Index (comparable danger score)",
             "tier": "derived", "records": len(ward_safety_index["wards"]), "date_range": None},
            {"id": "council_records", "name": "Council Records (street/bike-safety legislation)",
             "tier": council_records_out["data_tier"], "records": len(council_records_list),
             "date_range": None},
            {"id": "aldermen_safety_record", "name": "Alderman Safety Voting Record",
             "tier": "derived", "records": len(aldermen_safety_record["aldermen"]),
             "date_range": None},
            {"id": "hearings", "name": "Upcoming Bike/Traffic-Safety Committee Hearings",
             "tier": "real", "records": len(hearings_out.get("committees", [])),
             "date_range": None},
            {"id": "menu_spending", "name": "Aldermanic Menu Program Spending (Ward Wise)",
             "tier": "proxy", "records": len(menu_spending_out.get("wards", {})),
             "date_range": None},
        ],
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
    write_json(SITE_DATA_DIR / "ward_safety_index.json", ward_safety_index)
    write_json(SITE_DATA_DIR / "council_records.json", council_records_out)
    write_json(SITE_DATA_DIR / "aldermen_safety_record.json", aldermen_safety_record)
    write_json(SITE_DATA_DIR / "hearings.json", hearings_out)
    write_json(SITE_DATA_DIR / "menu_spending.json", menu_spending_out)

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
