import json

import pytest

import refresh_reporting
from refresh_reporting import guard_provenance, tuples_from_geojson, upsert_meta_sources


def _feat(props):
    return {"type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-87.6, 41.9]},
            "properties": props}


def test_tuples_from_geojson_maps_renamed_keys():
    gj = {"type": "FeatureCollection", "features": [
        _feat({"date": "2026-07-01T10:00:00", "injury_severity": "incapacitating",
               "hit_and_run": True, "dooring": False, "ward": "1"}),
        _feat({"date": "2026-06-15T08:00:00", "injury_severity": "none",
               "hit_and_run": False, "dooring": True, "ward": None}),
    ]}
    tuples = tuples_from_geojson(gj)
    assert tuples[0] == {"date": "2026-07-01", "severity": "incapacitating",
                         "hit_and_run": True, "dooring": False, "ward": "1"}
    assert tuples[1] == {"date": "2026-06-15", "severity": "none",
                         "hit_and_run": False, "dooring": True, "ward": None}


def test_refresh_refuses_non_socrata_provenance():
    # Fixture data must never be re-stamped as reporting truth — see the
    # provenance-stamp history in git (fix: make live pipeline authoritative).
    with pytest.raises(SystemExit):
        guard_provenance({"provenance": "fixtures"})
    with pytest.raises(SystemExit):
        guard_provenance({})
    guard_provenance({"provenance": "socrata"})  # must not raise


def _legacy_meta():
    """A meta.json predating citywide_trend/osm_trails/main_routes/network_nodes —
    e.g. a pre-Contract-v1.7 snapshot — with only the sources that existed then.
    """
    return {"sources": [
        {"id": "crashes"}, {"id": "bike_routes"}, {"id": "sr311"},
        {"id": "cameras"}, {"id": "obstructions"}, {"id": "mellow_routes"},
        {"id": "ward_safety_index"}, {"id": "bikeway_mileage_series"},
        {"id": "council_records"}, {"id": "aldermen_safety_record"},
        {"id": "hearings"}, {"id": "menu_spending"},
    ]}


def test_upsert_meta_sources_legacy_meta_inserts_in_aggregate_consistent_order():
    """A meta.json with none of main_routes/mellow_connectors/osm_trails/
    network_nodes must end up with all four in the exact order aggregate.py's
    main() builds them in: ... mellow_routes, mellow_connectors, osm_trails,
    main_routes, network_nodes, citywide_trend, ward_safety_index, ...

    This is the regression test for the ordering bug: the osm_trails block used
    to anchor on "main_routes" before main_routes had been upserted, so on a
    meta.json lacking both, osm_trails landed at the very end of sources instead
    of immediately before main_routes. mellow_connectors was added alongside
    osm_trails with the same anchor-on-main_routes trick, one block earlier.
    """
    meta = _legacy_meta()
    months = [{"month": "2020-01"}, {"month": "2020-02"}, {"month": "2020-03"}]
    anchor = "2020-03-15"
    # merged-shape layer: ONE feature whose `parts` property carries the
    # kept-part count — that's what records reports (mellow_connector_records)
    mellow_connectors = {"features": [{"properties": {"parts": 3}}]}
    osm_trails = {"features": [{"id": 1}, {"id": 2}]}
    main_routes = {"lines": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}
    network_nodes = {"nodes": [{"id": "node-001"}] * 4}

    upsert_meta_sources(meta, months, anchor, mellow_connectors, osm_trails, main_routes,
                        network_nodes)

    ids = [s["id"] for s in meta["sources"]]
    assert ids == [
        "crashes", "bike_routes", "sr311", "cameras", "obstructions",
        "mellow_routes", "mellow_connectors", "osm_trails", "main_routes", "network_nodes",
        "citywide_trend", "ward_safety_index", "bikeway_mileage_series",
        "council_records", "aldermen_safety_record", "hearings", "menu_spending",
    ]

    by_id = {s["id"]: s for s in meta["sources"]}
    assert by_id["mellow_connectors"] == {
        "id": "mellow_connectors",
        "name": "Mellow Connectors (deduped crowdsourced low-stress links)",
        "tier": "crowdsourced", "records": 3, "date_range": None}
    assert by_id["osm_trails"] == {"id": "osm_trails", "name": "OpenStreetMap Off-street Trails",
                                   "tier": "crowdsourced", "records": 2, "date_range": None}
    assert by_id["main_routes"] == {"id": "main_routes", "name": "Main Routes (curated line roster)",
                                    "tier": "derived", "records": 3, "date_range": None}
    assert by_id["network_nodes"] == {"id": "network_nodes",
                                      "name": "Network Map Nodes (interchanges + orientation points)",
                                      "tier": "derived", "records": 4, "date_range": None}
    assert by_id["citywide_trend"]["records"] == 3


