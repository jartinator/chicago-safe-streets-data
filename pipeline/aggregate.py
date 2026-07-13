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
from shapely.geometry import Point, shape, LineString, MultiLineString

from config import (RAW_DIR, SITE_DATA_DIR, SNAPSHOT_DIR, FIXTURE_SNAPSHOT_DIR,
                    METRIC_CRS, OUTPUT_CRS,
                    FACILITY_CATEGORY_MAP, FACILITY_CATEGORIES,
                    INJURY_SEVERITY_MAP, CONTRACT_VERSION, CRASH_START_DATE,
                    MAIN_ROUTES_PATH, MAIN_ROUTE_GRADE_MAP,
                    CURATED_TRAILS_PATH, ORIENTATION_POINTS_PATH)
from council_merge import load_all_council_records
from crash_metrics import (monthly_counts, per_ward_monthly, window_counts,
                           build_findings_core)
from socrata import write_json
from spatial_join import _first_key


def severity(rec):
    return INJURY_SEVERITY_MAP.get((rec.get("most_severe_injury") or "").upper(), "unknown")


def flag(rec, key):
    return (rec.get(key) or "").upper() == "Y"


def crash_tuples(crashes):
    """Raw joined-crash records -> the plain crash tuples crash_metrics operates on.

    Built once in main() and threaded through findings, the ward safety index,
    and the citywide trend so every published number derives from one shape.
    """
    return [{"date": (c.get("crash_date") or "")[:10],
             "severity": severity(c),
             "hit_and_run": flag(c, "hit_and_run_i"),
             "dooring": flag(c, "dooring_i"),
             "ward": c.get("ward")}
            for c in crashes if c.get("crash_date")]


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


def build_findings(tuples, corridors, wards_gj, as_of_date):
    """Thin live-path wrapper over crash_metrics.build_findings_core.

    The assembly itself lives in crash_metrics so refresh_reporting.py can rebuild
    the identical findings from committed site data. Protected-share miles come
    from the raw CDOT layer's centerline mileage (citywide_miles_by_category),
    matching bikeway_mileage_series.json's methodology; the `trail` category is
    excluded inside protected_share (off-street trails are OSM/crowdsourced and
    never enter real-tier statistics).
    """
    raw_routes = json.loads((RAW_DIR / "bike_routes.geojson").read_text())
    by_category_miles = citywide_miles_by_category(raw_routes)
    ward_counts = {f["properties"]["ward"]: f["properties"]["cyclist_crashes"]
                   for f in wards_gj["features"]}
    return build_findings_core(tuples, by_category_miles, corridors, ward_counts, as_of_date)


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


def _slug(name):
    """Lowercase, non-alphanumeric runs -> single hyphen; trimmed. For segment ids."""
    out = []
    prev_dash = False
    for ch in name.strip().lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-")


def build_osm_trails(raw):
    """Group Overpass named off-street ways into one feature per trail name.

    Overpass `out geom` returns way elements with an inline `geometry` list of
    {lat, lon} points and a `tags.name`. Ways sharing a name (a trail is chopped
    into many OSM ways) collapse into a single MultiLineString feature — one
    Leaflet layer per trail, not per fragment (same rationale as build_mellow).
    Tier is crowdsourced; facility_category reuses the pre-wired "trail" styling.
    """
    by_name = defaultdict(list)  # name -> list[list[(lon, lat)]]
    for el in raw.get("elements", []):
        if el.get("type") != "way":
            continue
        name = (el.get("tags") or {}).get("name")
        geom = el.get("geometry") or []
        if not name or len(geom) < 2:
            continue
        by_name[name].append([(pt["lon"], pt["lat"]) for pt in geom])

    if not by_name:
        return {"type": "FeatureCollection", "features": [], "data_tier": "crowdsourced"}

    names = sorted(by_name)
    shapes = []
    for name in names:
        parts = by_name[name]  # each part has >=2 coords (filtered above)
        shapes.append(LineString(parts[0]) if len(parts) == 1 else MultiLineString(parts))
    lengths = gpd.GeoDataFrame(geometry=shapes, crs=OUTPUT_CRS).to_crs(METRIC_CRS).geometry.length

    feats = []
    for name, geom, length in zip(names, shapes, lengths):
        feats.append({
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "segment_id": f"osm-trail-{_slug(name)}",
                "name": name,
                "facility_category": "trail",
                "length_m": round(float(length), 1),
                "data_tier": "crowdsourced",
            },
        })
    return {"type": "FeatureCollection", "features": feats, "data_tier": "crowdsourced"}


