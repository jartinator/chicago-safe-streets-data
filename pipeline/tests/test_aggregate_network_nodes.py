import aggregate


def _line_feat(line_id, coords):
    return {"type": "Feature",
            "properties": {"line_id": line_id},
            "geometry": {"type": "LineString", "coordinates": coords}}


def _main_routes_fixture():
    """Four synthetic lines (spec §7 test fixture):

    alpha: vertical  at lon -87.65, lat 41.80 -> 41.90
    beta:  horizontal at lat 41.85,  lon -87.70 -> -87.60  (crosses alpha)
    gamma: horizontal at lat 41.8505, lon -87.68 -> -87.63 (crosses alpha
           ~56 m north of the alpha x beta crossing -> must MERGE with it)
    delta: vertical  at lon -87.62, lat 41.80 -> 41.90     (crosses beta only,
           ~2.5 km east of the alpha/beta/gamma cluster -> stays a separate node)
    """
    return {
        "lines": [
            {"id": "alpha", "name": "Alpha Line"},
            {"id": "beta", "name": "Beta Line"},
            {"id": "gamma", "name": "Gamma Line"},
            {"id": "delta", "name": "Delta Line"},
        ],
        "features": [
            _line_feat("alpha", [[-87.65, 41.80], [-87.65, 41.90]]),
            _line_feat("beta", [[-87.70, 41.85], [-87.60, 41.85]]),
            _line_feat("gamma", [[-87.68, 41.8505], [-87.63, 41.8505]]),
            _line_feat("delta", [[-87.62, 41.80], [-87.62, 41.90]]),
        ],
    }


ORIENTATION_POINTS = [{"label": "Test Point", "lat": 41.90, "lng": -87.75}]


def test_build_network_nodes_count_merging_labels_and_ids():
    out = aggregate.build_network_nodes(_main_routes_fixture(), ORIENTATION_POINTS)

    assert out["data_tier"] == "derived"
    # 2 merged interchange nodes + 1 orientation node
    assert len(out["nodes"]) == 3

    interchanges = [n for n in out["nodes"] if n["kind"] == "interchange"]
    orientations = [n for n in out["nodes"] if n["kind"] == "orientation"]
    assert len(interchanges) == 2
    assert len(orientations) == 1

    # deterministic ids, sorted by lat then lng: the beta x delta node (lat
    # 41.85 exactly) sorts before the merged alpha/beta/gamma cluster (lat
    # ~41.85025)
    assert [n["id"] for n in interchanges] == ["node-001", "node-002"]
    assert orientations[0]["id"] == "orient-001"

    by_id = {n["id"]: n for n in out["nodes"]}

    node1 = by_id["node-001"]
    assert node1["lines"] == ["beta", "delta"]
    assert node1["label"] == "Beta Line × Delta Line"
    assert node1["lat"] == 41.85
    assert node1["lng"] == -87.62
    assert node1["data_tier"] == "derived"

    node2 = by_id["node-002"]
    # merged: alpha x beta and alpha x gamma collapse into one node within 150 m,
    # collecting the union of all three line_ids, ordered per the roster (lines
    # list) order, not alphabetically
    assert node2["lines"] == ["alpha", "beta", "gamma"]
    assert node2["label"] == "Alpha Line × Beta Line × Gamma Line"
    assert abs(node2["lat"] - 41.85025) < 1e-4
    assert abs(node2["lng"] - (-87.65)) < 1e-6

    orient1 = by_id["orient-001"]
    assert orient1 == {
        "id": "orient-001",
        "kind": "orientation",
        "lat": 41.90,
        "lng": -87.75,
        "label": "Test Point",
        "lines": [],
        "data_tier": "derived",
    }


def test_build_network_nodes_no_crossings_yields_only_orientation_points():
    main_routes_gj = {
        "lines": [{"id": "solo", "name": "Solo Line"}],
        "features": [_line_feat("solo", [[-87.65, 41.80], [-87.65, 41.90]])],
    }
    out = aggregate.build_network_nodes(main_routes_gj, ORIENTATION_POINTS)
    kinds = [n["kind"] for n in out["nodes"]]
    assert kinds == ["orientation"]
    assert out["nodes"][0]["id"] == "orient-001"


def test_build_network_nodes_no_orientation_points_is_fine():
    out = aggregate.build_network_nodes(_main_routes_fixture(), [])
    assert all(n["kind"] == "interchange" for n in out["nodes"])
    assert len(out["nodes"]) == 2


def test_line_bbox_padded_by_150m_merge_distance():
    segs = [((-87.65, 41.80), (-87.65, 41.90))]
    bbox = aggregate._line_bbox(segs)
    assert bbox is not None
    min_lon, min_lat, max_lon, max_lat = bbox
    # padding should be positive but small (150 m in degrees, not a huge margin)
    assert 0 < (-87.65 - min_lon) < 0.01
    assert 0 < (max_lon - (-87.65)) < 0.01
    assert min_lat < 41.80 and max_lat > 41.90


def test_line_bbox_empty_segments_is_none():
    assert aggregate._line_bbox([]) is None


def test_line_bboxes_disjoint():
    b1 = (-87.70, 41.80, -87.65, 41.90)
    b2 = (-87.60, 41.80, -87.55, 41.90)  # east of b1, no overlap
    b3 = (-87.66, 41.80, -87.61, 41.90)  # overlaps b1
    assert aggregate._line_bboxes_disjoint(b1, b2) is True
    assert aggregate._line_bboxes_disjoint(b1, b3) is False


def test_build_network_nodes_skips_far_apart_line_pair_via_bbox_prefilter():
    """A pair of lines whose bboxes don't overlap must contribute zero
    interchange nodes, even though nothing else about their geometry would
    prevent a crossing check — the line-level bbox prefilter (aggregate.py's
    O(n^2) cost fix) must never change which pairs actually get an interchange."""
    main_routes_gj = {
        "lines": [{"id": "near-a", "name": "Near A"}, {"id": "near-b", "name": "Near B"},
                  {"id": "far", "name": "Far Away"}],
        "features": [
            _line_feat("near-a", [[-87.65, 41.80], [-87.65, 41.90]]),
            _line_feat("near-b", [[-87.70, 41.85], [-87.60, 41.85]]),  # crosses near-a
            _line_feat("far", [[-85.00, 39.00], [-85.00, 39.10]]),     # far from both
        ],
    }
    out = aggregate.build_network_nodes(main_routes_gj, [])
    interchanges = [n for n in out["nodes"] if n["kind"] == "interchange"]
    assert len(interchanges) == 1
    assert interchanges[0]["lines"] == ["near-a", "near-b"]