def test_upsert_meta_sources_re_run_updates_in_place_without_reordering():
    """A meta.json that already has all five ids should get their records/tier
    refreshed in place, not moved — running refresh_reporting.py twice in a row
    must be idempotent about source order.
    """
    meta = _legacy_meta()
    months, anchor = [{"month": "2020-01"}], "2020-01-15"
    upsert_meta_sources(meta, months, anchor, {"features": [{"properties": {"parts": 1}}]},
                        {"features": [{"id": 1}]},
                        {"lines": [{"id": "a"}]}, {"nodes": [{"id": "node-001"}]})
    ids_first_pass = [s["id"] for s in meta["sources"]]

    upsert_meta_sources(meta, months, anchor,
                        {"features": [{"properties": {"parts": 2}}]},
                        {"features": [{"id": 1}, {"id": 2}]},
                        {"lines": [{"id": "a"}, {"id": "b"}]},
                        {"nodes": [{"id": "node-001"}, {"id": "node-002"}]})

    assert [s["id"] for s in meta["sources"]] == ids_first_pass
    by_id = {s["id"]: s for s in meta["sources"]}
    assert by_id["mellow_connectors"]["records"] == 2
    assert by_id["osm_trails"]["records"] == 2
    assert by_id["main_routes"]["records"] == 2
    assert by_id["network_nodes"]["records"] == 2


def test_upsert_meta_sources_adds_mellow_connectors_before_existing_osm_trails():
    """Regression test: a meta.json that ALREADY has osm_trails/main_routes/
    network_nodes from a prior run (the realistic case when mellow_connectors
    ships as a new source on an otherwise-populated meta.json) must still land
    mellow_connectors just before osm_trails, not after it. Anchoring on
    "main_routes" alone (main_routes' position, wherever it already is) would
    place mellow_connectors between osm_trails and main_routes instead —
    this is the bug the osm_trails-first anchor check guards against.
    """
    meta = {"sources": [
        {"id": "crashes"}, {"id": "bike_routes"}, {"id": "sr311"},
        {"id": "cameras"}, {"id": "obstructions"}, {"id": "mellow_routes"},
        {"id": "osm_trails"}, {"id": "main_routes"}, {"id": "network_nodes"},
        {"id": "citywide_trend"}, {"id": "ward_safety_index"},
        {"id": "bikeway_mileage_series"}, {"id": "council_records"},
        {"id": "aldermen_safety_record"}, {"id": "hearings"}, {"id": "menu_spending"},
    ]}
    months, anchor = [{"month": "2020-01"}], "2020-01-15"
    upsert_meta_sources(meta, months, anchor, {"features": [{"properties": {"parts": 1}}]},
                        {"features": [{"id": 1}]},
                        {"lines": [{"id": "a"}]}, {"nodes": [{"id": "node-001"}]})
    ids = [s["id"] for s in meta["sources"]]
    assert ids.index("mellow_routes") < ids.index("mellow_connectors") < ids.index("osm_trails") < ids.index("main_routes")