def build_curated_trails(curated_gj):
    """Build the osm_trails layer from the hand-traced curated fallback (spec §8,
    docs/superpowers/specs/2026-07-12-network-map-distinction.md).

    Used when raw/osm_trails.json (a real Overpass pull) is absent but
    data/curated_trails.geojson exists. Each feature passes through unchanged
    except length_m, recomputed with the identical UTM-16N reprojection
    build_osm_trails uses, so build_main_routes and every other osm_trails
    consumer see the same shape regardless of which source built the layer.
    Tier stays crowdsourced; the curated file's top-level note (provenance/
    approximation caveat) is preserved onto the output.
    """
    feats_in = curated_gj.get("features", [])
    if not feats_in:
        return {"type": "FeatureCollection", "features": []}
    shapes = [shape(f["geometry"]) for f in feats_in]
    lengths = gpd.GeoDataFrame(geometry=shapes, crs=OUTPUT_CRS).to_crs(METRIC_CRS).geometry.length
    feats = []
    for f, length in zip(feats_in, lengths):
        props = dict(f.get("properties") or {})
        props["length_m"] = round(float(length), 1)
        props.setdefault("data_tier", "crowdsourced")
        feats.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    out = {"type": "FeatureCollection", "features": feats, "data_tier": "crowdsourced"}
    if curated_gj.get("note"):
        out["note"] = curated_gj["note"]
    return out


def build_osm_trails_layer(raw_path=None, curated_path=CURATED_TRAILS_PATH):
    """site/data/osm_trails.geojson, in spec §8's priority order:

    1. raw_path (a real Overpass pull, pipeline/raw/osm_trails.json) via build_osm_trails;
    2. else curated_path (data/curated_trails.geojson) via build_curated_trails;
    3. else the empty stub.

    Shared by aggregate.main() and refresh_reporting.py so both build paths
    apply the identical priority order and can never drift.
    """
    raw_path = raw_path if raw_path is not None else (RAW_DIR / "osm_trails.json")
    if raw_path.exists():
        return build_osm_trails(json.loads(raw_path.read_text()))
    if curated_path.exists():
        return build_curated_trails(json.loads(curated_path.read_text()))
    return stub_layer(
        "OpenStreetMap off-street trails (Lakefront, 312 RiverRun, North Shore "
        "Channel, North Branch, etc.) were not pulled this run (pull_osm_trails.py "
        "didn't run, or Overpass was unreachable), and no curated fallback exists "
        "at data/curated_trails.geojson either. See CONTRIBUTING.md.")


_STREET_TYPE_SUFFIXES = {"ST", "AVE", "BLVD", "RD", "DR", "WAY", "PKWY"}

_MILES_PER_M = 1 / 1609.34


def normalize_street(name):
    """Uppercase and strip ONE trailing street-type suffix token.

    The raw CDOT layer mixes suffix variants ("RANDOLPH" vs "RANDOLPH ST");
    roster matching compares normalized names for exact equality — never
    substring containment, so "EAST LAKE"/"LAKE SHORE" can't leak into "LAKE".
    """
    tokens = (name or "").upper().split()
    if len(tokens) > 1 and tokens[-1] in _STREET_TYPE_SUFFIXES:
        tokens = tokens[:-1]
    return " ".join(tokens)


