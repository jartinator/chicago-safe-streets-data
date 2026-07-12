import config


def test_councilmatic_url_is_unhashed_base():
    # Must be the un-hashed base so the nightly content-hash change can't break us.
    assert config.COUNCILMATIC_DATASETTE_URL == "https://puddle.datamade.us/chicago_council"


def test_osm_trails_query_config_present_and_filtered():
    import config
    assert config.OVERPASS_API_URL.startswith("https://")
    # bbox is (south, west, north, east) covering Chicago + North Branch Trail north extent
    assert config.OSM_TRAILS_BBOX == (41.60, -87.95, 42.20, -87.50)
    q = config.OSM_TRAILS_QUERY
    # de-dup: road-parallel cycle tracks (is_sidepath=yes) are excluded at query time
    assert '"is_sidepath"!="yes"' in q
    # only named off-street ways
    assert '"name"' in q
    assert '"highway"="cycleway"' in q
    # bbox coordinates are interpolated into the query
    assert "41.6" in q and "-87.95" in q
