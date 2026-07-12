import make_fixtures
import aggregate


def test_bike_routes_fixture_has_no_offstreet_trail():
    # CDOT's real layer is on-street only; the fixture must match that shape so
    # trails don't appear in two layers. Off-street trails live in osm_trails now.
    labels = {c[2] for c in make_fixtures.CORRIDORS}
    assert "OFF-STREET TRAIL" not in labels


def test_osm_trails_fixture_shapes_into_trail_features():
    raw = make_fixtures.build_osm_trails_raw()
    out = aggregate.build_osm_trails(raw)
    names = {f["properties"]["name"] for f in out["features"]}
    assert "Lakefront Trail" in names
    assert all(f["properties"]["data_tier"] == "crowdsourced" for f in out["features"])
    assert all(f["properties"]["facility_category"] == "trail" for f in out["features"])
