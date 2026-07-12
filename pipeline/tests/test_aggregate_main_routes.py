import aggregate

# The tests run against the REAL checked-in roster (data/main_routes.json) so
# they validate the shipped config's ordering guarantees (loop first, etc.),
# not a synthetic stand-in.
ROSTER = aggregate.load_main_routes_roster()

# Loop bbox from the roster: (south, west, north, east) around downtown.
LOOP_MID = (41.882, -87.630)      # inside the loop clip bbox
WEST_MID = (41.882, -87.720)      # well west of it (Garfield Park-ish)
NORTH_MID = (41.950, -87.700)     # far outside the loop bbox


def _seg(sid, street, cat, length_m=1609.34, mid=NORTH_MID, crashes=0):
    """Street segment with a 3-vertex line whose MIDDLE vertex is exactly `mid`
    (build_main_routes uses the middle vertex as the clip-bbox test point)."""
    lat, lon = mid
    return {"type": "Feature",
            "geometry": {"type": "LineString",
                         "coordinates": [[lon, lat - 0.002], [lon, lat], [lon, lat + 0.002]]},
            "properties": {"segment_id": sid, "street": street,
                           "facility_category": cat, "length_m": length_m,
                           "crashes_within_30m": crashes, "data_tier": "real"}}


def _trail(name, length_m=16093.4):
    return {"type": "Feature",
            "geometry": {"type": "LineString",
                         "coordinates": [[-87.60, 41.75], [-87.65, 41.95]]},
            "properties": {"segment_id": "osm-trail-" + name.lower().replace(" ", "-"),
                           "name": name, "facility_category": "trail",
                           "length_m": length_m, "data_tier": "crowdsourced"}}


def _fc(feats):
    return {"type": "FeatureCollection", "features": feats}


STUB_TRAILS = aggregate.stub_layer("no trails pulled yet")


def _lines_by_id(out):
    return {ln["id"]: ln for ln in out["lines"]}


def test_roster_shape_matches_spec():
    lines = ROSTER["lines"]
    assert len(lines) == 18
    street = [ln for ln in lines if ln["source"] == "bike_routes"]
    trail = [ln for ln in lines if ln["source"] == "osm_trails"]
    assert len(street) == 13 and len(trail) == 5
    # loop is FIRST so its bbox claims downtown segments before the couplet lines
    assert lines[0]["id"] == "loop"
    assert lines[0].get("clip_bbox"), "loop must carry its downtown clip bbox"
    ids = [ln["id"] for ln in lines]
    assert ids.index("loop") < ids.index("jackson-washington")
    assert ids.index("loop") < ids.index("state-indiana")
    assert {"lakefront", "bloomingdale", "major-taylor",
            "north-shore-channel", "north-branch"} <= set(ids)


def test_normalize_street_strips_type_suffix():
    assert aggregate.normalize_street("RANDOLPH ST") == "RANDOLPH"
    assert aggregate.normalize_street("Milwaukee Ave") == "MILWAUKEE"
    assert aggregate.normalize_street("HALSTED") == "HALSTED"
    # only a trailing suffix TOKEN is stripped — embedded words survive
    assert aggregate.normalize_street("EAST LAKE") == "EAST LAKE"
    # a street that IS a suffix word alone is left as-is
    assert aggregate.normalize_street("ST") == "ST"


def test_first_match_wins_loop_bbox_claims_downtown_washington():
    routes = _fc([
        _seg("w-downtown", "WASHINGTON", "protected", mid=LOOP_MID),
        _seg("w-westside", "WASHINGTON", "buffered", mid=WEST_MID),
    ])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    by_seg = {f["properties"]["segment_id"]: f["properties"] for f in out["features"]}
    assert by_seg["w-downtown"]["line_id"] == "loop"
    assert by_seg["w-westside"]["line_id"] == "jackson-washington"
    # a segment joins at most one line — no duplicates in the member features
    seg_ids = [f["properties"]["segment_id"] for f in out["features"]]
    assert len(seg_ids) == len(set(seg_ids)) == 2


def test_street_suffix_variant_matches_roster():
    # the raw data carries both RANDOLPH and RANDOLPH ST (spec §5)
    routes = _fc([_seg("r1", "RANDOLPH ST", "protected", mid=LOOP_MID)])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    assert out["features"][0]["properties"]["line_id"] == "loop"