def test_upsert_meta_sources_skips_osm_trails_entry_when_not_rebuilt():
    """upsert_osm_trails=False (offline refresh with no raw Overpass pull, see
    refresh_reporting.main()) must leave any existing osm_trails meta entry
    completely untouched — not overwritten with a records count that doesn't
    reflect what's actually on disk — and must not add a new one either, even
    though osm_trails["features"] is non-empty (the committed file being read
    back as-is almost always has features).
    """
    meta = {"sources": [
        {"id": "crashes"}, {"id": "osm_trails", "name": "stale", "tier": "crowdsourced",
         "records": 269, "date_range": None},
        {"id": "main_routes"},
    ]}
    months, anchor = [{"month": "2020-01"}], "2020-01-15"
    # osm_trails carries plenty of features (as reading back a real committed
    # file would), but upsert_osm_trails=False must still skip it entirely.
    osm_trails = {"features": [{"id": i} for i in range(5)]}
    upsert_meta_sources(meta, months, anchor, {"features": []}, osm_trails,
                        {"lines": [{"id": "a"}]}, {"nodes": [{"id": "node-001"}]},
                        upsert_osm_trails=False)
    by_id = {s["id"]: s for s in meta["sources"]}
    # untouched — same stale dict as before, not re-stamped with records=5
    assert by_id["osm_trails"] == {"id": "osm_trails", "name": "stale", "tier": "crowdsourced",
                                   "records": 269, "date_range": None}


def _minimal_offline_fixture(site_data_dir, osm_trails_features):
    """Write the minimal set of site/data files refresh_reporting.main() needs,
    small enough to run in milliseconds (unlike the real multi-MB committed
    files) — this test cares only about the osm_trails guard, not about
    exercising the full real dataset.
    """
    line = {"type": "LineString", "coordinates": [[-87.65, 41.90], [-87.65, 41.91]]}

    (site_data_dir / "meta.json").write_text(json.dumps({
        "provenance": "socrata", "contract_version": "1.9", "sources": [],
        "generated_at": "2020-01-15T00:00:00+00:00",
    }))
    (site_data_dir / "crashes_cyclist.geojson").write_text(json.dumps({
        "type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": line, "properties": {
                "date": "2020-01-15T00:00:00", "injury_severity": "incapacitating",
                "hit_and_run": False, "dooring": False, "ward": "1"}},
        ]}))
    (site_data_dir / "bikeway_mileage_series.json").write_text(json.dumps({
        "series": [{"date": "2020-01-01", "by_category": {"protected": 5.0, "painted": 2.0},
                    "total": 7.0}],
    }))
    (site_data_dir / "corridors.json").write_text(json.dumps([]))
    (site_data_dir / "wards.geojson").write_text(json.dumps({
        "type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": line,
             "properties": {"ward": "1", "cyclist_crashes": 1}},
        ]}))
    (site_data_dir / "findings.json").write_text(json.dumps([]))
    (site_data_dir / "ward_safety_index.json").write_text(json.dumps({
        "wards": [{"ward": "1"}],
    }))
    (site_data_dir / "bike_routes.geojson").write_text(json.dumps({
        "type": "FeatureCollection", "features": [],
    }))
    # Empty mellow_routes: build_mellow_connectors short-circuits to the stub
    # shape without any geopandas work — keeps this test fast.
    (site_data_dir / "mellow_routes.geojson").write_text(json.dumps({
        "type": "FeatureCollection", "features": [],
    }))
    osm_trails_gj = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": line,
             "properties": {"segment_id": f"osm-trail-fixture-{i}", "name": f"Fixture Trail {i}",
                            "facility_category": "trail", "length_m": 100.0 + i,
                            "data_tier": "crowdsourced"}}
            for i in range(osm_trails_features)
        ],
    }
    (site_data_dir / "osm_trails.geojson").write_text(json.dumps(osm_trails_gj))
    return osm_trails_gj


