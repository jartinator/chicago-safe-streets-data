"""Offline refresh of the committed reporting data — no live pull required.

Recomputes findings.json, citywide_trend.json, the windows/monthly fields in
ward_safety_index.json, main_routes.geojson, and mellow_connectors.geojson
from data ALREADY COMMITTED under site/data/ (the last socrata pull), using
the exact same crash_metrics / aggregate.build_main_routes /
aggregate.build_mellow_connectors functions as the live path, so the
published numbers can ship without a multi-hour live run and without logic
drift. The weekly `python run_all.py` remains the canonical path.

Provenance guard: refuses to run when meta.json's provenance is not "socrata" —
fixture/synthetic data must never be re-stamped as reporting truth (see the
provenance-stamp history: fix "make live pipeline authoritative about provenance").

What it deliberately does NOT recompute: per-ward danger scores, geometry-derived
mileage, corridors, or ward crash counts — those need population/geometry/raw
inputs this script doesn't have. Corridors and ward counts are read from the
committed files as-is; protected-share miles come from the latest entry of the
committed bikeway_mileage_series.json (same centerline methodology as the live path).

Usage: python refresh_reporting.py
"""
import argparse
import json

from aggregate import (build_main_routes, load_main_routes_roster,
                       build_osm_trails_layer, build_network_nodes, load_orientation_points,
                       build_mellow_connectors, mellow_connector_records)
from config import SITE_DATA_DIR, CONTRACT_VERSION, CRASH_START_DATE
from crash_metrics import (monthly_counts, per_ward_monthly, window_counts,
                           build_findings_core)
from socrata import write_json


def guard_provenance(meta):
    """Exit rather than re-stamp non-socrata (e.g. fixtures) data as reporting truth."""
    provenance = meta.get("provenance")
    if provenance != "socrata":
        raise SystemExit(
            f"refresh_reporting: site/data/meta.json provenance is {provenance!r}, not "
            "'socrata' — refusing to recompute reporting files from non-live data. "
            "Run `python run_all.py` (live) first.")


def tuples_from_geojson(gj):
    """crashes_cyclist.geojson features -> crash tuples.

    The geojson carries the RENAMED published keys (date, injury_severity,
    hit_and_run, dooring, ward), not the raw Socrata ones aggregate.py reads.
    """
    tuples = []
    for f in gj.get("features", []):
        p = f.get("properties") or {}
        d = (p.get("date") or "")[:10]
        if not d:
            continue
        tuples.append({
            "date": d,
            "severity": p.get("injury_severity"),
            "hit_and_run": bool(p.get("hit_and_run")),
            "dooring": bool(p.get("dooring")),
            "ward": p.get("ward"),
        })
    return tuples


def _load(name):
    return json.loads((SITE_DATA_DIR / name).read_text())