def _geometry_midpoint(geometry):
    """(lat, lon) of the middle vertex of the flattened coordinate list.

    Deliberately the middle VERTEX, not a projected length-interpolated point:
    it needs no CRS machinery, and on the real 1,008-segment CDOT layer it
    selects the identical loop-bbox membership as true midpoint interpolation
    (verified 2026-07-12). Open knob per spec §11, resolved as midpoint-in-bbox.
    """
    if geometry["type"] == "LineString":
        coords = geometry["coordinates"]
    elif geometry["type"] == "MultiLineString":
        coords = [pt for part in geometry["coordinates"] for pt in part]
    else:
        return None
    if not coords:
        return None
    lon, lat = coords[len(coords) // 2][:2]
    return lat, lon


def _in_bbox(latlon, bbox):
    lat, lon = latlon
    south, west, north, east = bbox
    return south <= lat <= north and west <= lon <= east


def load_main_routes_roster(path=MAIN_ROUTES_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def load_orientation_points(path=ORIENTATION_POINTS_PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def build_main_routes(routes_gj, osm_trails_gj, roster):
    """Assign published segments to the curated main-route roster.

    Pure function over already-published feature shapes (bike_routes.geojson +
    osm_trails.geojson properties), so refresh_reporting.py can rebuild the
    layer from committed site data with the exact same code path as the live
    aggregate run. Roster lines match in order; first match wins; a segment
    joins at most one line. Corridor gaps are holes — geometry is never
    fabricated, and every share is computed over member miles only. Street
    lines aggregate real CDOT segments (line stats: derived); trail lines are
    OSM crowdsourced throughout; the two tiers never blend.
    """
    street_feats = routes_gj.get("features", [])
    trail_feats = osm_trails_gj.get("features", [])
    claimed = set()
    out_feats = []
    lines_out = []

    for line in roster["lines"]:
        is_street = line["source"] == "bike_routes"
        members = []  # (feature, grade, length_m, crashes)
        if is_street:
            streets = set(line["streets"])
            bbox = line.get("clip_bbox")
            for f in street_feats:
                p = f["properties"]
                seg_id = p.get("segment_id")
                if seg_id in claimed:
                    continue
                if normalize_street(p.get("street")) not in streets:
                    continue
                if bbox:
                    mid = _geometry_midpoint(f["geometry"])
                    if mid is None or not _in_bbox(mid, bbox):
                        continue
                claimed.add(seg_id)
                grade = MAIN_ROUTE_GRADE_MAP.get(p.get("facility_category"), "none")
                length_m = float(p.get("length_m") or 0.0)
                crashes = int(p.get("crashes_within_30m") or 0)
                members.append(({
                    "type": "Feature",
                    "geometry": f["geometry"],
                    "properties": {
                        "segment_id": seg_id,
                        "line_id": line["id"],
                        "grade": grade,
                        "facility_category": p.get("facility_category"),
                        "length_m": length_m,
                        "crashes_within_30m": crashes,
                        "data_tier": "real",
                    },
                }, grade, length_m, crashes))
        else:  # osm_trails
            tokens = [t.lower() for t in line["name_tokens"]]
            for f in trail_feats:
                p = f["properties"]
                seg_id = p.get("segment_id")
                if seg_id in claimed:
                    continue
                trail_name = (p.get("name") or "").lower()
                if not any(tok in trail_name for tok in tokens):
                    continue
                claimed.add(seg_id)
                length_m = float(p.get("length_m") or 0.0)
                members.append(({
                    "type": "Feature",
                    "geometry": f["geometry"],
                    "properties": {
                        "segment_id": seg_id,
                        "line_id": line["id"],
                        "grade": "offstreet",
                        "facility_category": "trail",
                        "length_m": length_m,
                        "data_tier": "crowdsourced",
                    },
                }, "offstreet", length_m, None))

        miles_by_grade = defaultdict(float)
        for _, grade, length_m, _ in members:
            miles_by_grade[grade] += length_m * _MILES_PER_M
        miles_total = sum(miles_by_grade.values())
        entry = {
            "id": line["id"],
            "name": line["name"],
            "termini": line["termini"],
            "source": line["source"],
            "data_tier": "derived" if is_street else "crowdsourced",
            "miles_total": round(miles_total, 2),
            "miles_by_grade": {g: round(m, 2) for g, m in miles_by_grade.items()},
        }
        if is_street:
            entry["pct_protected"] = (round(100 * miles_by_grade["protected"] / miles_total, 1)
                                      if miles_total > 0 else None)
            entry["crashes_total"] = sum(c for _, _, _, c in members)
        if not members:
            entry["no_data"] = True
        lines_out.append(entry)
        out_feats.extend(f for f, _, _, _ in members)

    return {
        "type": "FeatureCollection",
        "data_tier": "derived",
        "note": ("Curated main-route lines assigned from published segments each run. "
                 "The roster is editorial: we chose which corridors count as main routes; "
                 "segment grades and mileage are computed from source data every run. "
                 "Street lines aggregate real CDOT segments (stats: derived tier); trail "
                 "lines come from OpenStreetMap (crowdsourced tier) and never blend into "
                 "derived statistics. Corridor gaps are holes in the line — geometry is "
                 "never fabricated — and grade shares are over existing member miles only."),
        "lines": lines_out,
        "features": out_feats,
    }


def _line_id_to_name_and_order(main_routes_gj):
    """{line_id: name} and {line_id: roster position} from main_routes_gj["lines"].

    The roster position gives node labels a deterministic, spec-matching join
    order (e.g. "Milwaukee Line × Bloomingdale Trail (606)" — milwaukee is
    listed before the trail lines in data/main_routes.json).
    """
    id_to_name, id_to_order = {}, {}
    for i, ln in enumerate(main_routes_gj.get("lines", [])):
        id_to_name[ln["id"]] = ln["name"]
        id_to_order[ln["id"]] = i
    return id_to_name, id_to_order


def _geometry_segments(geometry):
    """Flatten a LineString/MultiLineString geometry into consecutive-vertex
    ((lon, lat), (lon, lat)) segment pairs for exact intersection math."""
    gtype = geometry.get("type")
    if gtype == "LineString":
        parts = [geometry["coordinates"]]
    elif gtype == "MultiLineString":
        parts = geometry["coordinates"]
    else:
        return []
    segs = []
    for coords in parts:
        for a, b in zip(coords, coords[1:]):
            segs.append(((a[0], a[1]), (b[0], b[1])))
    return segs


def _bboxes_overlap(p1, p2, p3, p4):
    """Cheap axis-aligned pre-filter before the full intersection solve below."""
    ax0, ax1 = (p1[0], p2[0]) if p1[0] <= p2[0] else (p2[0], p1[0])
    ay0, ay1 = (p1[1], p2[1]) if p1[1] <= p2[1] else (p2[1], p1[1])
    bx0, bx1 = (p3[0], p4[0]) if p3[0] <= p4[0] else (p4[0], p3[0])
    by0, by1 = (p3[1], p4[1]) if p3[1] <= p4[1] else (p4[1], p3[1])
    return ax0 <= bx1 and bx0 <= ax1 and ay0 <= by1 and by0 <= ay1


def _segment_intersection(p1, p2, p3, p4):
    """Exact 2-D intersection point of segments p1->p2 and p3->p4, or None.

    Points are (lon, lat) tuples; the math is plain Cartesian line-segment
    intersection (cross-product / parametric form) — scale- and unit-invariant,
    so doing it directly in lng/lat is correct for a yes/no + location
    crossing test (unlike a length computation, which needs a projected CRS).
    None covers parallel/collinear segments and crossings outside either
    segment's span. Endpoint-inclusive (small epsilon) so two lines that meet
    exactly at a shared vertex still register as an interchange.
    """
    if not _bboxes_overlap(p1, p2, p3, p4):
        return None
    (x1, y1), (x2, y2) = p1, p2
    (x3, y3), (x4, y4) = p3, p4
    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x4 - x3, y4 - y3
    denom = dx1 * dy2 - dy1 * dx2
    if abs(denom) < 1e-18:
        return None
    t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / denom
    u = ((x3 - x1) * dy1 - (y3 - y1) * dx1) / denom
    eps = 1e-9
    if -eps <= t <= 1 + eps and -eps <= u <= 1 + eps:
        return (x1 + t * dx1, y1 + t * dy1)
    return None


# Local equirectangular approximation for Chicago's latitude (~41.85N), matching
# the constants build_intersections() already uses for its grid-cluster cell math.
_LAT_M_PER_DEG = 111_320.0
_LON_M_PER_DEG = 83_000.0


def _meters_apart(latlon1, latlon2):
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    dy = (lat2 - lat1) * _LAT_M_PER_DEG
    dx = (lon2 - lon1) * _LON_M_PER_DEG
    return (dx * dx + dy * dy) ** 0.5


def _cluster_points(points, threshold_m):
    """Union-find clustering: merge (lat, lon, {line_ids}) points within
    threshold_m of ANY other point in their eventual cluster, returning one
    (centroid_lat, centroid_lon, merged_line_ids) per cluster.
    """
    n = len(points)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if _meters_apart(points[i][:2], points[j][:2]) <= threshold_m:
                union(i, j)

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    clusters = []
    for idxs in groups.values():
        lat = sum(points[i][0] for i in idxs) / len(idxs)
        lon = sum(points[i][1] for i in idxs) / len(idxs)
        line_ids = set()
        for i in idxs:
            line_ids |= points[i][2]
        clusters.append((lat, lon, line_ids))
    return clusters


# Padding (in degrees, at Chicago's latitude) added around each line's bbox before
# the build_network_nodes() pairwise prefilter below, so two lines whose segments
# don't literally overlap but whose nearest points are still within the 150 m merge
# distance aren't wrongly skipped.
_NODE_MERGE_PAD_LON_DEG = 150 / _LON_M_PER_DEG
_NODE_MERGE_PAD_LAT_DEG = 150 / _LAT_M_PER_DEG


def _line_bbox(segs):
    """(min_lon, min_lat, max_lon, max_lat) over every vertex in segs, padded by
    the 150 m node-merge distance. None for an empty segment list."""
    lons = [pt[0] for seg in segs for pt in seg]
    lats = [pt[1] for seg in segs for pt in seg]
    if not lons:
        return None
    return (min(lons) - _NODE_MERGE_PAD_LON_DEG, min(lats) - _NODE_MERGE_PAD_LAT_DEG,
            max(lons) + _NODE_MERGE_PAD_LON_DEG, max(lats) + _NODE_MERGE_PAD_LAT_DEG)


def _line_bboxes_disjoint(b1, b2):
    """True when two (min_lon, min_lat, max_lon, max_lat) boxes cannot overlap."""
    return b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1]


def build_network_nodes(main_routes_gj, orientation_points):
    """Interchange + orientation nodes for the network map (spec §7,
    docs/superpowers/specs/2026-07-12-network-map-distinction.md).

    Interchanges are derived: every pair of distinct line_ids among
    main_routes_gj["features"]' member geometries is checked for exact 2-D
    segment intersections (pure python — no new deps). Raw intersection
    points within 150 m of each other merge into one node at their centroid,
    collecting every line_id involved; only merged points where >=2 distinct
    lines meet are emitted as nodes. Orientation points are curated wayfinding
    labels appended verbatim after the interchanges, tier derived, lines
    always empty (they aren't derived from any line's geometry).

    Before the O(segments_a * segments_b) inner loop for a pair of lines, a
    cheap line-level bbox prefilter (each line's overall bbox, computed once
    and padded by the 150 m merge distance) skips the pair entirely when the
    boxes can't overlap — most roster line pairs are nowhere near each other,
    so this cuts the dominant cost on the full network without changing which
    intersections are found.
    """
    id_to_name, id_to_order = _line_id_to_name_and_order(main_routes_gj)

    segs_by_line = defaultdict(list)
    for f in main_routes_gj.get("features", []):
        line_id = f["properties"]["line_id"]
        segs_by_line[line_id].extend(_geometry_segments(f["geometry"]))

    line_ids = sorted(segs_by_line)  # deterministic pairing order
    line_bboxes = {lid: _line_bbox(segs_by_line[lid]) for lid in line_ids}
    raw_points = []  # (lat, lon, {line_id, line_id})
    for i, a in enumerate(line_ids):
        for b in line_ids[i + 1:]:
            bbox_a, bbox_b = line_bboxes[a], line_bboxes[b]
            if bbox_a is None or bbox_b is None or _line_bboxes_disjoint(bbox_a, bbox_b):
                continue
            for p1, p2 in segs_by_line[a]:
                for p3, p4 in segs_by_line[b]:
                    hit = _segment_intersection(p1, p2, p3, p4)
                    if hit is not None:
                        lon, lat = hit
                        raw_points.append((lat, lon, {a, b}))

    interchanges = []
    if raw_points:
        for lat, lon, ids in _cluster_points(raw_points, threshold_m=150):
            if len(ids) < 2:
                continue
            ordered = sorted(ids, key=lambda lid: id_to_order.get(lid, 0))
            label = " × ".join(id_to_name.get(lid, lid) for lid in ordered)
            interchanges.append({"lat": round(lat, 6), "lon": round(lon, 6),
                                 "ids": ordered, "label": label})
        interchanges.sort(key=lambda n: (n["lat"], n["lon"]))

    nodes = []
    for i, n in enumerate(interchanges, start=1):
        nodes.append({
            "id": f"node-{i:03d}",
            "kind": "interchange",
            "lat": n["lat"],
            "lng": n["lon"],
            "label": n["label"],
            "lines": n["ids"],
            "data_tier": "derived",
        })
    for i, pt in enumerate(orientation_points, start=1):
        nodes.append({
            "id": f"orient-{i:03d}",
            "kind": "orientation",
            "lat": pt["lat"],
            "lng": pt["lng"],
            "label": pt["label"],
            "lines": [],
            "data_tier": "derived",
        })

    return {"nodes": nodes, "data_tier": "derived"}


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


def ward_bikeway_miles_by_category(routes_gj, wards_gdf):
    """Bikeway miles per ward split by facility category: {ward: {category: miles}}.

    Same clipped-overlay method as ward_bikeway_miles, but carries each segment's
    facility category (resolved from the raw CDOT label via FACILITY_CATEGORY_MAP)
    through the overlay so growth can be read per type — protected-lane growth is
    the signal that should track injury reduction, which a total-miles number hides.
    Reads raw snapshot props, so it resolves the type key the same tolerant way
    build_routes() does.
    """
    feats = routes_gj["features"]
    if not feats:
        return {}
    type_key = _first_key(feats[0]["properties"],
                          ["displayroute", "displayrou", "bikeroute", "type", "facility"])
    unmatched = Counter()
    recs = [{"facility_category": facility_category(
                 str(f["properties"].get(type_key)) if type_key else "", unmatched),
             "geometry": shape(f["geometry"])}
            for f in feats]
    routes_gdf = gpd.GeoDataFrame(recs, crs=OUTPUT_CRS).to_crs(METRIC_CRS)
    wards_m = wards_gdf.to_crs(METRIC_CRS)[["ward", "geometry"]]
    overlaid = gpd.overlay(routes_gdf[["facility_category", "geometry"]], wards_m, how="intersection")
    out = defaultdict(lambda: defaultdict(float))
    for _, row in overlaid.iterrows():
        if row.geometry is not None:
            out[row["ward"]][row["facility_category"]] += row.geometry.length / 1609.34
    return {w: dict(cats) for w, cats in out.items()}


def citywide_miles_by_category(routes_gj):
    """Citywide bikeway miles by facility category for one snapshot: {category: miles}.

    Prefers the CDOT-provided per-segment centerline miles (mi_ctrline) when present —
    this reproduces the published Bike Lane Mileage Tracker's own methodology — and
    falls back to projected geometry length (e.g. for fixtures, which carry no
    mi_ctrline field).
    """
    feats = routes_gj["features"]
    if not feats:
        return {}
    props0 = feats[0]["properties"]
    type_key = _first_key(props0, ["displayroute", "displayrou", "bikeroute", "type", "facility"])
    mi_key = _first_key(props0, ["mi_ctrline", "miles", "length_mi"])
    unmatched = Counter()
    out = defaultdict(float)
    if mi_key:
        for f in feats:
            p = f["properties"]
            cat = facility_category(str(p.get(type_key)) if type_key else "", unmatched)
            try:
                out[cat] += float(p.get(mi_key) or 0.0)
            except (TypeError, ValueError):
                continue
        return dict(out)
    lengths = gpd.GeoDataFrame.from_features(feats, crs=OUTPUT_CRS).to_crs(METRIC_CRS).geometry.length
    for i, f in enumerate(feats):
        cat = facility_category(str(f["properties"].get(type_key)) if type_key else "", unmatched)
        out[cat] += float(lengths.iloc[i]) / 1609.34
    return dict(out)


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


def _category_deltas(old_cats, new_cats):
    """Per-facility-category {miles_added, pct_growth} for one ward, omitting types
    absent from both snapshots (keeps the payload to types that actually exist there)."""
    by_category = {}
    for cat in FACILITY_CATEGORIES:
        old_c, new_c = old_cats.get(cat, 0.0), new_cats.get(cat, 0.0)
        if old_c == 0.0 and new_c == 0.0:
            continue
        cpct = round(100 * (new_c - old_c) / old_c, 1) if old_c > 0 else None
        by_category[cat] = {"miles_added": round(new_c - old_c, 2), "pct_growth": cpct}
    return by_category


def infra_growth_trend(wards_gdf, snapshot_dir=SNAPSHOT_DIR):
    """Bikeway-mile growth per ward between the oldest and newest route snapshot.

    Each ward record carries the total delta plus a by_category breakdown (protected,
    buffered, painted, ...), since protected-lane growth is the correlate of interest.
    """
    snapshots = sorted(snapshot_dir.glob("bike_routes_*.geojson")) if snapshot_dir.exists() else []
    if len(snapshots) < 2:
        return {}, ("Only one bike-route snapshot exists so far — infrastructure growth trend "
                     "needs at least two pipeline runs over time to compare. Check back after "
                     "the next scheduled refresh.")
    oldest_gj = json.loads(snapshots[0].read_text())
    newest_gj = json.loads(snapshots[-1].read_text())
    oldest_miles = ward_bikeway_miles({"features": oldest_gj["features"]}, wards_gdf)
    newest_miles = ward_bikeway_miles({"features": newest_gj["features"]}, wards_gdf)
    oldest_cats = ward_bikeway_miles_by_category({"features": oldest_gj["features"]}, wards_gdf)
    newest_cats = ward_bikeway_miles_by_category({"features": newest_gj["features"]}, wards_gdf)
    since = snapshots[0].stem.replace("bike_routes_", "")
    out = {}
    for w in wards_gdf["ward"]:
        old_m, new_m = oldest_miles.get(w, 0.0), newest_miles.get(w, 0.0)
        pct = round(100 * (new_m - old_m) / old_m, 1) if old_m > 0 else None
        out[w] = {"miles_added": round(new_m - old_m, 2), "pct_growth": pct, "since": since,
                  "by_category": _category_deltas(oldest_cats.get(w, {}), newest_cats.get(w, {}))}
    note = (f"Compared {since} to {snapshots[-1].stem.replace('bike_routes_', '')} "
            f"({len(snapshots)} snapshots total).")
    return out, note


def build_bikeway_mileage_series(snapshot_dir=SNAPSHOT_DIR):
    """Citywide bikeway miles by facility category per snapshot date — a machine-readable
    equivalent of CDOT's quarterly Bike Lane Mileage Tracker, built from accumulated
    snapshots so it can be correlated against crash trends over time.
    """
    snapshots = sorted(snapshot_dir.glob("bike_routes_*.geojson")) if snapshot_dir.exists() else []
    series = []
    for snap in snapshots:
        by_cat = citywide_miles_by_category(json.loads(snap.read_text()))
        series.append({
            "date": snap.stem.replace("bike_routes_", ""),
            "by_category": {c: round(by_cat.get(c, 0.0), 2) for c in FACILITY_CATEGORIES},
            "total": round(sum(by_cat.values()), 2),
        })
    if len(series) < 2:
        note = ("Citywide bikeway miles by facility type. Only one snapshot exists so far — the "
                "over-time series fills in as the pipeline runs on a quarterly cadence (the CDOT "
                "Bike Routes layer has no install-date field, so history is built forward from "
                "snapshots, not backfillable). Miles use CDOT centerline mileage where available.")
    else:
        note = (f"Citywide bikeway miles by facility type across {len(series)} snapshots "
                f"({series[0]['date']} to {series[-1]['date']}). Miles use CDOT centerline "
                f"mileage where available, else projected geometry length. The CDOT Bike Routes "
                f"layer has no install-date field, so this series is built forward from snapshots.")
    return {"data_tier": "derived", "note": note, "series": series}


def build_ward_safety_index(crashes, wards_gj, routes_gj, wards_gdf, snapshot_dir=SNAPSHOT_DIR,
                            tuples=None):
    pop = ward_population()
    miles = ward_bikeway_miles(routes_gj, wards_gdf)
    ward_dates = crash_ward_dates(crashes)
    infra_trend, infra_note = infra_growth_trend(wards_gdf, snapshot_dir)

    # Per-ward reporting series (crash_metrics): trailing-12mo windows anchored at
    # the GLOBAL latest crash date (comparable across wards, unlike crash_trend's
    # per-ward anchor) plus a contiguous monthly series since CRASH_START_DATE.
    if tuples is None:
        tuples = crash_tuples(crashes)
    anchor = max((t["date"] for t in tuples), default=None)
    start_month = CRASH_START_DATE[:7]
    end_month = anchor[:7] if anchor else start_month
    ward_monthly = per_ward_monthly(tuples, start_month, end_month)
    tuples_by_ward = defaultdict(list)
    for t in tuples:
        if t.get("ward"):
            tuples_by_ward[t["ward"]].append(t)

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
            "windows": (window_counts(tuples_by_ward.get(w, []), anchor)
                        if anchor else None),
            "monthly": ward_monthly.get(w) or monthly_counts([], start_month, end_month),
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

    # Fixtures write synthetic snapshots to their own dir so the offline series/growth
    # is coherent against fixture wards; real runs read the committed snapshot history.
    snapshot_dir = FIXTURE_SNAPSHOT_DIR if provenance == "fixtures" else SNAPSHOT_DIR

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

    tuples = crash_tuples(crashes)
    as_of_date = datetime.now(timezone.utc).date().isoformat()
    findings = build_findings(tuples, corridors, wards_gj, as_of_date)

    # Citywide monthly trend since CRASH_START_DATE, from the same crash tuples.
    trend_anchor = max((t["date"] for t in tuples), default=None)
    trend_months = monthly_counts(tuples, CRASH_START_DATE[:7],
                                  trend_anchor[:7] if trend_anchor else CRASH_START_DATE[:7])
    citywide_trend = {
        "data_tier": "real",
        "window_end": trend_anchor,
        "note": ("Monthly counts of police-reported cyclist crashes citywide since Sept 2017; "
                 "ksi = crashes whose worst injury was fatal or incapacitating (\"killed or "
                 "seriously injured\"). Recent months are provisional — records get amended."),
        "months": trend_months,
    }

    ward_safety_index = build_ward_safety_index(crashes, wards_gj, routes_gj, wards_gdf,
                                                snapshot_dir, tuples=tuples)
    bikeway_mileage_series = build_bikeway_mileage_series(snapshot_dir)
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

    # Priority order (spec §8): real Overpass pull, else the hand-traced curated
    # fallback (data/curated_trails.geojson), else the empty stub.
    osm_trails_gj = build_osm_trails_layer()

    main_routes_gj = build_main_routes(routes_gj, osm_trails_gj, load_main_routes_roster())
    network_nodes_out = build_network_nodes(main_routes_gj, load_orientation_points())

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
             if mellow_gj["features"] else []) + (
            [{"id": "osm_trails", "name": "OpenStreetMap Off-street Trails",
              "tier": "crowdsourced", "records": len(osm_trails_gj["features"]), "date_range": None}]
             if osm_trails_gj["features"] else []) + [
            {"id": "main_routes", "name": "Main Routes (curated line roster)",
             "tier": "derived", "records": len(main_routes_gj["lines"]),
             "date_range": None},
            {"id": "network_nodes", "name": "Network Map Nodes (interchanges + orientation points)",
             "tier": "derived", "records": len(network_nodes_out["nodes"]),
             "date_range": None},
            {"id": "citywide_trend", "name": "Citywide Crash Trend (monthly counts)",
             "tier": "real", "records": len(citywide_trend["months"]),
             "date_range": ([CRASH_START_DATE, citywide_trend["window_end"]]
                            if citywide_trend["window_end"] else None)},
            {"id": "ward_safety_index", "name": "Ward Safety Index (comparable danger score)",
             "tier": "derived", "records": len(ward_safety_index["wards"]), "date_range": None},
            {"id": "bikeway_mileage_series", "name": "Bikeway Mileage Series (by facility type, over time)",
             "tier": "derived", "records": len(bikeway_mileage_series["series"]),
             "date_range": ([bikeway_mileage_series["series"][0]["date"],
                             bikeway_mileage_series["series"][-1]["date"]]
                            if bikeway_mileage_series["series"] else None)},
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
    write_json(SITE_DATA_DIR / "citywide_trend.json", citywide_trend)
    write_json(SITE_DATA_DIR / "meta.json", meta)
    write_json(SITE_DATA_DIR / "planned_routes.geojson", stub_layer(
        "CDOT publishes planned bikeways only as PDF maps — no structured feed yet. "
        "See CONTRIBUTING.md to digitize and drop data in."))
    write_json(SITE_DATA_DIR / "mellow_routes.geojson", mellow_gj)
    write_json(SITE_DATA_DIR / "osm_trails.geojson", osm_trails_gj)
    write_json(SITE_DATA_DIR / "main_routes.geojson", main_routes_gj)
    write_json(SITE_DATA_DIR / "network_nodes.json", network_nodes_out)
    write_json(SITE_DATA_DIR / "ward_safety_index.json", ward_safety_index)
    write_json(SITE_DATA_DIR / "bikeway_mileage_series.json", bikeway_mileage_series)
    write_json(SITE_DATA_DIR / "council_records.json", council_records_out)
    write_json(SITE_DATA_DIR / "aldermen_safety_record.json", aldermen_safety_record)
    write_json(SITE_DATA_DIR / "hearings.json", hearings_out)
    write_json(SITE_DATA_DIR / "menu_spending.json", menu_spending_out)

    # Fixtures/offline fallback only: live runs fill aldermen.json from the city's
    # Ward Offices dataset via pull_aldermen.py (which fails soft, preserving the
    # existing file). This block just guarantees the file exists for the UI.
    aldermen_path = SITE_DATA_DIR / "aldermen.json"
    if not aldermen_path.exists():
        write_json(aldermen_path, {
            "note": "Names/contacts left null — the live pipeline fills this via "
                    "pull_aldermen.py (Ward Offices dataset); never auto-generated by guessing. "
                    "Lookup: https://www.chicago.gov/city/en/about/wards.html",
            "lookup_url": "https://www.chicago.gov/city/en/about/wards.html",
            "wards": [{"ward": str(w), "alderman": None, "email": None} for w in range(1, 51)],
        })

    print(f"aggregate: {len(crash_gj['features'])} crashes, {len(routes_gj['features'])} segments, "
          f"{len(wards_gj['features'])} wards, {len(corridors)} corridors, "
          f"{len(intersections)} hotspots, {len(findings)} findings, "
          f"{len(main_routes_gj['lines'])} main-route lines, "
          f"{len(network_nodes_out['nodes'])} network nodes -> site/data "
          f"(provenance={provenance})")


if __name__ == "__main__":
    main()
