import aggregate


def _curated_gj(note="hand-traced approximation"):
    return {
        "type": "FeatureCollection",
        "note": note,
        "data_tier": "crowdsourced",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "segment_id": "curated-trail-lakefront-trail",
                    "name": "Lakefront Trail",
                    "facility_category": "trail",
                    "data_tier": "crowdsourced",
                    "note": "Ardmore to 71st.",
                },
                "geometry": {"type": "LineString",
                             "coordinates": [[-87.65, 41.98], [-87.63, 41.90], [-87.60, 41.80]]},
            },
            {
                "type": "Feature",
                "properties": {
                    "segment_id": "curated-trail-bloomingdale-trail",
                    "name": "Bloomingdale Trail (The 606)",
                    "facility_category": "trail",
                    "data_tier": "crowdsourced",
                },
                "geometry": {"type": "LineString",
                             "coordinates": [[-87.72, 41.9137], [-87.67, 41.9133]]},
            },
        ],
    }


def test_build_curated_trails_computes_length_and_tags_crowdsourced():
    out = aggregate.build_curated_trails(_curated_gj())
    assert out["type"] == "FeatureCollection"
    assert out["data_tier"] == "crowdsourced"
    assert out["note"] == "hand-traced approximation"
    assert len(out["features"]) == 2
    by_name = {f["properties"]["name"]: f for f in out["features"]}
    lf = by_name["Lakefront Trail"]
    assert lf["properties"]["length_m"] > 0
    assert lf["properties"]["facility_category"] == "trail"
    assert lf["properties"]["data_tier"] == "crowdsourced"
    assert lf["properties"]["segment_id"] == "curated-trail-lakefront-trail"
    # geometry passes through unchanged
    assert lf["geometry"]["type"] == "LineString"


def test_build_curated_trails_empty_input_yields_empty_featurecollection():
    out = aggregate.build_curated_trails({"type": "FeatureCollection", "features": []})
    assert out == {"type": "FeatureCollection", "features": []}


def test_build_curated_trails_omits_note_when_source_has_none():
    gj = _curated_gj(note=None)
    del gj["note"]
    out = aggregate.build_curated_trails(gj)
    assert "note" not in out


def test_osm_trails_layer_priority_raw_wins_over_curated(tmp_path):
    raw_path = tmp_path / "osm_trails.json"
    raw_path.write_text('{"elements": [{"type": "way", "id": 1, '
                        '"tags": {"name": "Real Pull Trail"}, '
                        '"geometry": [{"lat": 41.8, "lon": -87.6}, {"lat": 41.9, "lon": -87.65}]}]}')
    curated_path = tmp_path / "curated_trails.geojson"
    import json
    curated_path.write_text(json.dumps(_curated_gj()))

    out = aggregate.build_osm_trails_layer(raw_path=raw_path, curated_path=curated_path)
    names = {f["properties"]["name"] for f in out["features"]}
    assert names == {"Real Pull Trail"}


def test_osm_trails_layer_priority_curated_wins_over_stub(tmp_path):
    raw_path = tmp_path / "osm_trails.json"  # does not exist
    curated_path = tmp_path / "curated_trails.geojson"
    import json
    curated_path.write_text(json.dumps(_curated_gj()))

    out = aggregate.build_osm_trails_layer(raw_path=raw_path, curated_path=curated_path)
    assert "status" not in out.get("properties", {})
    names = {f["properties"]["name"] for f in out["features"]}
    assert names == {"Lakefront Trail", "Bloomingdale Trail (The 606)"}
    assert out["data_tier"] == "crowdsourced"


def test_osm_trails_layer_priority_stub_when_neither_exists(tmp_path):
    raw_path = tmp_path / "osm_trails.json"
    curated_path = tmp_path / "curated_trails.geojson"
    out = aggregate.build_osm_trails_layer(raw_path=raw_path, curated_path=curated_path)
    assert out["features"] == []
    assert out["properties"]["status"] == "no_data_yet"
