import json

import geopandas as gpd
import pytest
from shapely.geometry import LineString, Polygon

import aggregate
from crash_metrics import build_findings_core

OUTPUT_CRS = "EPSG:4326"


def _street(coords):
    return {"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"class": "2", "status": "N"}}


# --- ward_coverage_fields ---------------------------------------------------

def test_ward_coverage_fields_happy_path_excludes_trail_from_denominator():
    # trail must not enter the on-street denominator or numerator
    cats = {"protected": 2.0, "painted": 3.0, "trail": 10.0}
    out = aggregate.ward_coverage_fields(cats, 20.0)
    assert out["bikeway_pct_protected"] == 40.0   # 2 / (2+3)
    assert out["road_miles"] == 20.0
    assert out["bikeway_pct_of_roads"] == 25.0     # (2+3) / 20


def test_ward_coverage_fields_zero_onstreet_miles_gives_none_protected_pct():
    cats = {"trail": 5.0}   # only trail present -> on-street miles are zero
    out = aggregate.ward_coverage_fields(cats, 10.0)
    assert out["bikeway_pct_protected"] is None
    assert out["road_miles"] == 10.0


def test_ward_coverage_fields_road_miles_none_never_divides_by_zero():
    cats = {"protected": 2.0, "painted": 3.0}
    out = aggregate.ward_coverage_fields(cats, None)
    assert out["road_miles"] is None
    assert out["bikeway_pct_of_roads"] is None   # never 0
    assert out["bikeway_pct_protected"] == 40.0  # independent of road_miles


def test_ward_coverage_fields_road_miles_zero_gives_none_pct_of_roads():
    cats = {"protected": 2.0, "painted": 3.0}
    out = aggregate.ward_coverage_fields(cats, 0.0)
    assert out["bikeway_pct_of_roads"] is None   # never 0/0


# --- load_street_centerlines -------------------------------------------------

def test_load_street_centerlines_returns_none_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    assert aggregate.load_street_centerlines() is None


def test_load_street_centerlines_filters_excluded_classes_and_status(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    gj = {"features": [
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "1", "status": "N"}},  # excluded class
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "2", "status": "P"}},  # excluded status
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "9", "status": "N"}},  # excluded class
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "2", "status": "N"}},  # kept
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "3", "status": "N"}},  # kept
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "4", "status": "N"}},  # kept
    ]}
    (tmp_path / "street_centerlines.geojson").write_text(json.dumps(gj))

    out = aggregate.load_street_centerlines()
    assert out is not None
    assert len(out) == 3
    assert set(out["class"]) == {"2", "3", "4"}
    assert set(out["status"]) == {"N"}


def test_load_street_centerlines_returns_none_when_nothing_survives_filter(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    gj = {"features": [
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "1", "status": "N"}},
        {**_street([[0, 0], [0, 1]]), "properties": {"class": "2", "status": "P"}},
    ]}
    (tmp_path / "street_centerlines.geojson").write_text(json.dumps(gj))

    assert aggregate.load_street_centerlines() is None


# --- build_road_network / ward_bikeway_miles_by_category --------------------
#
# Two adjacent unit-ish squares near Chicago: ward "2" (west) and ward "10"
# (east). Sorting by int(ward) must put "2" before "10", which a plain string
# sort would get backwards.

WARD2 = Polygon([(-87.660, 41.850), (-87.650, 41.850),
                 (-87.650, 41.860), (-87.660, 41.860)])
WARD10 = Polygon([(-87.650, 41.850), (-87.640, 41.850),
                  (-87.640, 41.860), (-87.650, 41.860)])


@pytest.fixture
def wards_gdf():
    return gpd.GeoDataFrame({"ward": ["2", "10"], "geometry": [WARD2, WARD10]}, crs=OUTPUT_CRS)


@pytest.fixture
def streets_gdf():
    # one street fully inside each ward, away from the shared boundary
    street_w2 = LineString([(-87.659, 41.855), (-87.651, 41.855)])
    street_w10 = LineString([(-87.649, 41.855), (-87.641, 41.855)])
    return gpd.GeoDataFrame({"geometry": [street_w2, street_w10]}, crs=OUTPUT_CRS)


def _route(coords, facility_category):
    return {"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"facility_category": facility_category}}


@pytest.fixture
def routes_gj():
    # published bike_routes.geojson shape: features already carry facility_category.
    # protected route lives in ward "2"; trail route lives in ward "10" and must
    # never count toward on-street bikeway miles.
    return {"features": [
        _route([[-87.658, 41.857], [-87.652, 41.857]], "protected"),
        _route([[-87.648, 41.857], [-87.642, 41.857]], "trail"),
    ]}


def test_build_road_network_citywide_totals_exclude_trail(streets_gdf, wards_gdf, routes_gj):
    out = aggregate.build_road_network(streets_gdf, wards_gdf, routes_gj, "2026-07-12")
    assert out["data_tier"] == "real"
    assert out["as_of"] == "2026-07-12"
    assert out["citywide"] == {
        "road_miles": 0.8,
        "onstreet_bikeway_miles": 0.3,   # trail's mileage excluded
        "pct_with_bike_infra": 37.5,
    }


def test_build_road_network_wards_shape_and_sorted_by_int_ward(streets_gdf, wards_gdf, routes_gj):
    out = aggregate.build_road_network(streets_gdf, wards_gdf, routes_gj, "2026-07-12")
    assert out["wards"] == [
        {"ward": "2", "road_miles": 0.41},
        {"ward": "10", "road_miles": 0.41},
    ]


def test_ward_bikeway_miles_by_category_uses_published_facility_category_directly(wards_gdf, routes_gj):
    # These features carry only facility_category (no displayroute/type/etc.), so
    # the function must use it directly rather than trying to resolve a type key.
    out = aggregate.ward_bikeway_miles_by_category(routes_gj, wards_gdf)
    assert set(out["2"]) == {"protected"}
    assert out["2"]["protected"] == pytest.approx(0.309, abs=0.01)
    assert set(out["10"]) == {"trail"}
    assert out["10"]["trail"] == pytest.approx(0.309, abs=0.01)


# --- build_findings_core: street-coverage finding ----------------------------

def _crash_tuple(date):
    return {"date": date, "severity": "none", "hit_and_run": False, "dooring": False, "ward": "1"}


def test_build_findings_core_includes_street_coverage_after_protected_share():
    tuples = [_crash_tuple("2026-01-05")]
    by_cat = {"protected": 10.0, "painted": 30.0}
    road_coverage = {"road_miles": 100.0, "onstreet_bikeway_miles": 40.0,
                     "pct_with_bike_infra": 40.0}
    findings = build_findings_core(tuples, by_cat, [], {}, "2026-07-12",
                                   road_coverage=road_coverage)
    ids = [f["id"] for f in findings]
    assert "street-coverage" in ids
    assert ids.index("street-coverage") == ids.index("protected-share") + 1
    by_id = {f["id"]: f for f in findings}
    assert by_id["street-coverage"]["stat"] == "40%"
    assert by_id["street-coverage"]["data_tier"] == "real"


def test_build_findings_core_omits_street_coverage_when_road_coverage_none():
    tuples = [_crash_tuple("2026-01-05")]
    by_cat = {"protected": 10.0, "painted": 30.0}
    findings = build_findings_core(tuples, by_cat, [], {}, "2026-07-12", road_coverage=None)
    assert "street-coverage" not in [f["id"] for f in findings]
