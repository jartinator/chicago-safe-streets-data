"""Offline refresh of the committed reporting data — no live pull required.

Recomputes findings.json, citywide_trend.json, the windows/monthly fields in
ward_safety_index.json, main_routes.geojson, and mellow_connectors.geojson
from data ALREADY COMMITTED under site/data/ (the last socrata pull), using
the exact same crash_metrics / aggregate.build_main_routes /
aggregate.build_mellow_connectors functions as the live path, so the
published numbers can ship without a multi-hour live run and without logic
drift. The weekly `python run_all.py` remains the canonical path.

Finishes by calling emit_api.emit_all() so site/api/v1/ stays coherent with
the site/data/ files this script just rewrote.

Provenance guard: refuses to run when meta.json's provenance is not "socrata" —
fixture/synthetic data must never be re-stamped as reporting truth (see the
provenance-stamp history: fix "make live pipeline authoritative about provenance").

What it deliberately does NOT recompute: per-ward danger scores, geometry-derived
mileage, corridors, or ward crash counts — those need population/geometry/raw
inputs this script doesn't have. Corridors and ward counts are read from the
committed files as-is; protected-share miles come from the latest entry of the
committed bikeway_mileage_series.json (same centerline methodology as the live path).

Invariant: an offline run never mutates data it can't rebuild at least as well.
osm_trails.geojson is only rebuilt when pipeline/raw/osm_trails.json (a real
Overpass pull) is present; otherwise the committed file is read back as-is and
fed unchanged into main_routes/network_nodes, so a fresh clone (raw/ is
gitignored and normally absent) can never silently downgrade the committed
real-OSM trails to the smaller curated/stub fallback.

Usage: python refresh_reporting.py
"""
import argparse
import json

import emit_api
from aggregate import (build_main_routes, load_main_routes_roster,
                       build_osm_trails_layer, build_network_nodes, load_orientation_points,
                       build_mellow_connectors, mellow_connector_records, build_bna,
                       build_news_items, build_proposed_projects,
                       load_proposed_projects_roster, crash_trend)
from bna_metrics import build_bna_finding
from config import SITE_DATA_DIR, RAW_DIR, CONTRACT_VERSION, CRASH_START_DATE
from crash_metrics import (monthly_counts, per_ward_monthly, window_counts,
                           build_findings_core, check_trend_window_consistency)
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


def apply_bna(findings, raw_is_fixture=False):
    """Append the PFB BNA finding, rewriting bna_scores.json only from a raw pull.

    findings.json is fully rebuilt by this script, so the BNA card must be
    re-appended from whatever source exists — aggregate.build_bna's priority
    chain (raw/bna.json > committed site/data/bna_scores.json > None). But the
    committed file itself follows the osm_trails invariant (never mutate data
    this run can't rebuild at least as well): only a real raw pull rewrites it.
    raw_is_fixture (a --fixtures run's raw/bna.json) is treated as absent, same
    as osm_trails/news elsewhere in this script. Returns
    (bna_scores_or_None, rebuilt_from_raw).
    """
    rebuilt = (RAW_DIR / "bna.json").exists() and not raw_is_fixture
    bna = build_bna(ignore_raw=raw_is_fixture)
    if bna:
        findings.append(build_bna_finding(bna))
        if rebuilt:
            write_json(SITE_DATA_DIR / "bna_scores.json", bna)
    return bna, rebuilt


