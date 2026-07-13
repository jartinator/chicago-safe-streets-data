"""Aggregate joined data into the versioned static files the site consumes.

Reads raw/* (pull modules or fixtures) plus raw/crashes_joined.json (spatial_join.py)
and writes every contract file into site/data/. This module owns the published
schemas — see SCHEMA.md; do not add/rename output keys without bumping
CONTRACT_VERSION in config.py and updating SCHEMA.md.

Usage: python aggregate.py
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import geopandas as gpd
from shapely.geometry import Point, shape, LineString, MultiLineString
from shapely.ops import unary_union
from shapely.prepared import prep

from config import (RAW_DIR, SITE_DATA_DIR, SNAPSHOT_DIR, FIXTURE_SNAPSHOT_DIR,
                    METRIC_CRS, OUTPUT_CRS,
                    FACILITY_CATEGORY_MAP, FACILITY_CATEGORIES,
                    INJURY_SEVERITY_MAP, CONTRACT_VERSION, CRASH_START_DATE,
                    MAIN_ROUTES_PATH, MAIN_ROUTE_GRADE_MAP, MELLOW_DEDUPE_BUFFER_M,
                    STREET_CLASSES_INCLUDED, STREET_STATUS_INCLUDED,
                    CURATED_TRAILS_PATH, ORIENTATION_POINTS_PATH,
                    SAFETY_TOPIC_KEYWORDS, NEWS_WINDOW_DAYS, NEWS_MAX_ITEMS)
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


# Local equirectangular approximation for Chicago's latitude (~41.85N). Single shared
# definition for build_intersections' crash-cluster grid math and build_network_nodes'
# merge-distance node clustering (_meters_apart below) — both used to hard-code their
# own copy of these constants.
_LAT_M_PER_DEG = 111_320.0
_LON_M_PER_DEG = 83_000.0


def _deg_to_m(dlat, dlon):
    """Convert a (delta-lat, delta-lon) degree offset to (dy_m, dx_m) meters, via the
    shared equirectangular approximation above. Building-block for both callers: used
    directly by build_intersections' grid-cell keys, and by _meters_apart's distance
    formula for build_network_nodes' clustering."""
    return dlat * _LAT_M_PER_DEG, dlon * _LON_M_PER_DEG


def build_intersections(crashes, cell_m=100):
    """Grid-cluster crash points (~cell_m cells) and emit the top hotspots."""
    cells = defaultdict(list)
    for c in crashes:
        lat, lng = float(c["latitude"]), float(c["longitude"])
        y_m, x_m = _deg_to_m(lat, lng)
        key = (round(y_m / cell_m), round(x_m / cell_m))
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


def build_findings(tuples, corridors, wards_gj, as_of_date, road_coverage=None):
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
    return build_findings_core(tuples, by_category_miles, corridors, ward_counts, as_of_date,
                               road_coverage=road_coverage)


def _lengths_m(geometries):
    """Metric length (meters) of each shapely geometry, via the same OUTPUT_CRS ->
    METRIC_CRS (UTM-16N) reprojection every trail/route length in this module uses.
    Shared by build_osm_trails, build_mellow, and build_curated_trails, which each
    used to inline this GeoDataFrame-roundtrip idiom separately."""
    return gpd.GeoDataFrame(geometry=list(geometries), crs=OUTPUT_CRS).to_crs(METRIC_CRS).geometry.length


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
    lengths = _lengths_m(gdf.geometry)
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


