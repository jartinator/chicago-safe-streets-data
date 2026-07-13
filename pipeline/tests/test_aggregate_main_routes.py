import aggregate

# The tests run against the REAL checked-in roster (data/main_routes.json) so
# they validate the shipped config, not a synthetic stand-in.
ROSTER = aggregate.load_main_routes_roster()

NORTH_MID = (41.950, -87.700)


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
    # network-tiers-v2 design spec §2 (2026-07-13-network-tiers-design.md):
    # owner-signed count 14 street lines + 5 trail lines = 19; roosevelt and
    # vincennes demoted to connectors.
    lines = ROSTER["lines"]
    assert len(lines) == 19
    street = [ln for ln in lines if ln["source"] == "bike_routes"]
    trail = [ln for ln in lines if ln["source"] == "osm_trails"]
    assert len(street) == 14 and len(trail) == 5
    ids = [ln["id"] for ln in lines]
    assert not ({"loop", "belmont", "31st"} & set(ids)), "dropped lines must be gone"
    assert not ({"roosevelt", "vincennes"} & set(ids)), "demoted-to-connector lines must be gone"
    assert {"california", "mlk-drive", "lawrence", "marquette", "83rd"} <= set(ids)
    assert {"milwaukee", "halsted", "clark", "kedzie", "damen", "state-indiana",
            "elston", "lake", "jackson-washington"} <= set(ids)
    assert {"lakefront", "bloomingdale", "major-taylor",
            "north-shore-channel", "north-branch"} <= set(ids)
    # no line carries a clip_bbox anymore (that was loop-only)
    assert not any(ln.get("clip_bbox") for ln in lines)


def test_normalize_street_strips_type_suffix():
    assert aggregate.normalize_street("RANDOLPH ST") == "RANDOLPH"
    assert aggregate.normalize_street("Milwaukee Ave") == "MILWAUKEE"
    assert aggregate.normalize_street("HALSTED") == "HALSTED"
    # only a trailing suffix TOKEN is stripped — embedded words survive
    assert aggregate.normalize_street("EAST LAKE") == "EAST LAKE"
    # a street that IS a suffix word alone is left as-is
    assert aggregate.normalize_street("ST") == "ST"


def test_multi_membership_when_two_lines_share_a_street():
    # network-tiers-v2 design spec §6 (shared tracks / interlining): a segment
    # explicitly listed by MORE THAN ONE line's `streets` belongs to all of
    # them — no two real roster lines currently share a street name, so this
    # is a synthetic 2-line roster where both list HALSTED.
    mini_roster = {"lines": [
        {"id": "first", "name": "First", "termini": "a", "source": "bike_routes",
         "streets": ["HALSTED"]},
        {"id": "second", "name": "Second", "termini": "b", "source": "bike_routes",
         "streets": ["HALSTED"]},
    ]}
    routes = _fc([_seg("h1", "HALSTED", "protected", length_m=1609.34, crashes=2)])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, mini_roster)

    # exactly ONE feature is emitted for the shared segment — not one per line
    assert len(out["features"]) == 1
    props = out["features"][0]["properties"]
    assert props["segment_id"] == "h1"
    # line_id (back-compat) is the first roster-order match; line_ids carries both
    assert props["line_id"] == "first"
    assert props["line_ids"] == ["first", "second"]

    # both lines' mileage/crash totals include the shared segment
    by_id = _lines_by_id(out)
    assert by_id["first"]["miles_total"] == 1.0
    assert by_id["second"]["miles_total"] == 1.0
    assert by_id["first"]["miles_by_grade"] == {"protected": 1.0}
    assert by_id["second"]["miles_by_grade"] == {"protected": 1.0}
    assert by_id["first"]["crashes_total"] == 2
    assert by_id["second"]["crashes_total"] == 2


def test_single_membership_line_ids_is_length_one():
    # On real (non-overlapping) roster data, line_ids always has length 1.
    routes = _fc([_seg("m1", "MILWAUKEE", "protected")])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    props = out["features"][0]["properties"]
    assert props["line_ids"] == ["milwaukee"]
    assert props["line_id"] == "milwaukee"