def upsert_meta_sources(meta, months, anchor, mellow_connectors, osm_trails, main_routes,
                        network_nodes, upsert_osm_trails=True,
                        bna_scores=None, upsert_bna=False,
                        news_items=None, proposed_projects=None):
    """Register/update the citywide_trend, main_routes, mellow_connectors,
    osm_trails, and network_nodes source entries in meta["sources"] in place,
    matching aggregate.py's final ordering exactly: ... mellow_routes,
    mellow_connectors, osm_trails, main_routes, network_nodes, citywide_trend,
    ward_safety_index, ... (plus a sixth, order-independent block at the end
    of this function: news_items, appended last, only when this run rebuilt
    the news layer from a real raw pull).

    The order these five blocks RUN in matters, not just each entry's target
    position, because later blocks anchor on ids inserted by earlier ones:

    1. citywide_trend anchors on "ward_safety_index" (or list end).
    2. main_routes anchors on "citywide_trend" (now present from step 1), so it
       always lands immediately before it.
    3. mellow_connectors anchors on "osm_trails" if present, else "main_routes"
       (now present from step 2), so it lands immediately before whichever is
       there.
    4. osm_trails ALSO anchors on "main_routes" (still present) — running this
       block after mellow_connectors means osm_trails' insert lands BETWEEN
       mellow_connectors and main_routes, giving mellow_connectors, osm_trails,
       main_routes in that order — even on a legacy meta.json that has none of
       the three yet. (Anchoring osm_trails on "main_routes" before main_routes
       has been upserted — the original bug — left osm_trails stranded at the
       end of the list on such a meta.json, drifting from aggregate.py's order.)
       Skipped entirely when upsert_osm_trails is False (offline refresh with
       no raw Overpass pull to rebuild from — see refresh_reporting.main()).
    5. network_nodes anchors on "citywide_trend" (still present), landing
       immediately after main_routes (since main_routes was inserted just
       before citywide_trend in step 2).

    All five blocks funnel through the single `_upsert` helper below: update
    the existing entry in place (unless update_if_present=False), or insert a
    new one at the position of the first present id in `anchor_ids` (else at
    the list's end). Each block still computes ids fresh via `_upsert` itself,
    so the anchor-chaining behavior described above is unchanged.
    """
    def _upsert(id_, entry, anchor_ids, update_if_present=True):
        ids = [s.get("id") for s in meta["sources"]]
        if id_ in ids:
            if update_if_present:
                meta["sources"][ids.index(id_)] = entry
            return
        pos = len(ids)
        for anchor_id in anchor_ids:
            if anchor_id in ids:
                pos = ids.index(anchor_id)
                break
        meta["sources"].insert(pos, entry)

    # citywide_trend: insert-only if absent — unlike the other four, an
    # existing entry is never overwritten here (its own block above already
    # wrote the current month's data via write_json).
    ct_entry = {"id": "citywide_trend", "name": "Citywide Crash Trend (monthly counts)",
                "tier": "real", "records": len(months),
                "date_range": [CRASH_START_DATE, anchor]}
    _upsert("citywide_trend", ct_entry, anchor_ids=["ward_safety_index"],
           update_if_present=False)

    # main_routes upsert runs BEFORE the osm_trails block below, so that block's
    # "insert just before main_routes" anchor always has a main_routes entry to
    # anchor on, even starting from a legacy meta.json with neither id.
    mr_entry = {"id": "main_routes", "name": "Main Routes (curated line roster)",
                "tier": "derived", "records": len(main_routes["lines"]),
                "date_range": None}
    _upsert("main_routes", mr_entry, anchor_ids=["citywide_trend"])

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
        _upsert("mellow_connectors", mc_entry, anchor_ids=["osm_trails", "main_routes"])

    # osm_trails: register/update the source entry only when the layer actually
    # has features (mirrors aggregate.py's conditional inclusion — an empty stub
    # never gets a source entry) AND this run actually rebuilt it — an offline
    # refresh with no raw Overpass pull leaves the committed osm_trails.geojson
    # (and its meta entry) untouched rather than re-stamping it from a file it
    # didn't regenerate.
    if upsert_osm_trails and osm_trails["features"]:
        osm_entry = {"id": "osm_trails", "name": "OpenStreetMap Off-street Trails",
                     "tier": "crowdsourced", "records": len(osm_trails["features"]),
                     "date_range": None}
        _upsert("osm_trails", osm_entry, anchor_ids=["main_routes"])

    # bna_scores: aggregate.py's order places it between osm_trails and
    # main_routes. Running this block after the osm_trails block, anchored on
    # "main_routes" (guaranteed present from step 2), lands it exactly there.
    # Same rebuild gating as osm_trails: only a run that actually re-pulled
    # (upsert_bna=True) registers/updates the entry.
    if upsert_bna and bna_scores:
        bna_entry = {"id": "bna_scores",
                     "name": "PeopleForBikes BNA City Rating (citywide scorecard)",
                     "tier": "crowdsourced",
                     "records": len(bna_scores.get("history") or []),
                     "date_range": ([bna_scores["history"][0]["as_of"], bna_scores["as_of"]]
                                    if bna_scores.get("history") and bna_scores.get("as_of")
                                    else None)}
        _upsert("bna_scores", bna_entry, anchor_ids=["main_routes"])

    nn_entry = {"id": "network_nodes", "name": "Network Map Nodes (interchanges + orientation points)",
                "tier": "derived", "records": len(network_nodes["nodes"]),
                "date_range": None}
    _upsert("network_nodes", nn_entry, anchor_ids=["citywide_trend"])

    # news_items: register/update only when this run actually rebuilt the
    # layer from a real raw pull (news_items=None otherwise — same
    # rebuilt-this-run posture as osm_trails above). aggregate.py places it
    # last in the sources list, so no anchor: insert at the end.
    if news_items is not None:
        news_entry = {"id": "news_items", "name": "News Coverage (public RSS headlines)",
                      "tier": "real", "records": len(news_items["items"]),
                      "date_range": None}
        _upsert("news_items", news_entry, anchor_ids=[])

    # proposed_projects: rebuilt together with news_items (it joins the
    # roster to the fresh news matches), so it upserts under the same
    # rebuilt-this-run condition. Appended last, after news_items.
    if proposed_projects is not None:
        pp_entry = {"id": "proposed_projects",
                    "name": "Proposed & In-Progress Bikeway Projects (curated roster)",
                    "tier": "derived",
                    "records": len(proposed_projects["projects"]),
                    "date_range": None}
        _upsert("proposed_projects", pp_entry, anchor_ids=[])