def upsert_meta_sources(meta, months, anchor, mellow_connectors, osm_trails, main_routes,
                        network_nodes):
    """Register/update the citywide_trend, main_routes, mellow_connectors,
    osm_trails, and network_nodes source entries in meta["sources"] in place,
    matching aggregate.py's final ordering exactly: ... mellow_routes,
    mellow_connectors, osm_trails, main_routes, network_nodes, citywide_trend,
    ward_safety_index, ...

    The order these five blocks RUN in matters, not just each entry's target
    position, because later blocks anchor on ids inserted by earlier ones:

    1. citywide_trend anchors on "ward_safety_index" (or list end).
    2. main_routes anchors on "citywide_trend" (now present from step 1), so it
       always lands immediately before it.
    3. mellow_connectors anchors on "main_routes" (now present from step 2), so
       it lands immediately before it.
    4. osm_trails ALSO anchors on "main_routes" (still present) — running this
       block after mellow_connectors means osm_trails' insert lands BETWEEN
       mellow_connectors and main_routes, giving mellow_connectors, osm_trails,
       main_routes in that order — even on a legacy meta.json that has none of
       the three yet. (Anchoring osm_trails on "main_routes" before main_routes
       has been upserted — the original bug — left osm_trails stranded at the
       end of the list on such a meta.json, drifting from aggregate.py's order.)
    5. network_nodes anchors on "citywide_trend" (still present), landing
       immediately after main_routes (since main_routes was inserted just
       before citywide_trend in step 2).
    """
    if not any(s.get("id") == "citywide_trend" for s in meta.get("sources", [])):
        entry = {"id": "citywide_trend", "name": "Citywide Crash Trend (monthly counts)",
                 "tier": "real", "records": len(months),
                 "date_range": [CRASH_START_DATE, anchor]}
        ids = [s.get("id") for s in meta["sources"]]
        pos = ids.index("ward_safety_index") if "ward_safety_index" in ids else len(ids)
        meta["sources"].insert(pos, entry)  # same position as aggregate.py's list

    # main_routes upsert runs BEFORE the osm_trails block below, so that block's
    # "insert just before main_routes" anchor always has a main_routes entry to
    # anchor on, even starting from a legacy meta.json with neither id.
    mr_entry = {"id": "main_routes", "name": "Main Routes (curated line roster)",
                "tier": "derived", "records": len(main_routes["lines"]),
                "date_range": None}
    ids = [s.get("id") for s in meta["sources"]]
    if "main_routes" in ids:
        meta["sources"][ids.index("main_routes")] = mr_entry
    else:
        # aggregate.py places main_routes just before citywide_trend
        pos = ids.index("citywide_trend") if "citywide_trend" in ids else len(ids)
        meta["sources"].insert(pos, mr_entry)

    # mellow_connectors: register/update only when the built layer has features
    # (same conditional pattern as osm_trails below). aggregate.py's list places
    # mellow_connectors just before osm_trails, so anchor on "osm_trails" when
    # it's already present in this meta.json (the common case: everything but
    # mellow_connectors already exists from a prior run). Only fall back to
    # anchoring on "main_routes" when osm_trails ISN'T present yet either — a
    # from-scratch legacy meta, where this block runs before the osm_trails
    # block below, so that block's later "insert just before main_routes"
    # still lands between mellow_connectors and main_routes, in the right order.
    if mellow_connectors["features"]:
        mc_entry = {"id": "mellow_connectors",
                    "name": "Mellow Connectors (deduped crowdsourced low-stress links)",
                    "tier": "crowdsourced",
                    "records": mellow_connector_records(mellow_connectors),
                    "date_range": None}
        ids = [s.get("id") for s in meta["sources"]]
        if "mellow_connectors" in ids:
            meta["sources"][ids.index("mellow_connectors")] = mc_entry
        elif "osm_trails" in ids:
            meta["sources"].insert(ids.index("osm_trails"), mc_entry)
        else:
            pos = ids.index("main_routes") if "main_routes" in ids else len(ids)
            meta["sources"].insert(pos, mc_entry)

    # osm_trails: register/update the source entry only when the layer actually
    # has features (mirrors aggregate.py's conditional inclusion — an empty stub
    # never gets a source entry).
    if osm_trails["features"]:
        osm_entry = {"id": "osm_trails", "name": "OpenStreetMap Off-street Trails",
                     "tier": "crowdsourced", "records": len(osm_trails["features"]),
                     "date_range": None}
        ids = [s.get("id") for s in meta["sources"]]
        if "osm_trails" in ids:
            meta["sources"][ids.index("osm_trails")] = osm_entry
        else:
            # aggregate.py places osm_trails just before main_routes
            pos = ids.index("main_routes") if "main_routes" in ids else len(ids)
            meta["sources"].insert(pos, osm_entry)

    nn_entry = {"id": "network_nodes", "name": "Network Map Nodes (interchanges + orientation points)",
                "tier": "derived", "records": len(network_nodes["nodes"]),
                "date_range": None}
    ids = [s.get("id") for s in meta["sources"]]
    if "network_nodes" in ids:
        meta["sources"][ids.index("network_nodes")] = nn_entry
    else:
        # aggregate.py places network_nodes just after main_routes, before citywide_trend
        pos = ids.index("citywide_trend") if "citywide_trend" in ids else len(ids)
        meta["sources"].insert(pos, nn_entry)


