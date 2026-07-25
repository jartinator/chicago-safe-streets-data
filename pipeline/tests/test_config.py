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


def test_low_stress_categories_are_derived_from_the_grade_map():
    """The two definitions drifted once; they must not be able to drift again.

    MAIN_ROUTE_GRADE_MAP has graded buffered lanes as "paint" since the network-tiers
    work, but a separate hand-written low-stress list in commitments_metrics counted
    buffered as low-stress — so the network map and the findings copy disagreed about
    106 miles. LOW_STRESS_CATEGORIES is now derived from the grade map. This test
    fails if anyone reintroduces a hand-maintained list that diverges.
    """
    from config import (LOW_STRESS_CATEGORIES, LOW_STRESS_GRADES,
                        MAIN_ROUTE_GRADE_MAP, FACILITY_CATEGORIES)

    expected = {c for c, g in MAIN_ROUTE_GRADE_MAP.items() if g in LOW_STRESS_GRADES}
    assert set(LOW_STRESS_CATEGORIES) == expected
    assert set(LOW_STRESS_CATEGORIES) <= set(FACILITY_CATEGORIES)

    # The substantive commitments this encodes, spelled out so a silent grade-map
    # edit has to confront them.
    assert "buffered" not in LOW_STRESS_CATEGORIES, "buffered is paint, not protection"
    assert "painted" not in LOW_STRESS_CATEGORIES
    assert "sharrow" not in LOW_STRESS_CATEGORIES
    assert {"protected", "greenway", "trail"} == set(LOW_STRESS_CATEGORIES)


def test_commitments_metrics_uses_the_shared_definition():
    # Guards against a module-local copy creeping back in.
    import commitments_metrics
    from config import LOW_STRESS_CATEGORIES
    assert commitments_metrics.LOW_STRESS_CATEGORIES is LOW_STRESS_CATEGORIES