def main():
    argparse.ArgumentParser(
        description="Recompute committed reporting JSON from the last socrata pull."
    ).parse_args()

    meta = _load("meta.json")
    guard_provenance(meta)

    # Raw files left by a --fixtures run (raw/PROVENANCE says "fixtures") are
    # synthetic — treat them as absent everywhere below, or fixture geometry/
    # headlines/scores get re-stamped over committed real data. Computed early
    # so every rebuild-from-raw check (osm_trails, news, bna) can use it.
    raw_provenance_path = RAW_DIR / "PROVENANCE"
    raw_is_fixture = (raw_provenance_path.exists()
                      and raw_provenance_path.read_text().strip() == "fixtures")

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
    # PFB BNA scorecard card (B1) — re-appended from raw pull or committed
    # bna_scores.json so the full findings rebuild doesn't drop it.
    bna_scores_out, bna_rebuilt = apply_bna(findings, raw_is_fixture=raw_is_fixture)
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

    # Merge windows/monthly/crash_trend into the existing ward records in place —
    # danger scores and mileage need inputs this script doesn't have and are left
    # untouched. crash_trend IS recomputed here: it shares the windows anchor
    # (the global latest crash date), and leaving the committed one in place
    # would let the two blocks drift apart between a live pull and an offline
    # refresh.
    wsi = _load("ward_safety_index.json")
    start_month, end_month = CRASH_START_DATE[:7], anchor[:7]
    ward_monthly = per_ward_monthly(tuples, start_month, end_month)
    tuples_by_ward = {}
    for t in tuples:
        if t["ward"]:
            tuples_by_ward.setdefault(t["ward"], []).append(t)
    for rec in wsi["wards"]:
        w = rec["ward"]
        ward_tuples = tuples_by_ward.get(w, [])
        rec["crash_trend"] = crash_trend([t["date"] for t in ward_tuples],
                                         anchor_date=anchor)
        rec["windows"] = window_counts(ward_tuples, anchor)
        rec["monthly"] = ward_monthly.get(w) or monthly_counts([], start_month, end_month)
        check_trend_window_consistency(rec["crash_trend"], rec["windows"], f"ward {w}")
    write_json(SITE_DATA_DIR / "ward_safety_index.json", wsi)

    # osm_trails: only rebuild when a real Overpass pull (pipeline/raw/osm_trails.json,
    # gitignored) is actually present. Offline refresh never mutates data it can't
    # rebuild at least as well: build_osm_trails_layer()'s fallback chain (raw >
    # curated > stub) means that on a fresh clone with raw/ absent, "rebuilding"
    # would silently replace the committed real-OSM osm_trails.geojson with the
    # much smaller curated/stub fallback, then cascade that degradation into
    # main_routes.geojson and network_nodes.json. So: rebuild only when raw_path
    # exists (a curated_trails.geojson edit then does take effect, same as
    # before); otherwise read the committed file back as-is and feed it into
    # build_main_routes/build_network_nodes unchanged — this is what the
    # pre-v2 script did. raw_is_fixture (computed above) applies the same
    # fixtures-are-absent rule here as everywhere else.
    osm_raw_path = RAW_DIR / "osm_trails.json"
    rebuild_osm_trails = osm_raw_path.exists() and not raw_is_fixture
    if osm_raw_path.exists() and raw_is_fixture:
        print(f"  osm_trails: {osm_raw_path} is from a --fixtures run — left "
              f"committed site/data/osm_trails.geojson untouched")
    if rebuild_osm_trails:
        osm_trails = build_osm_trails_layer()
        write_json(SITE_DATA_DIR / "osm_trails.geojson", osm_trails)
        print(f"  osm_trails: rebuilt from {osm_raw_path} "
              f"({len(osm_trails['features'])} features)")
    else:
        osm_trails = _load("osm_trails.geojson")
        print(f"  osm_trails: {osm_raw_path} absent — left committed "
              f"site/data/osm_trails.geojson untouched "
              f"({len(osm_trails.get('features', []))} features)")

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

    # News items: only rebuild when a real feed pull (pipeline/raw/news.json,
    # gitignored) is present — same never-downgrade invariant as osm_trails
    # above (build_news_items with no raw file would replace a committed real
    # list with an honest-but-empty one).
    news_raw_path = RAW_DIR / "news.json"
    news_items = None
    proposed = None
    if news_raw_path.exists() and raw_is_fixture:
        print(f"  news_items: {news_raw_path} is from a --fixtures run — left "
              f"committed site/data/news_items.json untouched")
    elif news_raw_path.exists():
        projects_roster = load_proposed_projects_roster()
        news_items = build_news_items(load_main_routes_roster(), projects_roster)
        write_json(SITE_DATA_DIR / "news_items.json", news_items)
        # The proposed-projects file is a pure function of the checked-in
        # roster + the news items just rebuilt, so it refreshes with them.
        proposed = build_proposed_projects(projects_roster, news_items)
        write_json(SITE_DATA_DIR / "proposed_projects.json", proposed)
        print(f"  news_items: rebuilt from {news_raw_path} "
              f"({len(news_items['items'])} items); proposed_projects: "
              f"{len(proposed['projects'])} projects")
    else:
        print(f"  news_items: {news_raw_path} absent — left committed "
              f"site/data/news_items.json and proposed_projects.json untouched")

    # meta.json: stamp the (possibly newer) contract version and register the
    # citywide_trend / main_routes / mellow_connectors / osm_trails /
    # network_nodes sources if this meta predates them (see upsert_meta_sources
    # for the ordering rationale). generated_at stays — it describes the
    # underlying pull, which this script does not redo.
    meta["contract_version"] = CONTRACT_VERSION
    upsert_meta_sources(meta, months, anchor, mellow_connectors, osm_trails, main_routes,
                        network_nodes, upsert_osm_trails=rebuild_osm_trails,
                        bna_scores=bna_scores_out, upsert_bna=bna_rebuilt,
                        news_items=news_items, proposed_projects=proposed)
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

    # Regenerate site/api/v1/ so it stays coherent with the site/data/ files
    # just rewritten above, rather than drifting stale until the next live run.
    emit_api.emit_all()


if __name__ == "__main__":
    main()
