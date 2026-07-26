import json

import aggregate

# One bike_routes segment running north-south along lon -87.650.
BIKE_LON = -87.650
ROUTES_GJ = {"type": "FeatureCollection", "features": [
    {"type": "Feature",
     "geometry": {"type": "LineString",
                  "coordinates": [[BIKE_LON, 41.800], [BIKE_LON, 41.810]]},
     "properties": {"segment_id": "b1", "facility_category": "protected"}},
]}

# A mellow MultiLineString with two parts (mellow ships pre-split into parts,
# see build_mellow's docstring): one ~5 m from the bike route (well within
# the 25 m dedupe buffer -> dropped) and one ~830 m east of it (well outside
# the buffer -> survives as connector geometry).
OVERLAPPING_PART = [[BIKE_LON + 0.00006, 41.800], [BIKE_LON + 0.00006, 41.805]]
DISTANT_PART = [[BIKE_LON + 0.01, 41.800], [BIKE_LON + 0.01, 41.805]]
MELLOW_GJ = {"type": "FeatureCollection", "features": [
    {"type": "Feature",
     "geometry": {"type": "MultiLineString", "coordinates": [OVERLAPPING_PART, DISTANT_PART]},
     "properties": {"segment_id": "mellow-street", "route_type": "street"}},
]}


def test_overlapping_part_dropped_distant_part_survives():
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    # everything kept collapses into ONE merged MultiLineString feature
    assert len(out["features"]) == 1
    f = out["features"][0]
    assert f["geometry"]["type"] == "MultiLineString"
    parts = f["geometry"]["coordinates"]
    # only the distant part survived the dedupe
    assert len(parts) == 1
    assert f["properties"]["parts"] == 1
    # its geometry is the distant part, not the dropped overlapping one
    assert abs(parts[0][0][0] - (BIKE_LON + 0.01)) < 1e-6
    # length_m is the surviving 0.005-degree-latitude part (~556 m)
    assert 500 < f["properties"]["length_m"] < 600


def test_connector_feature_shape():
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    f = out["features"][0]
    props = f["properties"]
    assert props["segment_id"] == "mellow-connectors"
    assert props["facility_category"] == "mellow"
    assert props["data_tier"] == "crowdsourced"
    assert isinstance(props["length_m"], float)
    assert props["parts"] == len(f["geometry"]["coordinates"])
    # no leftover mellow-specific properties (route_type, etc.) leak through
    assert set(props) == {"segment_id", "facility_category", "length_m", "parts", "data_tier"}


def test_coordinates_rounded_to_6dp():
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    for part in out["features"][0]["geometry"]["coordinates"]:
        for x, y in part:
            assert x == round(x, 6)
            assert y == round(y, 6)


def test_top_level_shape_and_note():
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    assert out["type"] == "FeatureCollection"
    assert out["data_tier"] == "crowdsourced"
    assert "25" in out["note"]  # buffer distance
    assert "%" in out["note"]  # dropped-fraction callout
    assert "parts" in out["note"]  # records-count semantics documented


def test_no_bike_routes_keeps_every_mellow_part():
    empty_routes = {"type": "FeatureCollection", "features": []}
    out = aggregate.build_mellow_connectors(MELLOW_GJ, empty_routes)
    # both parts of the one mellow feature survive — nothing to dedupe against —
    # still merged into one feature
    assert len(out["features"]) == 1
    f = out["features"][0]
    assert f["properties"]["parts"] == 2
    assert len(f["geometry"]["coordinates"]) == 2


def test_no_mellow_features_returns_stub_shape():
    # Matches the project's stub convention (stub_layer()): empty
    # FeatureCollection with properties.status/"no_data_yet" + properties.note,
    # and NO top-level data_tier claiming real (crowdsourced) content.
    empty_mellow = {"type": "FeatureCollection", "features": []}
    out = aggregate.build_mellow_connectors(empty_mellow, ROUTES_GJ)
    assert out["type"] == "FeatureCollection"
    assert out["features"] == []
    assert "data_tier" not in out
    assert out["properties"]["status"] == "no_data_yet"
    assert out["properties"]["note"]


def test_everything_deduped_away_yields_zero_features():
    # With a huge buffer, every part (including the "distant" one ~830 m away)
    # is dropped — no zero-part feature is emitted, features is just empty.
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ, buffer_m=1000.0)
    assert out["features"] == []


def test_custom_buffer_distance_narrows_the_drop():
    # With a tiny buffer, even the "overlapping" part (~5 m away) survives.
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ, buffer_m=1.0)
    assert out["features"][0]["properties"]["parts"] == 2


# --- reproducible output -----------------------------------------------------
# site/data/mellow_connectors.geojson used to come back modified after every
# `python refresh_reporting.py`, showing as a ~4.3 MB whole-file diff (the layer
# is one long line). The parts kept were always the same and always in the same
# order; ~1,000 of them differed in the 6th decimal place by exactly 1 unit.
# Cause: the emitted coordinates were read back out of a METRIC_CRS round trip
# (lon/lat -> UTM-16N -> lon/lat) instead of off the input geometry. Mellow ships
# 7-decimal coordinates, so ~10% of them land exactly on a 6-dp rounding tie;
# a round trip lands a hair either side of that tie depending on the platform's
# PROJ/libm build, and round() then flips the last digit. The projection is still
# needed for the dedupe buffer and for length_m — it just must not be the source
# of the coordinates that ship.

# Coordinates whose 7th decimal is a 5: each sits exactly on a 6-dp rounding tie.
TIE_PART = [[-87.6918275, 41.8937965], [-87.6918295, 41.8938825], [-87.6917135, 41.8937985]]
TIE_MELLOW = {"type": "FeatureCollection", "features": [
    {"type": "Feature",
     "geometry": {"type": "MultiLineString", "coordinates": [TIE_PART]},
     "properties": {"segment_id": "mellow-street", "route_type": "street"}},
]}
NO_ROUTES = {"type": "FeatureCollection", "features": []}


def test_coordinates_are_the_input_rounded_not_a_reprojection_roundtrip():
    out = aggregate.build_mellow_connectors(TIE_MELLOW, NO_ROUTES)
    part = out["features"][0]["geometry"]["coordinates"][0]
    assert part == [[round(x, 6), round(y, 6)] for x, y in TIE_PART]


def test_building_twice_is_byte_identical():
    a = aggregate.build_mellow_connectors(TIE_MELLOW, ROUTES_GJ)
    b = aggregate.build_mellow_connectors(TIE_MELLOW, ROUTES_GJ)
    assert json.dumps(a) == json.dumps(b)
    c = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    d = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    assert json.dumps(c) == json.dumps(d)


def test_mellow_connector_records_is_part_count():
    out = aggregate.build_mellow_connectors(MELLOW_GJ, ROUTES_GJ)
    assert aggregate.mellow_connector_records(out) == 1
    empty = aggregate.build_mellow_connectors({"type": "FeatureCollection", "features": []},
                                              ROUTES_GJ)
    assert aggregate.mellow_connector_records(empty) == 0
