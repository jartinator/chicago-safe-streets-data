import pytest

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
