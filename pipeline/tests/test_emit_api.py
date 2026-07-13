import json

import pytest

import emit_api
from config import SITE_BASE_URL, CONTRACT_VERSION
from emit_api import build_citywide, build_corridors_api, build_index, emit_all


def _meta(provenance="socrata", generated_at="2026-07-01T00:00:00+00:00"):
    return {"generated_at": generated_at, "provenance": provenance,
            "contract_version": CONTRACT_VERSION, "sources": []}


def _citywide_trend():
    return {"data_tier": "real", "window_end": "2026-06-30",
            "note": "Monthly counts of police-reported cyclist crashes.",
            "months": [{"month": "2026-06", "crashes": 10, "injury_crashes": 5,
                       "ksi": 2, "fatal": 0}]}


def _findings():
    return [
        {"id": "ksi-trend", "title": "KSI", "stat": "216", "description": "desc",
         "caveat": "counts, not rates",
         "map_state": {"screen": "map", "layers": ["crashes"], "filters": {}},
         "data_tier": "real"},
        {"id": "another", "title": "Another", "stat": "1", "description": "d2",
         "caveat": "c2", "map_state": {}, "data_tier": "proxy"},
    ]


def _mileage_series(series=None):
    if series is None:
        series = [
            {"date": "2026-01-01", "by_category": {"protected": 50.0, "painted": 50.0},
             "total": 100.0},
            {"date": "2026-07-01", "by_category": {"protected": 68.74, "painted": 138.49},
             "total": 445.91},
        ]
    return {"data_tier": "derived", "note": "Bikeway mileage by facility category.",
            "series": series}


def _corridors():
    return [{"street": "KINZIE", "segments": 3, "length_m": 1355.6, "crashes": 105,
             "crashes_per_km": 77.46, "facility_mix": {"protected": 859.1},
             "data_tier": "real"}]


def _intersections():
    return [{"lat": 41.9, "lng": -87.6, "label": "near X", "crashes": 24,
             "data_tier": "real"}]


def _write_site_data(dir_):
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / "meta.json").write_text(json.dumps(_meta()))
    (dir_ / "citywide_trend.json").write_text(json.dumps(_citywide_trend()))
    (dir_ / "findings.json").write_text(json.dumps(_findings()))
    (dir_ / "bikeway_mileage_series.json").write_text(json.dumps(_mileage_series()))
    (dir_ / "corridors.json").write_text(json.dumps(_corridors()))
    (dir_ / "intersections.json").write_text(json.dumps(_intersections()))


# --- 1. envelope propagation -------------------------------------------------

def test_envelope_copies_generated_at_and_provenance_verbatim():
    meta = _meta(provenance="fixtures", generated_at="2020-01-01T00:00:00+00:00")
    out = build_citywide(meta, _citywide_trend(), _findings(), _mileage_series())
    assert out["_meta"]["generated_at"] == "2020-01-01T00:00:00+00:00"
    assert out["_meta"]["provenance"] == "fixtures"
    assert out["_meta"]["api_version"] == emit_api.API_VERSION
    assert out["_meta"]["contract_version"] == CONTRACT_VERSION


def test_envelope_is_first_key_in_every_builder_output():
    citywide = build_citywide(_meta(), _citywide_trend(), _findings(), _mileage_series())
    corridors = build_corridors_api(_meta(), _corridors(), _intersections())
    index = build_index(_meta(), {"citywide.json": 1, "corridors.json": 1})
    assert list(citywide.keys())[0] == "_meta"
    assert list(corridors.keys())[0] == "_meta"
    assert list(index.keys())[0] == "_meta"


def test_envelope_carries_license_and_attribution():
    out = build_corridors_api(_meta(), _corridors(), _intersections())
    assert "City of Chicago Data Portal" in out["_meta"]["license"]
    assert "On Your Left!" in out["_meta"]["attribution"]


# --- 2. build_citywide --------------------------------------------------------

def test_build_citywide_sections_present_and_map_state_stripped():
    out = build_citywide(_meta(), _citywide_trend(), _findings(), _mileage_series())
    assert out["trend"]["months"] == _citywide_trend()["months"]
    assert out["trend"]["data_tier"] == "real"
    assert len(out["findings"]) == 2
    for f in out["findings"]:
        assert "map_state" not in f
    assert out["findings"][0]["caveat"] == "counts, not rates"
    assert out["findings"][0]["data_tier"] == "real"
    assert out["bikeway_mileage"]["data_tier"] == "derived"
    assert out["bikeway_mileage"]["series"] == _mileage_series()["series"]


def test_build_citywide_protected_share_math():
    out = build_citywide(_meta(), _citywide_trend(), _findings(), _mileage_series())
    ps = out["protected_share"]
    assert ps["as_of"] == "2026-07-01"
    assert ps["protected_miles"] == 68.74
    assert ps["total_miles"] == 445.91
    assert ps["pct_protected"] == round(100 * 68.74 / 445.91, 1)
    assert ps["data_tier"] == "derived"


def test_build_citywide_empty_series_omits_protected_share():
    out = build_citywide(_meta(), _citywide_trend(), _findings(),
                         _mileage_series(series=[]))
    assert "protected_share" not in out
    assert out["bikeway_mileage"]["series"] == []


