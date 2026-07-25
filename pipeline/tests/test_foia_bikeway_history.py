import json
import pathlib

import pytest

import foia_bikeway_history as fbh
from config import CDOT_BIKEWAY_HISTORY_PATH, FACILITY_CATEGORIES

openpyxl = pytest.importorskip("openpyxl")


def _dashboard(tmp_path, rows, years=(2010, 2011)):
    """Minimal R_Dashboard-shaped workbook: a label column then one column per year."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = fbh.DASHBOARD_SHEET
    ws.append(["CDOT Complete Streets"])          # banner rows the real sheet carries
    ws.append([])
    ws.append([fbh.YEAR_ROW_LABEL, *years])
    for label, values in rows:
        ws.append([label, *values])
    path = tmp_path / "dash.xlsx"
    wb.save(path)
    return path


def test_build_annual_series_maps_rows_to_facility_categories(tmp_path):
    path = _dashboard(tmp_path, [
        ("R_Bike_Net_PBL", [2.0, 11.4]),
        ("R_Bike_Net_BBL", [1.0, 18.65]),
        ("R_Bike_Net_BL", [116.0, 134.2]),
        ("R_Bike_Net_NG", [0.0, 1.0]),
        ("R_Bike_Net_SL", [30.0, 39.85]),
        ("R_Bike_Net_Trail", [47.2, 47.76]),
        ("R_Bike_Net_Path", [0.0, 5.8]),
    ])
    out = fbh.build_annual_series(path)

    assert out["years"] == [2010, 2011]
    first = out["network"][0]
    assert first["year"] == 2010
    assert first["by_category"]["protected"] == 2.0
    assert first["by_category"]["painted"] == 116.0   # "BIKE LANE" is painted, not protected
    assert first["by_category"]["sharrow"] == 30.0
    assert first["by_category"]["trail"] == 47.2
    assert set(first["by_category"]) == set(FACILITY_CATEGORIES)
    assert first["total"] == pytest.approx(196.2)


def test_first_occurrence_of_a_repeated_label_wins(tmp_path):
    # The real sheet repeats several R_* labels lower down to drive extra charts.
    path = _dashboard(tmp_path, [
        ("R_Bike_Net_PBL", [2.0, 11.4]),
        ("R_Bike_Net_PBL", [999.0, 999.0]),
    ])
    table, _years = fbh._read_r_dashboard(path)
    assert table["R_Bike_Net_PBL"][2010] == 2.0


def test_concrete_upgrades_are_reported_apart_from_installed_miles(tmp_path):
    # CDOT folds concrete upgrades of existing PBL into its installed totals even
    # though they add no new mileage. We surface them separately.
    path = _dashboard(tmp_path, [
        ("R_Bike_Install_PBL", [1.0, 9.49]),
        ("R_Bike_Install_PBLC", [0.0, 17.56]),
    ])
    installed = fbh.build_annual_series(path)["installed"]
    second = installed[1]
    assert second["by_category"]["protected"] == 9.49
    assert second["protected_concrete_upgrade"] == 17.56
    assert second["total"] == 9.49          # upgrades excluded from the category total


def test_missing_year_row_is_an_explicit_error(tmp_path):
    wb = openpyxl.Workbook()
    wb.active.title = fbh.DASHBOARD_SHEET
    wb.active.append(["R_Bike_Net_PBL", 1.0])
    path = tmp_path / "no_years.xlsx"
    wb.save(path)
    with pytest.raises(ValueError, match=fbh.YEAR_ROW_LABEL):
        fbh._read_r_dashboard(path)


def test_segment_facility_map_covers_the_layers_abbreviated_codes():
    # The 2023+ layer schema abbreviates ("BIKE", not "BIKE LANE"), so the public
    # layer's FACILITY_CATEGORY_MAP does not apply. Guard the divergence.
    assert fbh.SEGMENT_FACILITY_MAP["BIKE"] == "painted"
    assert fbh.SEGMENT_FACILITY_MAP["NEIGHBORHOOD"] == "greenway"
    assert set(fbh.SEGMENT_FACILITY_MAP.values()) <= set(FACILITY_CATEGORIES)


# --- the committed artifact itself -------------------------------------------------

@pytest.fixture(scope="module")
def committed():
    if not CDOT_BIKEWAY_HISTORY_PATH.exists():
        pytest.skip("data/cdot_bikeway_history.json not built")
    return json.loads(pathlib.Path(CDOT_BIKEWAY_HISTORY_PATH).read_text())


def test_committed_history_covers_2010_through_2025(committed):
    assert committed["data_tier"] == "real"
    assert committed["annual"]["years"] == [2010, 2025]
    assert len(committed["annual"]["network"]) == 16


def test_committed_category_sums_reconcile_to_cdots_own_totals(committed):
    """Our per-category sums must equal the totals CDOT published in the same sheet.

    This is the real regression guard: if a row label is remapped or dropped, the
    reconciliation breaks even though the file still looks well-formed.
    """
    reported = committed["annual"]["cdot_reported_totals"]["network_total"]
    for point in committed["annual"]["network"]:
        assert point["total"] == pytest.approx(reported[str(point["year"])], abs=0.05), point["year"]


def test_committed_segment_totals_track_the_2024_on_street_network(committed):
    # Segment-level centerline miles should land on CDOT's 2024 on-street figure.
    segments = committed["segment_install_years"]
    on_street_2024 = committed["annual"]["cdot_reported_totals"]["network_on_street"]["2024"]
    assert segments["centerline_miles"] == pytest.approx(on_street_2024, abs=2.0)
    assert segments["segments"] > 900
    years = [p["year"] for p in segments["by_install_year"]]
    assert years == sorted(years) and min(years) > 1900
