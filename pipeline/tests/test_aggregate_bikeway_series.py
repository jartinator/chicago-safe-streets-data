import json

import aggregate


def _snap(displayrou, mi_ctrline):
    # Minimal raw-snapshot-shaped feature: citywide_miles_by_category uses mi_ctrline
    # when present, so geometry can be a placeholder for that branch.
    return {"type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[0, 0], [0, 1]]},
            "properties": {"displayrou": displayrou, "mi_ctrline": mi_ctrline}}


def test_citywide_miles_by_category_uses_centerline_and_maps_labels():
    gj = {"features": [
        _snap("PROTECTED BIKE LANE", 2.0),
        _snap("Protected Bike Lane", 1.0),   # case-insensitive map
        _snap("BUFFERED BIKE LANE", 3.0),
        _snap("MARKED SHARED LANE", 0.5),
        _snap("SOMETHING WEIRD", 4.0),        # unmatched -> "other"
    ]}
    out = aggregate.citywide_miles_by_category(gj)
    assert out["protected"] == 3.0
    assert out["buffered"] == 3.0
    assert out["sharrow"] == 0.5
    assert out["other"] == 4.0


def test_build_bikeway_mileage_series_orders_and_totals(tmp_path):
    # history_path=None isolates the snapshot half; the splice is covered below.
    (tmp_path / "bike_routes_2025-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 1.0), _snap("BIKE LANE", 2.0)]}))
    (tmp_path / "bike_routes_2026-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 4.0), _snap("BIKE LANE", 2.0)]}))

    result = aggregate.build_bikeway_mileage_series(tmp_path, None)
    series = result["series"]
    assert result["data_tier"] == "derived"
    assert [p["date"] for p in series] == ["2025-01-01", "2026-01-01"]  # sorted ascending
    assert series[0]["total"] == 3.0 and series[1]["total"] == 6.0
    assert series[0]["by_category"]["protected"] == 1.0
    assert series[1]["by_category"]["protected"] == 4.0
    # on-street categories are all present, even at zero
    assert set(aggregate.ON_STREET_CATEGORIES) <= set(series[0]["by_category"])
    assert all(p["source"] == "oyl_snapshot" for p in series)


def test_snapshot_points_report_off_street_as_unknown_not_zero(tmp_path):
    # The public Bike Routes layer has no off-street trails in it at all. Emitting 0
    # would read as "the trails disappeared" once spliced after CDOT's ~55 mi.
    (tmp_path / "bike_routes_2025-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 1.0)]}))
    point = aggregate.build_bikeway_mileage_series(tmp_path, None)["series"][0]
    assert point["off_street"] is None
    assert point["off_street_total"] is None
    assert "trail" not in point["by_category"]


def test_series_note_flags_snapshot_only_run(tmp_path):
    (tmp_path / "bike_routes_2025-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 1.0)]}))
    result = aggregate.build_bikeway_mileage_series(tmp_path, None)
    assert len(result["series"]) == 1
    assert "snapshots only" in result["note"]


def test_history_is_spliced_before_snapshots_and_tagged(tmp_path):
    history = tmp_path / "history.json"
    history.write_text(json.dumps({"annual": {"network": [
        {"year": 2010, "by_category": {"protected": 0.0, "buffered": 0.0, "painted": 116.0,
                                       "greenway": 0.0, "sharrow": 30.0, "trail": 47.2,
                                       "other": 0.0}},
        {"year": 2011, "by_category": {"protected": 2.0, "buffered": 1.0, "painted": 133.0,
                                       "greenway": 0.0, "sharrow": 39.0, "trail": 47.2,
                                       "other": 0.0}},
    ]}}))
    (tmp_path / "bike_routes_2026-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 4.0)]}))

    series = aggregate.build_bikeway_mileage_series(tmp_path, history)["series"]
    assert [p["date"] for p in series] == ["2010-12-31", "2011-12-31", "2026-01-01"]
    assert [p["source"] for p in series] == ["cdot_foia_dashboard"] * 2 + ["oyl_snapshot"]
    # On-street basis: 116 painted + 30 sharrow = 146, with the 47.2 trail miles held
    # out of the total rather than folded in.
    assert series[0]["total"] == 146.0
    assert series[0]["off_street"] == {"trail": 47.2, "other": 0.0}
    assert series[0]["off_street_total"] == 47.2


def test_committed_series_splices_cdots_history_onto_our_snapshots():
    """The real artifact: one continuous on-street line from 2010 to now.

    Guards the seam specifically — CDOT's last year and our first snapshot must stay
    close, because that agreement is the whole justification for splicing them.
    """
    from config import CDOT_BIKEWAY_HISTORY_PATH, SNAPSHOT_DIR
    if not CDOT_BIKEWAY_HISTORY_PATH.exists():
        return
    series = aggregate.build_bikeway_mileage_series(SNAPSHOT_DIR,
                                                    CDOT_BIKEWAY_HISTORY_PATH)["series"]
    foia = [p for p in series if p["source"] == "cdot_foia_dashboard"]
    snaps = [p for p in series if p["source"] == "oyl_snapshot"]
    assert foia and snaps
    assert [p["date"] for p in series] == sorted(p["date"] for p in series)
    assert foia[0]["date"].startswith("2010")
    # the seam: CDOT's final year vs our earliest snapshot, same on-street basis
    assert abs(foia[-1]["total"] - snaps[0]["total"]) < 1.0


def test_category_deltas_reports_protected_upgrade_under_flat_total():
    # A painted->protected relabel: total unchanged, but the split must expose the shift.
    deltas = aggregate._category_deltas({"protected": 1.0, "painted": 2.0},
                                        {"protected": 3.0, "painted": 0.0})
    assert deltas["protected"] == {"miles_added": 2.0, "pct_growth": 200.0}
    assert deltas["painted"]["miles_added"] == -2.0
    # a type absent from both snapshots is omitted, not reported as zero
    assert "trail" not in deltas