def test_build_citywide_envelope_is_mixed_with_tier_note():
    out = build_citywide(_meta(), _citywide_trend(), _findings(), _mileage_series())
    assert out["_meta"]["data_tier"] == "mixed"
    assert out["_meta"].get("tier_note")
    assert out["_meta"]["human_page"] == SITE_BASE_URL + "/findings.html"


# --- 3. build_corridors_api ---------------------------------------------------

def test_build_corridors_api_pass_through_fidelity():
    corridors, intersections = _corridors(), _intersections()
    out = build_corridors_api(_meta(), corridors, intersections)
    assert out["corridors"] == corridors
    assert out["hotspot_intersections"] == intersections


def test_build_corridors_api_envelope_is_real_no_tier_note():
    out = build_corridors_api(_meta(), _corridors(), _intersections())
    assert out["_meta"]["data_tier"] == "real"
    assert "tier_note" not in out["_meta"]
    assert out["_meta"]["human_page"] == SITE_BASE_URL + "/index.html"


# --- 4. build_index ------------------------------------------------------------

def test_build_index_lists_exactly_phase1_endpoints():
    out = build_index(_meta(), {"citywide.json": 1234, "corridors.json": 5678})
    paths = [e["path"] for e in out["endpoints"]]
    assert paths == ["citywide.json", "corridors.json"]


def test_build_index_endpoint_urls_are_absolute_under_api_v1():
    out = build_index(_meta(), {"citywide.json": 1234, "corridors.json": 5678})
    for e in out["endpoints"]:
        assert e["url"] == SITE_BASE_URL + "/api/v1/" + e["path"]


def test_build_index_bytes_approx_taken_from_input():
    out = build_index(_meta(), {"citywide.json": 1234, "corridors.json": 5678})
    by_path = {e["path"]: e for e in out["endpoints"]}
    assert by_path["citywide.json"]["bytes_approx"] == 1234
    assert by_path["corridors.json"]["bytes_approx"] == 5678


def test_build_index_endpoints_have_example_questions():
    out = build_index(_meta(), {"citywide.json": 1, "corridors.json": 1})
    for e in out["endpoints"]:
        assert 2 <= len(e["example_questions"]) <= 3
        assert all(isinstance(q, str) and q for q in e["example_questions"])


def test_build_index_no_synthetic_data_statement_present():
    out = build_index(_meta(), {"citywide.json": 1, "corridors.json": 1})
    assert "obstruction" in out["no_synthetic_data"].lower()
    assert "synthetic" in out["no_synthetic_data"].lower()


def test_build_index_fetch_recipes_reference_only_phase1_urls():
    out = build_index(_meta(), {"citywide.json": 1, "corridors.json": 1})
    allowed = {SITE_BASE_URL + "/api/v1/citywide.json",
              SITE_BASE_URL + "/api/v1/corridors.json"}
    assert 2 <= len(out["fetch_recipes"]) <= 3
    for recipe in out["fetch_recipes"]:
        assert recipe["question"] and recipe["then"]
        for url in recipe["fetch"]:
            assert url in allowed


def test_build_index_coverage_note_mentions_crash_start_date():
    from config import CRASH_START_DATE
    out = build_index(_meta(), {"citywide.json": 1, "corridors.json": 1})
    assert CRASH_START_DATE in out["coverage_note"]


def test_build_index_planned_namespaces_are_marked_not_yet_published():
    out = build_index(_meta(), {"citywide.json": 1, "corridors.json": 1})
    assert out["planned"]
    for entry in out["planned"]:
        assert "not yet published" in entry.lower()


# --- 5. no obstruction leakage -------------------------------------------------

def test_emit_all_mentions_obstruction_only_in_index_no_synthetic_statement(
        tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_all()

    index = json.loads((api_dir / "index.json").read_text())
    no_synth = index.pop("no_synthetic_data")
    assert "obstruction" in no_synth.lower()

    assert "obstruction" not in json.dumps(index).lower()
    for name in ["citywide.json", "corridors.json"]:
        assert "obstruction" not in (api_dir / name).read_text().lower()


# --- 6. emit_all IO orchestration ----------------------------------------------

def test_emit_all_writes_three_files(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    assert set(written) == {"citywide.json", "corridors.json", "index.json"}
    for name in written:
        assert (api_dir / name).exists()


def test_emit_all_budget_violation_raises_system_exit(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "API_SIZE_BUDGET_BYTES", 10)

    with pytest.raises(SystemExit):
        emit_all()


def test_emit_all_prunes_stale_files_but_preserves_schemas(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    stale = api_dir / "wards" / "ward-99.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("{}")
    schema = api_dir / "schemas" / "whatever.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_text("{}")

    emit_all()

    assert not stale.exists()
    assert not stale.parent.exists()  # emptied wards/ dir pruned too
    assert schema.exists()


# --- 7. bytes_approx matches actual on-disk sizes ------------------------------

def test_index_bytes_approx_matches_actual_on_disk_sizes(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_all()

    index = json.loads((api_dir / "index.json").read_text())
    for e in index["endpoints"]:
        actual = (api_dir / e["path"]).stat().st_size
        assert e["bytes_approx"] == actual