def test_grade_mapping_including_greenway_and_sharrow():
    routes = _fc([
        _seg("g1", "HALSTED", "protected"),
        _seg("g2", "ELSTON", "buffered"),
        _seg("g3", "DAMEN", "greenway"),
        _seg("g4", "MILWAUKEE", "sharrow"),
        _seg("g5", "CLARK", "painted"),
        _seg("g6", "KEDZIE", "other"),
    ])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    grades = {f["properties"]["segment_id"]: f["properties"]["grade"]
              for f in out["features"]}
    assert grades == {"g1": "protected", "g2": "painted", "g3": "painted",
                      "g4": "none", "g5": "painted", "g6": "none"}


def test_pct_protected_over_member_miles_only():
    # 1 mi protected + 2 mi painted = 33.3% — gaps are holes, never fabricated,
    # so the denominator is member miles only.
    routes = _fc([
        _seg("l1", "LAKE", "protected", length_m=1609.34),
        _seg("l2", "LAKE", "painted", length_m=3218.68),
    ])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    lake = _lines_by_id(out)["lake"]
    assert lake["data_tier"] == "derived"
    assert lake["miles_total"] == 3.0
    assert lake["pct_protected"] == 33.3
    assert lake["miles_by_grade"] == {"protected": 1.0, "painted": 2.0}
    assert "no_data" not in lake


def test_trail_matching_by_name_token():
    trails = _fc([_trail("Lakefront Trail"),
                  _trail("The 606 - Bloomingdale Trail"),
                  _trail("Some Unrelated Path")])
    out = aggregate.build_main_routes(_fc([]), trails, ROSTER)
    by_line = _lines_by_id(out)
    assert "no_data" not in by_line["lakefront"]
    assert by_line["lakefront"]["data_tier"] == "crowdsourced"
    assert by_line["lakefront"]["miles_total"] == 10.0
    assert by_line["lakefront"]["miles_by_grade"] == {"offstreet": 10.0}
    assert by_line["bloomingdale"].get("no_data") is not True
    # unmatched trail names stay out of the layer entirely
    member_names = {f["properties"]["segment_id"] for f in out["features"]}
    assert "osm-trail-some-unrelated-path" not in member_names
    # trail members carry grade offstreet + crowdsourced tier, no crash counts
    lf = next(f for f in out["features"]
              if f["properties"]["line_id"] == "lakefront")
    assert lf["properties"]["grade"] == "offstreet"
    assert lf["properties"]["data_tier"] == "crowdsourced"
    assert "crashes_within_30m" not in lf["properties"]


def test_stub_trails_produce_no_data_lines_with_zero_features():
    out = aggregate.build_main_routes(_fc([]), STUB_TRAILS, ROSTER)
    assert out["features"] == []
    for ln in out["lines"]:
        if ln["source"] == "osm_trails":
            assert ln["no_data"] is True
            assert ln["miles_total"] == 0
            assert ln["data_tier"] == "crowdsourced"


def test_crashes_total_on_street_lines_only():
    routes = _fc([
        _seg("h1", "HALSTED", "protected", crashes=3),
        _seg("h2", "HALSTED", "painted", crashes=2),
    ])
    trails = _fc([_trail("Lakefront Trail")])
    out = aggregate.build_main_routes(routes, trails, ROSTER)
    by_line = _lines_by_id(out)
    assert by_line["halsted"]["crashes_total"] == 5
    assert "crashes_total" not in by_line["lakefront"]
    assert "pct_protected" not in by_line["lakefront"]
    # street member features keep their crash counts; tier passthrough is real
    h1 = next(f for f in out["features"] if f["properties"]["segment_id"] == "h1")
    assert h1["properties"]["crashes_within_30m"] == 3
    assert h1["properties"]["data_tier"] == "real"


def test_top_level_shape_is_derived_with_lines_key():
    out = aggregate.build_main_routes(_fc([]), STUB_TRAILS, ROSTER)
    assert out["type"] == "FeatureCollection"
    assert out["data_tier"] == "derived"
    assert "editorial" in out["note"]
    assert len(out["lines"]) == 18