def build_mellow_connectors(mellow_gj, routes_gj, buffer_m=MELLOW_DEDUPE_BUFFER_M):
    """Dedupe Mellow Bike Map geometry against the published bike_routes layer,
    emitting the non-overlapping remainder as connector-tier features (network
    tiers v2 design, spec §4, docs/superpowers/specs/2026-07-13-network-tiers-
    design.md). The standalone mellow overlay is retired from the network map;
    this is what replaces it there. `mellow_routes.geojson` itself is untouched
    and keeps shipping for any other page that reads it.

    Takes the PUBLISHED shapes (build_mellow's output + build_routes'/the
    committed bike_routes.geojson's output), so aggregate.py's live path and
    refresh_reporting.py's offline path share this one function and can never
    drift on dedupe logic.

    Mellow's MultiLineStrings arrive pre-chopped into thousands of parts at
    roughly block length already (~25-45 m per part on the real pull — see
    build_mellow's docstring); that's the atomic unit this function drops or
    keeps whole, rather than clipping/splitting a part mid-geometry. A part is
    dropped when it falls within `buffer_m` (projected to METRIC_CRS) of ANY
    published bike_routes segment — bike_routes wins as the higher-provenance
    layer. Performance: with ~60k+ total mellow parts across all route_types,
    testing each part against ~1,000 individually-buffered bike segments would
    be O(parts x segments); instead the buffered bike segments are unioned once
    and wrapped in a shapely PreparedGeometry (`shapely.prepared.prep`), so
    each part pays one fast indexed `.intersects()` call — this is what keeps
    a full run under the ~60s target.

    Output shape: connectors are identity-less by design (spec §1), so the
    kept parts collapse into ONE feature whose geometry is a MultiLineString
    of every surviving part — the same one-big-MultiLineString shape
    mellow_routes.geojson itself uses (Leaflet draws it as one efficient
    multi-part polyline; per-part features would be ~10 MB of mostly-JSON
    property overhead for the same geometry). Coordinates are rounded to 6
    decimal places (~0.1 m). The feature's `parts` property carries the kept
    part count — that's what meta.json's mellow_connectors `records` reports
    (see mellow_connector_records)."""
    mellow_feats = mellow_gj.get("features", [])
    if not mellow_feats:
        # No mellow geometry to dedupe this run — emit the standard stub shape
        # (spec's stub convention: empty FeatureCollection with
        # properties.status/"no_data_yet" + properties.note), NOT a
        # crowdsourced-tier envelope with a top-level data_tier claiming real
        # content over zero features. Matches planned_routes.geojson / the
        # osm_trails empty-stub tier / stub_layer()'s documented shape.
        return stub_layer(
            "No mellow route geometry was available to dedupe this run "
            "(mellow_routes.geojson has no features this run) — see its own note.")

    # Explode every mellow MultiLineString into its individual parts.
    mellow_gdf = gpd.GeoDataFrame(geometry=[shape(f["geometry"]) for f in mellow_feats],
                                  crs=OUTPUT_CRS)
    parts_m = (mellow_gdf.to_crs(METRIC_CRS).explode(index_parts=False)
              .reset_index(drop=True).geometry)
    total_before_m = float(parts_m.length.sum())

    bike_feats = routes_gj.get("features", [])
    if bike_feats:
        bike_gdf = gpd.GeoDataFrame(geometry=[shape(f["geometry"]) for f in bike_feats],
                                    crs=OUTPUT_CRS)
        buffered = bike_gdf.to_crs(METRIC_CRS).geometry.buffer(buffer_m)
        bike_union = prep(unary_union(list(buffered)))
        kept = [geom for geom in parts_m if not bike_union.intersects(geom)]
    else:
        kept = list(parts_m)

    kept_gdf = gpd.GeoDataFrame(geometry=kept, crs=METRIC_CRS)
    kept_lengths = kept_gdf.geometry.length
    kept_ll = kept_gdf.to_crs(OUTPUT_CRS).geometry

    total_after_m = float(kept_lengths.sum())
    dropped_pct = (round(100 * (1 - total_after_m / total_before_m), 1)
                  if total_before_m > 0 else 0.0)

    # One identity-less feature: every kept part as one MultiLineString,
    # coordinates rounded to 6 dp (~0.1 m — plenty for block-level geometry).
    coords = [[[round(x, 6), round(y, 6)] for x, y in geom.coords] for geom in kept_ll]
    feats = []
    if coords:
        feats.append({
            "type": "Feature",
            "geometry": {"type": "MultiLineString", "coordinates": coords},
            "properties": {
                "segment_id": "mellow-connectors",
                "facility_category": "mellow",
                "length_m": round(total_after_m, 1),
                "parts": len(coords),
                "data_tier": "crowdsourced",
            },
        })

    return {
        "type": "FeatureCollection",
        "data_tier": "crowdsourced",
        "note": (f"Mellow Bike Map's low-stress-street geometry, buffer-matched against the "
                 f"published CDOT bike_routes layer ({buffer_m:.0f} m buffer, projected to "
                 f"{METRIC_CRS}) and deduped: mellow ships pre-split into block-length parts, "
                 f"and any part that falls within the buffer of a real bike_routes segment is "
                 f"dropped as a duplicate (bike_routes wins). The remainder ships here as "
                 f"connector-tier geometry (facility_category 'mellow', data_tier "
                 f"crowdsourced) — the network map's replacement for the retired standalone "
                 f"mellow overlay. Connectors are identity-less, so all surviving parts "
                 f"collapse into ONE MultiLineString feature (same shape as "
                 f"mellow_routes.geojson); its `parts` property is the kept-part count, "
                 f"which is also what meta.json reports as this source's `records`. "
                 f"mellow_routes.geojson itself is unchanged and keeps shipping for any "
                 f"other page that reads it. This run dropped {dropped_pct}% of mellow "
                 f"route miles as duplicates of on-street bike infrastructure."),
        "features": feats,
    }


