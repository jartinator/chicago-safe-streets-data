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
    (tmp_path / "bike_routes_2025-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 1.0), _snap("BIKE LANE", 2.0)]}))
    (tmp_path / "bike_routes_2026-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 4.0), _snap("BIKE LANE", 2.0)]}))

    result = aggregate.build_bikeway_mileage_series(tmp_path)
    series = result["series"]
    assert result["data_tier"] == "derived"
    assert [p["date"] for p in series] == ["2025-01-01", "2026-01-01"]  # sorted ascending
    assert series[0]["total"] == 3.0 and series[1]["total"] == 6.0
    assert series[0]["by_category"]["protected"] == 1.0
    assert series[1]["by_category"]["protected"] == 4.0
    # every declared category key is present, even at zero
    assert set(aggregate.FACILITY_CATEGORIES) <= set(series[0]["by_category"])


def test_series_note_flags_single_snapshot(tmp_path):
    (tmp_path / "bike_routes_2025-01-01.geojson").write_text(json.dumps(
        {"features": [_snap("PROTECTED BIKE LANE", 1.0)]}))
    result = aggregate.build_bikeway_mileage_series(tmp_path)
    assert len(result["series"]) == 1
    assert "Only one snapshot" in result["note"]


def test_category_deltas_reports_protected_upgrade_under_flat_total():
    # A painted->protected relabel: total unchanged, but the split must expose the shift.
    deltas = aggregate._category_deltas({"protected": 1.0, "painted": 2.0},
                                        {"protected": 3.0, "painted": 0.0})
    assert deltas["protected"] == {"miles_added": 2.0, "pct_growth": 200.0}
    assert deltas["painted"]["miles_added"] == -2.0
    # a type absent from both snapshots is omitted, not reported as zero
    assert "trail" not in deltas