def main():
    argparse.ArgumentParser(
        description="Recompute committed reporting JSON from the last socrata pull."
    ).parse_args()

    meta = _load("meta.json")
    guard_provenance(meta)

    tuples = tuples_from_geojson(_load("crashes_cyclist.geojson"))
    if not tuples:
        raise SystemExit("refresh_reporting: no crash tuples in crashes_cyclist.geojson")

    # Protected share: latest committed mileage snapshot (CDOT centerline methodology,
    # same as the live path); the trail exclusion happens inside protected_share.
    series = _load("bikeway_mileage_series.json")["series"]
    if not series:
        raise SystemExit("refresh_reporting: bikeway_mileage_series.json has no snapshots")
    by_category_miles = series[-1]["by_category"]
    as_of_date = series[-1]["date"]

    road_path = SITE_DATA_DIR / "road_network.json"
    road_coverage = None
    if road_path.exists():
        road_coverage = (json.loads(road_path.read_text()) or {}).get("citywide")

    corridors = _load("corridors.json")
    ward_counts = {f["properties"]["ward"]: f["properties"]["cyclist_crashes"]
                   for f in _load("wards.geojson")["features"]}

    old_ids = [f["id"] for f in _load("findings.json")]
    findings = build_findings_core(tuples, by_category_miles, corridors, ward_counts,
                                   as_of_date, road_coverage=road_coverage)
    write_json(SITE_DATA_DIR / "findings.json", findings)

    # Citywide monthly trend — identical assembly to aggregate.main().
    anchor = max(t["date"] for t in tuples)
    months = monthly_counts(tuples, CRASH_START_DATE[:7], anchor[:7])
    citywide_trend = {
        "data_tier": "real",
        "window_end": anchor,
        "note": ("Monthly counts of police-reported cyclist crashes citywide since Sept 2017; "
                 "ksi = crashes whose worst injury was fatal or incapacitating (\"killed or "
                 "seriously injured\"). Recent months are provisional — records get amended."),
        "months": months,
    }
    write_json(SITE_DATA_DIR / "citywide_trend.json", citywide_trend)

    # Merge windows/monthly into the existing ward records in place — danger scores,
    # trends, and mileage need inputs this script doesn't have and are left untouched.
    wsi = _load("ward_safety_index.json")
    start_month, end_month = CRASH_START_DATE[:7], anchor[:7]
    ward_monthly = per_ward_monthly(tuples, start_month, end_month)
    tuples_by_ward = {}
    for t in tuples:
        if t["ward"]:
            tuples_by_ward.setdefault(t["ward"], []).append(t)
    for rec in wsi["wards"]:
        w = rec["ward"]
        rec["windows"] = window_counts(tuples_by_ward.get(w, []), anchor)
        rec["monthly"] = ward_monthly.get(w) or monthly_counts([], start_month, end_month)
    write_json(SITE_DATA_DIR / "ward_safety_index.json", wsi)

    # osm_trails: rebuild from the same priority-ordered source aggregate.py uses
    # (live Overpass pull, else the hand-traced curated fallback, else the stub —
    # spec §8), not just read back the possibly-stale committed file, so a curated
    # trail addition/edit takes effect on the next offline refresh too.
    osm_trails = build_osm_trails_layer()
    write_json(SITE_DATA_DIR / "osm_trails.geojson", osm_trails)

    # Main routes: rebuild the curated-line layer from the committed CDOT segments
    # + the just-rebuilt OSM trails + checked-in roster, via the exact same
    # build_main_routes the live aggregate path calls (no logic drift possible).
    main_routes = build_main_routes(_load("bike_routes.geojson"),
                                    osm_trails,
                                    load_main_routes_roster())
    write_json(SITE_DATA_DIR / "main_routes.geojson", main_routes)

    # Network nodes: derived interchanges (exact intersections between roster
    # lines) + curated orientation points (spec §7), rebuilt from the main_routes
    # layer just written above.
    network_nodes = build_network_nodes(main_routes, load_orientation_points())
    write_json(SITE_DATA_DIR / "network_nodes.json", network_nodes)

    # Mellow connectors: rebuild the deduped-remainder connector layer from the
    # committed mellow_routes + bike_routes, via the exact same
    # build_mellow_connectors the live aggregate path calls (no logic drift
    # possible). mellow_routes.geojson itself is read back as-is below, unchanged.
    mellow_connectors = build_mellow_connectors(_load("mellow_routes.geojson"),
                                                _load("bike_routes.geojson"))
    write_json(SITE_DATA_DIR / "mellow_connectors.geojson", mellow_connectors)

    # meta.json: stamp the (possibly newer) contract version and register the
    # citywide_trend / main_routes / mellow_connectors / osm_trails /
    # network_nodes sources if this meta predates them (see upsert_meta_sources
    # for the ordering rationale). generated_at stays — it describes the
    # underlying pull, which this script does not redo.
    meta["contract_version"] = CONTRACT_VERSION
    upsert_meta_sources(meta, months, anchor, mellow_connectors, osm_trails, main_routes,
                        network_nodes)
    write_json(SITE_DATA_DIR / "meta.json", meta)

    print(f"refresh_reporting: {len(tuples)} crash tuples through {anchor}")
    print(f"  findings: {old_ids} -> {[f['id'] for f in findings]}")
    print(f"  citywide_trend: {len(months)} months; ward_safety_index: "
          f"{len(wsi['wards'])} wards got windows+monthly; "
          f"contract_version={CONTRACT_VERSION}")
    print(f"  main_routes: {len(main_routes['features'])} member segments across "
          f"{len(main_routes['lines'])} lines:")
    for ln in main_routes["lines"]:
        pct = ln.get("pct_protected")
        pct_s = f"{pct:5.1f}% protected" if pct is not None else " " * 16
        flag_s = "  NO DATA" if ln.get("no_data") else ""
        print(f"    {ln['id']:<20} {ln['miles_total']:6.2f} mi  {pct_s}{flag_s}")
    print(f"  osm_trails: {len(osm_trails['features'])} trail features; "
          f"network_nodes: {len(network_nodes['nodes'])} nodes")
    mc_miles = sum(f["properties"]["length_m"] for f in mellow_connectors["features"]) / 1609.34
    print(f"  mellow_connectors: {len(mellow_connectors['features'])} feature(s), "
          f"{mellow_connector_records(mellow_connectors)} parts, {mc_miles:.2f} mi")


if __name__ == "__main__":
    main()