def mellow_connector_records(mellow_connectors_gj):
    """meta.json `records` count for the mellow_connectors source: the kept
    MultiLineString part count (the merged layer has only 1-ish features, so a
    feature count would be meaningless). Shared by aggregate.main() and
    refresh_reporting.upsert_meta_sources so the two paths agree."""
    return sum(f["properties"].get("parts", 0)
               for f in mellow_connectors_gj.get("features", []))


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
    lengths = _lengths_m(shapes)

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
    lengths = _lengths_m(shapes)
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
    aggregate run. Corridor gaps are holes — geometry is never fabricated, and
    every share is computed over member miles only. Street lines aggregate
    real CDOT segments (line stats: derived); trail lines are OSM crowdsourced
    throughout; the two tiers never blend.

    Shared-track membership (network-tiers-v2 design spec §6): a street
    segment is claimed by EVERY roster line whose `streets` list matches it
    (and whose `clip_bbox`, if any, contains the segment's midpoint) — no
    longer first-match-wins. Each such segment is emitted as ONE feature
    carrying `line_ids` (all matching line ids, in roster order) alongside
    `line_id` (line_ids[0], kept for back-compat), and its length/crash counts
    are folded into EVERY matching line's miles_total/miles_by_grade/
    crashes_total. The current roster has no overlapping `streets` lists, so
    on real data every line_ids is length 1 (see test fixtures for the
    multi-membership behavior). Trail matching is unchanged — first-match-wins
    over osm_trails features via `name_tokens` — spec §6 only lifts the
    restriction for bike_routes street matchers.
    """
    street_feats = routes_gj.get("features", [])
    trail_feats = osm_trails_gj.get("features", [])

    # Pre-pass: every roster line id a street segment matches, in roster order.
    # A `streets` entry is either a plain normalized name, or
    # {"name": ..., "clip_bbox": [south, west, north, east]} when the line
    # should claim only part of that street (e.g. the downtown lines sharing
    # just the Loop stretch of RANDOLPH). A per-street clip_bbox overrides
    # the line-level one; both test the segment's geometry midpoint.
    matches_by_seg = defaultdict(list)
    for line in roster["lines"]:
        if line["source"] != "bike_routes":
            continue
        street_bboxes = {}
        for entry in line["streets"]:
            if isinstance(entry, dict):
                street_bboxes[entry["name"]] = entry.get("clip_bbox") or line.get("clip_bbox")
            else:
                street_bboxes[entry] = line.get("clip_bbox")
        for f in street_feats:
            p = f["properties"]
            seg_id = p.get("segment_id")
            name = normalize_street(p.get("street"))
            if name not in street_bboxes:
                continue
            bbox = street_bboxes[name]
            if bbox:
                mid = _geometry_midpoint(f["geometry"])
                if mid is None or not _in_bbox(mid, bbox):
                    continue
            matches_by_seg[seg_id].append(line["id"])

    out_feats = []
    lines_out = []
    claimed_trails = set()
    emitted_street_segs = set()

    for line in roster["lines"]:
        is_street = line["source"] == "bike_routes"
        members = []  # (grade, length_m, crashes)
        if is_street:
            for f in street_feats:
                p = f["properties"]
                seg_id = p.get("segment_id")
                line_ids = matches_by_seg.get(seg_id)
                if not line_ids or line["id"] not in line_ids:
                    continue
                grade = MAIN_ROUTE_GRADE_MAP.get(p.get("facility_category"), "none")
                length_m = float(p.get("length_m") or 0.0)
                crashes = int(p.get("crashes_within_30m") or 0)
                members.append((grade, length_m, crashes))
                if seg_id not in emitted_street_segs:
                    emitted_street_segs.add(seg_id)
                    out_feats.append({
                        "type": "Feature",
                        "geometry": f["geometry"],
                        "properties": {
                            "segment_id": seg_id,
                            # Normalized source street: lets the UI treat a
                            # couplet line (Jackson–Washington) as one chain
                            # per street instead of zigzagging between them.
                            "street": normalize_street(p.get("street")),
                            "line_id": line_ids[0],
                            "line_ids": list(line_ids),
                            "grade": grade,
                            "facility_category": p.get("facility_category"),
                            "length_m": length_m,
                            "crashes_within_30m": crashes,
                            "data_tier": "real",
                        },
                    })
        else:  # osm_trails
            tokens = [t.lower() for t in line["name_tokens"]]
            # exclude_tokens veto a name_tokens match: OSM has distinct
            # trails whose names embed a roster trail's name (e.g. the
            # "Evanston Lakefront Trail" is not Chicago's Lakefront Trail,
            # which ends at Ardmore).
            exclude = [t.lower() for t in line.get("exclude_tokens", [])]
            for f in trail_feats:
                p = f["properties"]
                seg_id = p.get("segment_id")
                if seg_id in claimed_trails:
                    continue
                trail_name = (p.get("name") or "").lower()
                if not any(tok in trail_name for tok in tokens):
                    continue
                if any(tok in trail_name for tok in exclude):
                    continue
                claimed_trails.add(seg_id)
                length_m = float(p.get("length_m") or 0.0)
                members.append(("offstreet", length_m, None))
                out_feats.append({
                    "type": "Feature",
                    "geometry": f["geometry"],
                    "properties": {
                        "segment_id": seg_id,
                        "line_id": line["id"],
                        "line_ids": [line["id"]],
                        "grade": "offstreet",
                        "facility_category": "trail",
                        "length_m": length_m,
                        "data_tier": "crowdsourced",
                    },
                })

        miles_by_grade = defaultdict(float)
        for grade, length_m, _ in members:
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
            entry["crashes_total"] = sum(c for _, _, c in members)
        if not members:
            entry["no_data"] = True
        lines_out.append(entry)

    return {
        "type": "FeatureCollection",
        "data_tier": "derived",
        "note": ("Curated main-route lines assigned from published segments each run. "
                 "The roster is editorial: we chose which corridors count as main routes; "
                 "segment grades and mileage are computed from source data every run. "
                 "Street lines aggregate real CDOT segments (stats: derived tier); trail "
                 "lines come from OpenStreetMap (crowdsourced tier) and never blend into "
                 "derived statistics. Corridor gaps are holes in the line — geometry is "
                 "never fabricated — and grade shares are over existing member miles only. "
                 "A street segment listed by more than one line's `streets` belongs to all "
                 "of them (see `line_ids` on each feature); `line_id` is the first "
                 "roster-order match, kept for back-compat."),
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


def _meters_apart(latlon1, latlon2):
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    dy, dx = _deg_to_m(lat2 - lat1, lon2 - lon1)
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


def _line_bbox(geom):
    """(min_lon, min_lat, max_lon, max_lat) shapely .bounds of geom, padded by the
    150 m node-merge distance. None for an empty/None geometry."""
    if geom is None or geom.is_empty:
        return None
    min_lon, min_lat, max_lon, max_lat = geom.bounds
    return (min_lon - _NODE_MERGE_PAD_LON_DEG, min_lat - _NODE_MERGE_PAD_LAT_DEG,
            max_lon + _NODE_MERGE_PAD_LON_DEG, max_lat + _NODE_MERGE_PAD_LAT_DEG)


def _line_bboxes_disjoint(b1, b2):
    """True when two (min_lon, min_lat, max_lon, max_lat) boxes cannot overlap."""
    return b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1]


def _crossing_points(geom):
    """Yield (lon, lat) crossing points out of a two-line shapely .intersection() result.

    Point/MultiPoint contribute their coordinates directly — an ordinary crossing or a
    shared vertex touch. A LineString/MultiLineString result means the two lines run
    collinear along a shared block (e.g. two roster lines both claiming an overlapping
    stretch of the same street); each such part contributes its true midpoint (by
    length, via shapely's interpolate), one node per overlap. The old hand-rolled
    segment-intersection math had no equivalent for this case and documented it as a
    known miss. GeometryCollection (a pair can mix point touches and collinear
    overlaps at once) is unpacked recursively. Any other geometry type (e.g. an empty
    result) yields nothing.
    """
    if geom is None or geom.is_empty:
        return
    gtype = geom.geom_type
    if gtype == "Point":
        yield (geom.x, geom.y)
    elif gtype == "MultiPoint":
        for p in geom.geoms:
            yield (p.x, p.y)
    elif gtype == "LineString":
        mid = geom.interpolate(0.5, normalized=True)
        yield (mid.x, mid.y)
    elif gtype == "MultiLineString":
        for part in geom.geoms:
            mid = part.interpolate(0.5, normalized=True)
            yield (mid.x, mid.y)
    elif gtype == "GeometryCollection":
        for part in geom.geoms:
            yield from _crossing_points(part)


def build_network_nodes(main_routes_gj, orientation_points):
    """Interchange + orientation nodes for the network map (spec §7,
    docs/superpowers/specs/2026-07-12-network-map-distinction.md).

    Interchanges are derived: each line_id's member feature geometries are merged
    (shapely unary_union) into one geometry per line, and every pair of distinct
    lines is checked via shapely .intersection() for crossing points (see
    _crossing_points — ordinary crossings, shared-vertex touches, and collinear
    shared-block overlaps all contribute a point). Raw crossing points within 150 m
    of each other merge into one node at their centroid, collecting every line_id
    involved; only merged points where >=2 distinct lines meet are emitted as nodes.
    Orientation points are curated wayfinding labels appended verbatim after the
    interchanges, tier derived, lines always empty (they aren't derived from any
    line's geometry).

    Before the .intersection() call for a pair of lines, a cheap line-level bbox
    prefilter (each line's overall shapely .bounds, computed once and padded by the
    150 m merge distance) skips the pair entirely when the boxes can't overlap —
    most roster line pairs are nowhere near each other, so this cuts the dominant
    cost on the full network without changing which intersections are found.
    """
    id_to_name, id_to_order = _line_id_to_name_and_order(main_routes_gj)

    geoms_by_line = defaultdict(list)
    for f in main_routes_gj.get("features", []):
        line_id = f["properties"]["line_id"]
        geoms_by_line[line_id].append(shape(f["geometry"]))

    line_ids = sorted(geoms_by_line)  # deterministic pairing order
    line_geom = {lid: unary_union(geoms_by_line[lid]) for lid in line_ids}
    line_bboxes = {lid: _line_bbox(line_geom[lid]) for lid in line_ids}
    raw_points = []  # (lat, lon, {line_id, line_id})
    for i, a in enumerate(line_ids):
        for b in line_ids[i + 1:]:
            bbox_a, bbox_b = line_bboxes[a], line_bboxes[b]
            if bbox_a is None or bbox_b is None or _line_bboxes_disjoint(bbox_a, bbox_b):
                continue
            inter = line_geom[a].intersection(line_geom[b])
            for lon, lat in _crossing_points(inter):
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


def load_street_centerlines():
    """Filtered surface-street GeoDataFrame from raw/street_centerlines.geojson,
    or None when the pull didn't run. Applies the coverage-denominator filter
    (STREET_CLASSES_INCLUDED x STREET_STATUS_INCLUDED); see DECISIONS.md."""
    path = RAW_DIR / "street_centerlines.geojson"
    if not path.exists():
        print("  WARNING street_centerlines.geojson missing — road coverage metrics "
              "will be null this run (pull_street_centerlines.py did not run)")
        return None
    gj = json.loads(path.read_text())
    feats = [f for f in gj["features"]
             if (f["properties"].get("class") or "") in STREET_CLASSES_INCLUDED
             and (f["properties"].get("status") or "") in STREET_STATUS_INCLUDED
             and f.get("geometry")]
    if not feats:
        return None
    return gpd.GeoDataFrame.from_features(feats, crs=OUTPUT_CRS)


def street_miles_by_ward(streets_gdf, wards_gdf):
    """{ward: surface-street centerline miles} — same clipped-overlay method as
    ward_bikeway_miles, so ratios over the two are method-consistent."""
    streets_m = streets_gdf.to_crs(METRIC_CRS)
    wards_m = wards_gdf.to_crs(METRIC_CRS)[["ward", "geometry"]]
    overlaid = gpd.overlay(streets_m[["geometry"]], wards_m, how="intersection")
    miles = defaultdict(float)
    for _, row in overlaid.iterrows():
        if row.geometry is not None:
            miles[row["ward"]] += row.geometry.length * _MILES_PER_M
    return dict(miles)


def build_road_network(streets_gdf, wards_gdf, routes_gj, as_of_date):
    """road_network.json payload: surface-street miles citywide + per ward, and
    the citywide share of street miles carrying any on-street bike infrastructure.

    routes_gj is the PUBLISHED bike_routes shape (features carry
    facility_category). The numerator excludes the `trail` category — off-street
    trails aren't roads. Both sides of the ratio are projected centerline miles
    (METRIC_CRS), method-consistent even though the citywide mileage series
    prefers CDOT's mi_ctrline field.
    """
    onstreet = [f for f in routes_gj["features"]
                if f["properties"].get("facility_category") != "trail"]
    onstreet_mi = 0.0
    if onstreet:
        g = gpd.GeoDataFrame.from_features(onstreet, crs=OUTPUT_CRS).to_crs(METRIC_CRS)
        onstreet_mi = float(g.geometry.length.sum()) * _MILES_PER_M
    road_mi = float(streets_gdf.to_crs(METRIC_CRS).geometry.length.sum()) * _MILES_PER_M
    ward_road_miles = street_miles_by_ward(streets_gdf, wards_gdf)
    return {
        "data_tier": "real",
        "as_of": as_of_date,
        "note": ("Surface-street centerline miles (Street Center Lines layer, classes "
                 "2/3/4 = arterial/collector/local, status N; expressways, ramps, "
                 "alleys, and river channels excluded) vs on-street bikeway centerline "
                 "miles (trail category excluded). Both sides are projected geometry "
                 "lengths, so the ratio is method-consistent. The city's street "
                 "centerline layer was last updated 2021-06 — the grid changes slowly."),
        "citywide": {
            "road_miles": round(road_mi, 1),
            "onstreet_bikeway_miles": round(onstreet_mi, 1),
            "pct_with_bike_infra": (round(100 * onstreet_mi / road_mi, 1)
                                    if road_mi else None),
        },
        "wards": [{"ward": w, "road_miles": round(m, 2)}
                  for w, m in sorted(ward_road_miles.items(), key=lambda kv: int(kv[0]))],
    }


def ward_coverage_fields(cats, road_miles):
    """The three per-ward coverage fields, from that ward's facility-category miles
    and surface-street miles. Shared by build_ward_safety_index (live) and
    refresh_coverage.py (offline merge) so the two paths cannot drift.
    `trail` is excluded from on-street miles throughout."""
    onstreet = sum(m for c, m in cats.items() if c != "trail")
    rm = road_miles if road_miles and road_miles > 0 else None
    return {
        "bikeway_pct_protected": (round(100 * cats.get("protected", 0.0) / onstreet, 1)
                                  if onstreet > 0 else None),
        "road_miles": round(road_miles, 2) if road_miles is not None else None,
        "bikeway_pct_of_roads": round(100 * onstreet / rm, 1) if rm else None,
    }


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
    build_routes() does. Also accepts the PUBLISHED bike_routes.geojson shape
    (features already carrying a resolved `facility_category` property) — those
    are used directly, with no re-resolution through FACILITY_CATEGORY_MAP.
    """
    feats = routes_gj["features"]
    if not feats:
        return {}
    type_key = _first_key(feats[0]["properties"],
                          ["displayroute", "displayrou", "bikeroute", "type", "facility"])
    unmatched = Counter()

    def _cat(f):
        p = f["properties"]
        if p.get("facility_category"):
            return p["facility_category"]
        return facility_category(str(p.get(type_key)) if type_key else "", unmatched)

    recs = [{"facility_category": _cat(f), "geometry": shape(f["geometry"])}
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
                            tuples=None, road_miles_by_ward=None):
    pop = ward_population()
    miles = ward_bikeway_miles(routes_gj, wards_gdf)
    cats_by_ward = ward_bikeway_miles_by_category(routes_gj, wards_gdf)
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
        rec = {
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
        }
        rec.update(ward_coverage_fields(
            cats_by_ward.get(w, {}),
            road_miles_by_ward.get(w) if road_miles_by_ward else None))
        records.append(rec)
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
                 "denominator and is a meaningful signal, not a data gap. " + infra_note +
                 " bikeway_pct_protected is the protected share of the ward's on-street "
                 "(non-trail) bikeway miles; bikeway_pct_of_roads is the share of the "
                 "ward's surface-street miles (see road_network.json) with any on-street "
                 "bike infrastructure; both are null when the denominator is missing or "
                 "zero."),
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


def decorate_agenda_item(item, tracked_ids):
    """Add the two derived flags the UI keys off: does this agenda item match
    the safety keyword net, and is it already in the published council-records
    set (so the UI can cross-link instead of just naming it)."""
    haystack = f"{item.get('title') or ''} {item.get('agenda_text') or ''}".lower()
    item["safety_keyword_match"] = any(kw in haystack for kw in SAFETY_TOPIC_KEYWORDS)
    item["tracked"] = bool(item.get("record_number")) and item["record_number"] in tracked_ids
    return item


AGENDA_NOTE = (" Agenda items are extracted from the official agenda PDF and matched "
               "to City Clerk records by record number; extraction is best-effort — "
               "the linked PDF is authoritative.")


def build_hearings(council_records=None):
    path = RAW_DIR / "hearings.json"
    if not path.exists():
        return {"data_tier": "real", "as_of": None, "structured_data_available": False,
                "note": "pull_hearings.py did not run this pipeline run.", "committees": []}
    raw = json.loads(path.read_text())
    raw["data_tier"] = "real"

    agenda_path = RAW_DIR / "agenda_items.json"
    if agenda_path.exists():
        agendas = json.loads(agenda_path.read_text()).get("agendas") or {}
        tracked_ids = {r["matter_id"] for r in (council_records or [])
                       if isinstance(r.get("matter_id"), str)}
        merged_any = False
        for committee in raw.get("committees") or []:
            for meeting in committee.get("meetings") or []:
                agenda = agendas.get(meeting.get("agenda_url"))
                if agenda is None:
                    continue  # PDF unfetchable/unparseable — meeting keeps its link only
                meeting["agenda_items"] = [decorate_agenda_item(i, tracked_ids)
                                           for i in agenda.get("items") or []]
                meeting["agenda_amended"] = bool(agenda.get("amended"))
                merged_any = True
        if merged_any and raw.get("note"):
            raw["note"] += AGENDA_NOTE
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


# ---- News coverage ("In the news") -----------------------------------------
# Deterministic entity matching of pulled news items (raw/news.json) against
# entities the site already publishes. Design + persona-validation basis:
# docs/superpowers/specs/2026-07-13-news-coverage-design.md. Precision over
# recall throughout — one wrong match costs more trust than ten misses (4/4
# study participants), so every rule below requires an unambiguous anchor and
# every match records how it was made (`via`), keeping matches auditable.

# "35th Ward" — as a whole publisher tag or inside a headline.
_WARD_TEXT_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\s+Ward\b", re.IGNORECASE)

# Street-name headline matches require a street-type suffix ("Milwaukee
# Avenue" yes, bare "Milwaukee" no — could be the city or the brewery).
_STREET_SUFFIXES = r"(?:Ave(?:nue)?|St(?:reet)?|Blvd|Boulevard|R(?:oa)?d|Dr(?:ive)?)"

# "Today's Headlines for Monday…" — Streetsblog's daily link-roundup digests,
# not original reporting (both straight and curly apostrophes).
_DIGEST_TITLE_RE = re.compile(r"^Today[’']s Headlines", re.IGNORECASE)

# Publisher topic categories that mark an item bike-relevant even when the
# headline lacks a SAFETY_TOPIC_KEYWORDS hit (observed live: Streetsblog
# "Bicycling"/"Complete Streets", Block Club "Bikes").
NEWS_TOPIC_CATEGORIES = {"bicycling", "bikes", "bike lanes", "bike safety",
                         "complete streets", "vision zero", "dooring"}


def _news_relevant(item, feed_kind):
    if _DIGEST_TITLE_RE.search(item.get("title") or ""):
        return False
    if feed_kind == "google_news":
        return True  # the search query itself is the filter
    title = (item.get("title") or "").lower()
    if any(kw in title for kw in SAFETY_TOPIC_KEYWORDS):
        return True
    return any((c or "").lower() in NEWS_TOPIC_CATEGORIES
               for c in item.get("categories") or [])


def _alderman_matchers(aldermen_wards):
    """Per-alderman match patterns from aldermen.json's "Last, First" names.

    Bare surnames never match (amendment B); a surname needs an
    "Ald./Alderman/Alderwoman/Alderperson" honorific in front of it, and a
    surname shared by two alders is matched by full name only.
    """
    parsed = []
    for w in aldermen_wards or []:
        name = (w.get("alderman") or "").strip()
        if "," not in name:
            continue
        last, first = [p.strip() for p in name.split(",", 1)]
        first = first.rstrip(".")
        if last and first:
            parsed.append({"name": name, "ward": w.get("ward"),
                           "surname": last, "full": f"{first} {last}"})
    surname_counts = Counter(p["surname"].lower() for p in parsed)
    for p in parsed:
        pats = [(re.compile(r"\b" + re.escape(p["full"]) + r"\b", re.IGNORECASE),
                 p["full"])]
        if surname_counts[p["surname"].lower()] == 1:
            pats.append((re.compile(
                r"\b(?:Ald\.?|Alderman|Alderwoman|Alderperson)\s+"
                + re.escape(p["surname"]) + r"\b", re.IGNORECASE),
                f"Ald. {p['surname']}"))
        p["patterns"] = pats
    return parsed


def _route_matchers(roster):
    """Per-route match patterns from the main-routes roster: street lines match
    "<Street> <type-suffix>"; trail lines match their name_tokens."""
    matchers = []
    for line in roster.get("lines") or []:
        pats = []
        for street in line.get("streets") or []:
            name = street["name"] if isinstance(street, dict) else street
            display = name.title()
            pats.append((re.compile(
                r"\b" + re.escape(display) + r"\s+" + _STREET_SUFFIXES + r"\b",
                re.IGNORECASE), display))
        for token in line.get("name_tokens") or []:
            pats.append((re.compile(r"\b" + re.escape(token) + r"\b",
                                    re.IGNORECASE), token))
        if pats:
            matchers.append({"id": line["id"], "name": line["name"],
                             "patterns": pats})
    return matchers


def _search_tagged(item, pattern):
    """Where a pattern hits: the matched publisher tag, the headline, or None.
    Publisher tags are checked first — they're the outlet's own indexing and
    the strongest evidence."""
    for cat in item.get("categories") or []:
        if pattern.search(cat):
            return f"publisher tag '{cat}'"
    m = pattern.search(item.get("title") or "")
    if m:
        return f"'{m.group(0)}' in headline"
    return None


def match_news_item(item, alderman_matchers, route_matchers):
    """{wards, aldermen, routes} for one item, every entry carrying `via`."""
    wards, aldermen, routes = [], [], []
    seen_wards = set()

    for cat in item.get("categories") or []:
        m = _WARD_TEXT_RE.search(cat)
        if m and m.group(1) not in seen_wards:
            seen_wards.add(m.group(1))
            wards.append({"ward": m.group(1), "via": f"publisher tag '{cat}'"})
    m = _WARD_TEXT_RE.search(item.get("title") or "")
    if m and m.group(1) not in seen_wards:
        seen_wards.add(m.group(1))
        wards.append({"ward": m.group(1), "via": f"'{m.group(0)}' in headline"})

    for a in alderman_matchers:
        for pattern, label in a["patterns"]:
            where = _search_tagged(item, pattern)
            if where:
                aldermen.append({"name": a["name"], "ward": a["ward"],
                                 "via": where})
                if a["ward"] and a["ward"] not in seen_wards:
                    seen_wards.add(a["ward"])
                    wards.append({"ward": a["ward"],
                                  "via": f"names Ald. {a['surname']} ({where})"})
                break

    for r in route_matchers:
        for pattern, label in r["patterns"]:
            where = _search_tagged(item, pattern)
            if where:
                routes.append({"id": r["id"], "name": r["name"], "via": where})
                break

    return {"wards": wards, "aldermen": aldermen, "routes": routes}


NEWS_NOTE = (
    "Recent public news coverage of Chicago bike/street safety: verbatim "
    "headlines, links, dates, and outlet names from the outlets' own public "
    "RSS feeds — never article text. Matching to wards, alderpersons, and "
    "main routes is computed by exact name rules (each match records how it "
    "was made in `via`) and can miss or, rarely, mismatch; the linked article "
    "is authoritative. These are independent editorial outlets: coverage "
    "listed here is not an endorsement by this site, and absence of coverage "
    "does not mean nothing happened — outlets cover some neighborhoods more "
    "than others.")


def build_news_items(roster):
    """site/data/news_items.json from raw/news.json: relevance-filtered,
    entity-matched, windowed to NEWS_WINDOW_DAYS before the pull's own
    fetched_at (deterministic on re-aggregation), newest first, capped."""
    path = RAW_DIR / "news.json"
    empty = {"data_tier": "real", "match_tier": "derived", "as_of": None,
             "note": NEWS_NOTE, "items": []}
    if not path.exists():
        empty["note"] += " pull_news.py did not run this pipeline run."
        return empty
    raw = json.loads(path.read_text())
    fetched_at = raw.get("fetched_at")
    try:
        anchor = datetime.fromisoformat(fetched_at)
    except (TypeError, ValueError):
        return empty
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=timezone.utc)
    cutoff = anchor - timedelta(days=NEWS_WINDOW_DAYS)

    aldermen_path = SITE_DATA_DIR / "aldermen.json"
    aldermen_wards = (json.loads(aldermen_path.read_text()).get("wards", [])
                      if aldermen_path.exists() else [])
    alderman_matchers = _alderman_matchers(aldermen_wards)
    route_matchers = _route_matchers(roster)

    items = []
    for feed in raw.get("feeds") or []:
        for item in feed.get("items") or []:
            if not _news_relevant(item, feed.get("kind")):
                continue
            try:
                published = datetime.fromisoformat(item["published"])
            except (TypeError, ValueError, KeyError):
                continue  # can't window an undated item — drop, don't guess
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            if published < cutoff:
                continue
            items.append({
                "title": item["title"],
                "url": item["url"],
                "source": item.get("source"),
                "published": item["published"],
                "matches": match_news_item(item, alderman_matchers,
                                           route_matchers),
            })
    items.sort(key=lambda i: i["published"], reverse=True)
    return {"data_tier": "real", "match_tier": "derived", "as_of": fetched_at,
            "note": NEWS_NOTE, "items": items[:NEWS_MAX_ITEMS]}


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

    streets_gdf = load_street_centerlines()
    as_of_date = datetime.now(timezone.utc).date().isoformat()
    if streets_gdf is not None:
        road_network = build_road_network(streets_gdf, wards_gdf, routes_gj, as_of_date)
    else:
        road_network = {"data_tier": "real", "as_of": None,
                        "note": ("Street centerlines were not pulled this run — road "
                                 "coverage metrics are unavailable. Run "
                                 "pull_street_centerlines.py."),
                        "citywide": None, "wards": []}
    road_miles_by_ward = {r["ward"]: r["road_miles"] for r in road_network["wards"]} or None

    corridors = build_corridors(routes_gj, crashes)
    intersections = build_intersections(crashes)

    tuples = crash_tuples(crashes)
    findings = build_findings(tuples, corridors, wards_gj, as_of_date, road_coverage=road_network["citywide"])

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
                                                snapshot_dir, tuples=tuples,
                                                road_miles_by_ward=road_miles_by_ward)
    bikeway_mileage_series = build_bikeway_mileage_series(snapshot_dir)
    name_to_ward = load_name_to_ward()
    council_records_out, council_records_list = build_council_records(name_to_ward)
    aldermen_safety_record = build_aldermen_safety_record(council_records_list, name_to_ward)
    hearings_out = build_hearings(council_records_list)
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

    # Mellow layer retirement + dedupe (network-tiers-v2 spec §4): buffer-match
    # mellow geometry against the just-built bike_routes layer; the deduped
    # remainder ships as its own connector-tier product. mellow_routes.geojson
    # itself is untouched (written unchanged below, for any other page).
    mellow_connectors_gj = build_mellow_connectors(mellow_gj, routes_gj)

    # Priority order (spec §8): real Overpass pull, else the hand-traced curated
    # fallback (data/curated_trails.geojson), else the empty stub.
    osm_trails_gj = build_osm_trails_layer()

    main_routes_roster = load_main_routes_roster()
    main_routes_gj = build_main_routes(routes_gj, osm_trails_gj, main_routes_roster)
    network_nodes_out = build_network_nodes(main_routes_gj, load_orientation_points())
    news_items_out = build_news_items(main_routes_roster)

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
            {"id": "street_centerlines", "name": "Street Center Lines (surface-street grid)",
             "tier": "real",
             "records": int(len(streets_gdf)) if streets_gdf is not None else None,
             "date_range": None},
            {"id": "sr311", "name": "311 Service Requests (bike-related)", "tier": "proxy",
             "records": len(sr311), "date_range": None},
            {"id": "cameras", "name": "Speed/Red-light Camera Violations", "tier": "proxy",
             "records": len(cameras), "date_range": None},
            {"id": "obstructions", "name": "Bike-lane Obstructions", "tier": "mock",
             "records": None, "date_range": None},
        ] + ([{"id": "mellow_routes", "name": "Mellow Bike Map (crowdsourced low-stress streets)",
               "tier": "crowdsourced", "records": len(mellow_gj["features"]), "date_range": None}]
             if mellow_gj["features"] else []) + (
            [{"id": "mellow_connectors", "name": "Mellow Connectors (deduped crowdsourced low-stress links)",
              "tier": "crowdsourced", "records": mellow_connector_records(mellow_connectors_gj),
              "date_range": None}]
             if mellow_connectors_gj["features"] else []) + (
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
            {"id": "news_items", "name": "News Coverage (public RSS headlines)",
             "tier": "real", "records": len(news_items_out["items"]),
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
    write_json(SITE_DATA_DIR / "mellow_connectors.geojson", mellow_connectors_gj)
    write_json(SITE_DATA_DIR / "osm_trails.geojson", osm_trails_gj)
    write_json(SITE_DATA_DIR / "main_routes.geojson", main_routes_gj)
    write_json(SITE_DATA_DIR / "network_nodes.json", network_nodes_out)
    write_json(SITE_DATA_DIR / "ward_safety_index.json", ward_safety_index)
    write_json(SITE_DATA_DIR / "bikeway_mileage_series.json", bikeway_mileage_series)
    write_json(SITE_DATA_DIR / "council_records.json", council_records_out)
    write_json(SITE_DATA_DIR / "aldermen_safety_record.json", aldermen_safety_record)
    write_json(SITE_DATA_DIR / "hearings.json", hearings_out)
    write_json(SITE_DATA_DIR / "menu_spending.json", menu_spending_out)
    write_json(SITE_DATA_DIR / "road_network.json", road_network)
    write_json(SITE_DATA_DIR / "news_items.json", news_items_out)

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
          f"(provenance={provenance})"
          + (f", street coverage: {road_network['citywide']['pct_with_bike_infra']}%"
             if road_network["citywide"] is not None else ""))


if __name__ == "__main__":
    main()