def test_clip_bbox_filters_by_segment_midpoint():
    # clip_bbox is unused by the current roster (only "loop" carried one, and
    # it was dropped — spec §3) but build_main_routes must still honor it.
    downtown_mid = (41.882, -87.630)   # inside the bbox
    west_mid = (41.882, -87.720)       # well outside it
    mini_roster = {"lines": [
        {"id": "downtown", "name": "Downtown", "termini": "a", "source": "bike_routes",
         "streets": ["WASHINGTON"], "clip_bbox": [41.868, -87.647, 41.9, -87.615]},
        {"id": "westside", "name": "Westside", "termini": "b", "source": "bike_routes",
         "streets": ["WASHINGTON"]},
    ]}
    routes = _fc([
        _seg("w-downtown", "WASHINGTON", "protected", mid=downtown_mid),
        _seg("w-westside", "WASHINGTON", "buffered", mid=west_mid),
    ])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, mini_roster)
    by_seg = {f["properties"]["segment_id"]: f["properties"] for f in out["features"]}
    assert by_seg["w-downtown"]["line_id"] == "downtown"
    assert by_seg["w-westside"]["line_id"] == "westside"
    # a segment joins at most one line — no duplicates in the member features
    seg_ids = [f["properties"]["segment_id"] for f in out["features"]]
    assert len(seg_ids) == len(set(seg_ids)) == 2


def test_per_street_clip_bbox_claims_only_part_of_a_street():
    # streets entries may be {"name", "clip_bbox"}: a per-street bbox clips
    # that street alone, leaving the line's other streets unclipped.
    mini_roster = {"lines": [
        {"id": "diag", "name": "Diag", "termini": "a", "source": "bike_routes",
         "streets": ["MILWAUKEE",
                     {"name": "RANDOLPH", "clip_bbox": [41.88, -87.65, 41.89, -87.61]}]},
    ]}
    routes = _fc([
        _seg("m-far", "MILWAUKEE", "protected", mid=(41.95, -87.70)),   # unclipped street: kept anywhere
        _seg("r-loop", "RANDOLPH", "protected", mid=(41.884, -87.63)),  # inside the street bbox: kept
        _seg("r-west", "RANDOLPH", "painted", mid=(41.884, -87.72)),    # outside it: dropped
    ])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, mini_roster)
    seg_ids = {f["properties"]["segment_id"] for f in out["features"]}
    assert seg_ids == {"m-far", "r-loop"}


def test_downtown_trunk_is_shared_by_four_lines():
    # The shipped roster interlines the Loop stretch of RANDOLPH across
    # milwaukee/clark/lake/jackson-washington (in roster order) so those
    # four connect downtown and lead to the Lakefront Trail.
    routes = _fc([_seg("r-trunk", "RANDOLPH", "protected", mid=(41.8845, -87.622))])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    props = out["features"][0]["properties"]
    assert props["line_ids"] == ["milwaukee", "clark", "lake", "jackson-washington"]
    assert props["line_id"] == "milwaukee"


def test_street_property_emitted_on_members():
    # The UI chains gap fills per source street (couplet lines like
    # Jackson–Washington must not zigzag between their two streets).
    routes = _fc([_seg("m1", "MILWAUKEE AVE", "protected")])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    assert out["features"][0]["properties"]["street"] == "MILWAUKEE"


def test_street_suffix_variant_matches_roster():
    # the raw data carries both MILWAUKEE and MILWAUKEE AVE (spec §5)
    routes = _fc([_seg("m1", "MILWAUKEE AVE", "protected")])
    out = aggregate.build_main_routes(routes, STUB_TRAILS, ROSTER)
    assert out["features"][0]["properties"]["line_id"] == "milwaukee"


def test_grade_mapping_including_greenway_and_sharrow():
    # network-tiers-v2 design spec §3: protected<-protected; paint<-buffered,
    # painted; mellow<-greenway (its own grade, no longer lumped into paint);
    # none<-sharrow, other/unmatched.
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
    assert grades == {"g1": "protected", "g2": "paint", "g3": "mellow",
                      "g4": "none", "g5": "paint", "g6": "none"}


def test_pct_protected_over_member_miles_only():
    # 1 mi protected + 2 mi paint = 33.3% — gaps are holes, never fabricated,
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
    assert lake["miles_by_grade"] == {"protected": 1.0, "paint": 2.0}
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


def test_trail_exclude_tokens_veto_a_name_match():
    # OSM's "Evanston Lakefront Trail" is a distinct suburban trail whose
    # name embeds "lakefront" — the roster's exclude_tokens must keep it
    # out of Chicago's Lakefront Trail line (which ends at Ardmore).
    trails = _fc([_trail("Lakefront Trail"),
                  _trail("Evanston Lakefront Trail")])
    out = aggregate.build_main_routes(_fc([]), trails, ROSTER)
    member_names = {f["properties"]["segment_id"] for f in out["features"]}
    assert "osm-trail-lakefront-trail" in member_names
    assert "osm-trail-evanston-lakefront-trail" not in member_names
    # the excluded trail's mileage stays out of the line stats too
    assert _lines_by_id(out)["lakefront"]["miles_total"] == 10.0


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
    assert len(out["lines"]) == 19