def test_refresh_offline_run_leaves_committed_osm_trails_untouched_when_raw_absent(
        tmp_path, monkeypatch):
    """Regression test for the offline-refresh-clobbers-real-OSM-trails bug:
    build_osm_trails_layer()'s fallback chain (raw pull > curated fallback >
    stub) means that on a fresh clone where pipeline/raw/ is gitignored and
    absent, rebuilding osm_trails.geojson every offline run would silently
    replace a real committed file with the much smaller curated/stub
    fallback. The fix: refresh_reporting.main() must only rebuild
    osm_trails.geojson when pipeline/raw/osm_trails.json is actually present;
    otherwise the committed file — here seeded with MORE features (8) than
    the repo's real curated fallback (data/curated_trails.geojson, 5
    features) — must be left byte-for-byte untouched.
    """
    site_data_dir = tmp_path / "site_data"
    raw_dir = tmp_path / "raw"  # deliberately left empty: no osm_trails.json
    site_data_dir.mkdir()
    raw_dir.mkdir()

    committed_osm_trails = _minimal_offline_fixture(site_data_dir, osm_trails_features=8)
    before_bytes = (site_data_dir / "osm_trails.geojson").read_bytes()

    monkeypatch.setattr(refresh_reporting, "SITE_DATA_DIR", site_data_dir)
    monkeypatch.setattr(refresh_reporting, "RAW_DIR", raw_dir)
    monkeypatch.setattr("sys.argv", ["refresh_reporting.py"])
    # Not exercising emit_api here — this test is scoped to the osm_trails
    # guard; stub it out so main() doesn't reach for site/data/intersections.json
    # (not part of this minimal fixture) or write outside tmp_path.
    monkeypatch.setattr(refresh_reporting.emit_api, "emit_all", lambda: {})

    refresh_reporting.main()

    after_bytes = (site_data_dir / "osm_trails.geojson").read_bytes()
    assert after_bytes == before_bytes, (
        "offline refresh rewrote osm_trails.geojson even though raw/osm_trails.json "
        "was absent — it must read the committed file back as-is instead")
    after = json.loads(after_bytes)
    assert len(after["features"]) == 8  # not replaced by curated fallback's 5 or the 0-feature stub

    # meta.json must not gain an osm_trails source entry either — this run didn't
    # rebuild it, so there's nothing new to register.
    meta_out = json.loads((site_data_dir / "meta.json").read_text())
    assert not any(s.get("id") == "osm_trails" for s in meta_out["sources"])

    # main_routes/network_nodes still got built from the untouched osm_trails
    # content (fed through unchanged), proving the guard doesn't just skip the
    # whole pipeline.
    assert (site_data_dir / "main_routes.geojson").exists()
    assert (site_data_dir / "network_nodes.json").exists()


def test_refresh_reporting_main_calls_emit_api_at_the_end(tmp_path, monkeypatch):
    # An offline reporting refresh must regenerate site/api/v1/ coherently
    # with the site/data files it just rewrote — otherwise the two go stale
    # relative to each other. Exercise emit_api.emit_all() for real (routed
    # into tmp_path) rather than just stubbing it, so a wiring regression
    # (wrong call site, wrong args, exception swallowed) would show up here.
    site_data_dir = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    raw_dir = tmp_path / "raw"
    site_data_dir.mkdir()
    raw_dir.mkdir()

    _minimal_offline_fixture(site_data_dir, osm_trails_features=3)
    # emit_api additionally reads intersections.json, which refresh_reporting
    # itself never touches.
    (site_data_dir / "intersections.json").write_text(json.dumps([]))

    monkeypatch.setattr(refresh_reporting, "SITE_DATA_DIR", site_data_dir)
    monkeypatch.setattr(refresh_reporting, "RAW_DIR", raw_dir)
    monkeypatch.setattr(refresh_reporting.emit_api, "SITE_DATA_DIR", site_data_dir)
    monkeypatch.setattr(refresh_reporting.emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr("sys.argv", ["refresh_reporting.py"])

    refresh_reporting.main()

    assert (api_dir / "index.json").exists()
    assert (api_dir / "citywide.json").exists()
    assert (api_dir / "corridors.json").exists()
    # The API's generated_at must match the meta.json refresh_reporting just
    # wrote back out — proof emit_api ran AFTER the meta.json rewrite, not
    # against stale data.
    meta_out = json.loads((site_data_dir / "meta.json").read_text())
    index = json.loads((api_dir / "index.json").read_text())
    assert index["_meta"]["generated_at"] == meta_out["generated_at"]
