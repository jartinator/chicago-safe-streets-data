import aggregate


def _way(name, coords):
    # coords: list of (lat, lon)
    return {"type": "way", "id": abs(hash(name + str(coords))) % 10_000,
            "tags": {"name": name, "highway": "cycleway"},
            "geometry": [{"lat": la, "lon": lo} for la, lo in coords]}


def test_build_osm_trails_groups_by_name_and_tags_crowdsourced():
    raw = {"elements": [
        _way("Lakefront Trail", [(41.75, -87.56), (41.85, -87.61)]),
        _way("Lakefront Trail", [(41.85, -87.61), (41.98, -87.655)]),  # second way, same trail
        _way("North Branch Trail", [(41.98, -87.70), (42.10, -87.78)]),
    ]}
    out = aggregate.build_osm_trails(raw)

    assert out["type"] == "FeatureCollection"
    # two ways sharing "Lakefront Trail" collapse into ONE feature
    names = sorted(f["properties"]["name"] for f in out["features"])
    assert names == ["Lakefront Trail", "North Branch Trail"]

    by_name = {f["properties"]["name"]: f for f in out["features"]}
    lake = by_name["Lakefront Trail"]
    assert lake["geometry"]["type"] == "MultiLineString"       # 2 ways -> multi
    assert lake["properties"]["segment_id"] == "osm-trail-lakefront-trail"
    assert lake["properties"]["facility_category"] == "trail"
    assert lake["properties"]["data_tier"] == "crowdsourced"
    assert lake["properties"]["length_m"] > 0

    nb = by_name["North Branch Trail"]
    assert nb["geometry"]["type"] == "LineString"              # 1 way -> single


def test_build_osm_trails_skips_unnamed_and_non_ways():
    raw = {"elements": [
        {"type": "node", "id": 1, "lat": 41.8, "lon": -87.6},          # not a way
        {"type": "way", "id": 2, "tags": {}, "geometry": [{"lat": 41.8, "lon": -87.6}]},  # no name
    ]}
    out = aggregate.build_osm_trails(raw)
    assert out["features"] == []
