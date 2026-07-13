import json

import pytest

import emit_api
from config import SITE_BASE_URL, CONTRACT_VERSION
from emit_api import (COMPARABLE_DANGER_SCORE_DESC, build_citywide, build_corridors_api,
                      build_index, build_ward_file, build_wards_index, emit_all)


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


def _ward_record(ward="1", **overrides):
    rec = {
        "ward": ward, "cyclist_crashes": 120, "population": 55000.0,
        "bikeway_miles": 4.2, "crashes_per_10k_pop": 21.8,
        "crashes_per_bikeway_mile": 28.6, "comparable_danger_score": 62.0,
        "crash_trend": {"direction": "worsening", "window_end": "2026-06-30",
                       "recent_12mo": 40, "prior_12mo": 35, "pct_change": 14.3},
        "infra_growth_trend": {"miles_added": 0.1, "pct_growth": 2.4,
                              "since": "2026-01-01", "by_category": {}},
        "windows": {"recent_12mo": {"crashes": 40, "injury_crashes": 15, "ksi": 2, "fatal": 0},
                   "prior_12mo": {"crashes": 35, "injury_crashes": 12, "ksi": 1, "fatal": 0},
                   "window_end": "2026-06-30"},
        "monthly": [{"month": "2026-06", "crashes": 4, "injury_crashes": 1, "ksi": 0, "fatal": 0}],
        "data_tier": "derived", "bikeway_pct_protected": 40.0,
        "road_miles": 12.0, "bikeway_pct_of_roads": 35.0,
    }
    rec.update(overrides)
    return rec


def _ward_safety_index(wards=None):
    if wards is None:
        wards = [_ward_record("1"), _ward_record("2", comparable_danger_score=20.0)]
    return {"data_tier": "derived",
           "note": ("comparable_danger_score is a 0-100 blend of each ward's "
                   "percentile rank on crashes-per-10k-population and "
                   "crashes-per-bikeway-mile."),
           "wards": wards}


def _aldermen(wards=None):
    if wards is None:
        wards = [{"ward": "1", "alderman": "Alder One", "email": "w1@cityofchicago.org",
                 "phone": "(111) 111-1111", "website": "https://w1.example"}]
        # ward "2" intentionally absent — tests the honest-null branch
    return {"as_of": "2026-07-13T05:00:00+00:00", "source": "Chicago Data Portal — Ward Offices",
           "data_tier": "real", "note": "Current alderperson roster.",
           "lookup_url": "https://www.chicago.gov/city/en/about/wards.html",
           "wards": wards}


def _aldermen_safety_record(aldermen=None):
    if aldermen is None:
        aldermen = [
            {"sponsor_name": "Alder One", "ward": "1", "safety_sponsorships": 5,
             "total_matched_sponsorships": 5, "recorded_no_votes": 0, "records": [],
             "data_tier": "derived"},
            {"sponsor_name": "Alder One (former)", "ward": "1", "safety_sponsorships": 2,
             "total_matched_sponsorships": 2, "recorded_no_votes": 1, "records": [],
             "data_tier": "derived"},
            # ward "2" intentionally has zero matching entries
        ]
    return {"data_tier": "derived",
           "note": "Aggregate of Chicago City Council sponsorships on safety-relevant matters.",
           "aldermen": aldermen}


def _menu_spending(wards=None):
    return {"data_tier": "proxy",
           "note": "Ward Wise (wardwisechicago.org) was unreachable this run.",
           "wards": wards or {}}


def _ward_311(wards=None):
    if wards is None:
        wards = [{"ward": "1", "total": 500, "by_type": {"Bicycle Request/Complaint": 500}}]
        # ward "2" intentionally absent — tests the honest-absence branch
    return {"data_tier": "proxy",
           "note": "311 requests are self-reported and biased toward engaged 311 users.",
           "wards": wards}


def _write_site_data(dir_, n_wards=50):
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / "meta.json").write_text(json.dumps(_meta()))
    (dir_ / "citywide_trend.json").write_text(json.dumps(_citywide_trend()))
    (dir_ / "findings.json").write_text(json.dumps(_findings()))
    (dir_ / "bikeway_mileage_series.json").write_text(json.dumps(_mileage_series()))
    (dir_ / "corridors.json").write_text(json.dumps(_corridors()))
    (dir_ / "intersections.json").write_text(json.dumps(_intersections()))

    ward_records = [_ward_record(str(n)) for n in range(1, n_wards + 1)]
    (dir_ / "ward_safety_index.json").write_text(
        json.dumps(_ward_safety_index(wards=ward_records)))
    alderman_wards = [{"ward": str(n), "alderman": f"Alder {n}",
                       "email": f"Ward{n:02d}@cityofchicago.org", "phone": "(111) 111-1111",
                       "website": f"https://w{n}.example"} for n in range(1, n_wards + 1)]
    (dir_ / "aldermen.json").write_text(json.dumps(_aldermen(wards=alderman_wards)))
    (dir_ / "aldermen_safety_record.json").write_text(
        json.dumps(_aldermen_safety_record(aldermen=[
            {"sponsor_name": f"Alder {n}", "ward": str(n), "safety_sponsorships": 1,
             "total_matched_sponsorships": 1, "recorded_no_votes": 0, "records": [],
             "data_tier": "derived"} for n in range(1, n_wards + 1)])))
    (dir_ / "menu_spending.json").write_text(json.dumps(_menu_spending()))
    sr311_wards = [{"ward": str(n), "total": n * 10,
                    "by_type": {"Bicycle Request/Complaint": n * 10}}
                   for n in range(1, n_wards + 1)]
    (dir_ / "ward_311.json").write_text(json.dumps(_ward_311(wards=sr311_wards)))


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
    index = build_index(_meta(), _endpoint_bytes())
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


def test_build_citywide_zero_total_omits_protected_share():
    # total == 0 must be treated like the empty-series case (omit), never a
    # ZeroDivisionError or a null-laden block.
    zero_total = [{"date": "2026-07-01", "by_category": {"protected": 0.0},
                  "total": 0.0}]
    out = build_citywide(_meta(), _citywide_trend(), _findings(),
                         _mileage_series(series=zero_total))
    assert "protected_share" not in out


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

def _endpoint_bytes(**overrides):
    bytes_ = {"citywide.json": 1234, "corridors.json": 5678, "wards/index.json": 999}
    bytes_.update(overrides)
    return bytes_


def test_build_index_lists_exactly_the_known_endpoints():
    out = build_index(_meta(), _endpoint_bytes())
    paths = [e["path"] for e in out["endpoints"]]
    assert paths == ["citywide.json", "corridors.json", "wards/index.json"]


def test_build_index_endpoint_urls_are_absolute_under_api_v1():
    out = build_index(_meta(), _endpoint_bytes())
    for e in out["endpoints"]:
        assert e["url"] == SITE_BASE_URL + "/api/v1/" + e["path"]


def test_build_index_bytes_approx_taken_from_input():
    out = build_index(_meta(), _endpoint_bytes())
    by_path = {e["path"]: e for e in out["endpoints"]}
    assert by_path["citywide.json"]["bytes_approx"] == 1234
    assert by_path["corridors.json"]["bytes_approx"] == 5678
    assert by_path["wards/index.json"]["bytes_approx"] == 999


def test_build_index_endpoints_have_example_questions():
    out = build_index(_meta(), _endpoint_bytes())
    for e in out["endpoints"]:
        assert 2 <= len(e["example_questions"]) <= 3
        assert all(isinstance(q, str) and q for q in e["example_questions"])


def test_build_index_no_synthetic_data_statement_present():
    out = build_index(_meta(), _endpoint_bytes())
    assert "obstruction" in out["no_synthetic_data"].lower()
    assert "synthetic" in out["no_synthetic_data"].lower()


def test_build_index_fetch_recipes_reference_known_urls():
    out = build_index(_meta(), _endpoint_bytes())
    allowed = {SITE_BASE_URL + "/api/v1/citywide.json",
              SITE_BASE_URL + "/api/v1/corridors.json",
              SITE_BASE_URL + "/api/v1/wards/ward-40.json"}
    assert 3 <= len(out["fetch_recipes"]) <= 4
    for recipe in out["fetch_recipes"]:
        assert recipe["question"] and recipe["then"]
        for url in recipe["fetch"]:
            assert url in allowed


def test_build_index_ward_fetch_recipe_uses_exact_danger_score_string():
    out = build_index(_meta(), _endpoint_bytes())
    ward_recipes = [r for r in out["fetch_recipes"]
                   if SITE_BASE_URL + "/api/v1/wards/ward-40.json" in r["fetch"]]
    assert len(ward_recipes) == 1
    assert COMPARABLE_DANGER_SCORE_DESC in ward_recipes[0]["then"]
    assert "alderman" in ward_recipes[0]["then"].lower()


def test_build_index_coverage_note_mentions_crash_start_date():
    from config import CRASH_START_DATE
    out = build_index(_meta(), _endpoint_bytes())
    assert CRASH_START_DATE in out["coverage_note"]


def test_build_index_planned_namespaces_are_marked_not_yet_published():
    out = build_index(_meta(), _endpoint_bytes())
    assert out["planned"]
    for entry in out["planned"]:
        assert "not yet published" in entry.lower()


def test_build_index_planned_no_longer_lists_wards():
    out = build_index(_meta(), _endpoint_bytes())
    assert not any("wards/" in entry for entry in out["planned"])
    # still-unpublished namespaces stay
    assert any("crashes/" in entry for entry in out["planned"])
    assert any("routes/" in entry for entry in out["planned"])
    assert any("council/" in entry for entry in out["planned"])
    assert any("schemas/" in entry for entry in out["planned"])


def test_build_index_omits_ward_family_when_no_ward_files_given():
    out = build_index(_meta(), _endpoint_bytes())
    assert out["families"] == []


def test_build_index_ward_family_present_with_count_and_real_max_bytes():
    ward_files_bytes = {f"wards/ward-{n:02d}.json": 1000 + n for n in range(1, 51)}
    out = build_index(_meta(), _endpoint_bytes(), ward_files_bytes)
    families = {f["path_template"]: f for f in out["families"]}
    fam = families["wards/ward-{NN}.json"]
    assert fam["count"] == 50
    assert fam["bytes_approx_max"] == max(ward_files_bytes.values())
    assert fam["example"] == SITE_BASE_URL + "/api/v1/wards/ward-01.json"


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
    assert "obstruction" not in (api_dir / "wards" / "index.json").read_text().lower()
    assert "obstruction" not in (api_dir / "wards" / "ward-01.json").read_text().lower()


# --- 6. emit_all IO orchestration ----------------------------------------------

def test_emit_all_writes_all_files(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    # phase-1 (2) + wards/index.json (1) + 50 ward files + index.json (1) = 54
    assert len(written) == 54
    expected = {"citywide.json", "corridors.json", "index.json", "wards/index.json"}
    expected |= {f"wards/ward-{n:02d}.json" for n in range(1, 51)}
    assert set(written) == expected
    for name in written:
        assert (api_dir / name).exists()


def test_emit_all_ward_files_within_budget(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    for path, size in written.items():
        assert size <= emit_api.API_SIZE_BUDGET_BYTES, f"{path} over budget: {size}"


def test_emit_all_budget_violation_raises_system_exit(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "API_SIZE_BUDGET_BYTES", 10)

    with pytest.raises(SystemExit) as excinfo:
        emit_all()
    # The exit message must name the offending file, its actual byte size,
    # and the budget it blew through.
    message = str(excinfo.value)
    assert "citywide.json" in message
    actual_size = (api_dir / "citywide.json").stat().st_size
    assert f"{actual_size:,}" in message
    assert "10" in message


def test_emit_all_prunes_stale_files_but_preserves_schemas(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    # routes/ is still `planned` (not yet emitted by any builder), so it's a
    # clean stand-in for "a retired/renamed endpoint under a subdirectory"
    # now that wards/ is real, populated output.
    stale = api_dir / "routes" / "line-99.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("{}")
    stale_ward = api_dir / "wards" / "ward-99.json"
    stale_ward.parent.mkdir(parents=True, exist_ok=True)
    stale_ward.write_text("{}")
    schema = api_dir / "schemas" / "whatever.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_text("{}")

    emit_all()

    assert not stale.exists()
    assert not stale.parent.exists()  # emptied routes/ dir pruned too
    assert not stale_ward.exists()  # stale ward-99.json pruned; wards/ itself stays (real files)
    assert (api_dir / "wards").exists()
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

    ward_family = next(f for f in index["families"]
                       if f["path_template"] == "wards/ward-{NN}.json")
    actual_sizes = [(api_dir / "wards" / f"ward-{n:02d}.json").stat().st_size
                    for n in range(1, 51)]
    assert ward_family["bytes_approx_max"] == max(actual_sizes)
    assert ward_family["count"] == 50


# --- 8. build_wards_index -------------------------------------------------------

def test_build_wards_index_has_all_wards_no_monthly_verbatim_otherwise():
    wsi = _ward_safety_index()
    out = build_wards_index(_meta(), wsi)
    assert len(out["wards"]) == 2
    for entry, source in zip(out["wards"], wsi["wards"]):
        assert "monthly" not in entry
        for key, value in source.items():
            if key == "monthly":
                continue
            assert entry[key] == value


def test_build_wards_index_detail_and_crashes_urls_are_padded():
    out = build_wards_index(_meta(), _ward_safety_index())
    by_ward = {e["ward"]: e for e in out["wards"]}
    assert by_ward["1"]["detail_url"] == SITE_BASE_URL + "/api/v1/wards/ward-01.json"
    assert by_ward["1"]["crashes_url"] == SITE_BASE_URL + "/api/v1/crashes/ward-01.json"


def test_build_wards_index_preserves_source_order():
    wsi = _ward_safety_index(wards=[_ward_record("42"), _ward_record("3"), _ward_record("17")])
    out = build_wards_index(_meta(), wsi)
    assert [e["ward"] for e in out["wards"]] == ["42", "3", "17"]


def test_build_wards_index_note_contains_exact_danger_score_string():
    out = build_wards_index(_meta(), _ward_safety_index())
    assert COMPARABLE_DANGER_SCORE_DESC in out["note"]


def test_build_wards_index_envelope_and_data_tier():
    out = build_wards_index(_meta(), _ward_safety_index())
    assert out["_meta"]["data_tier"] == "derived"
    assert out["data_tier"] == "derived"
    assert out["_meta"]["human_page"] == SITE_BASE_URL + "/table.html"


# --- 9. build_ward_file ----------------------------------------------------------

def test_build_ward_file_full_safety_record_includes_monthly():
    ward_rec = _ward_record("1")
    out = build_ward_file(_meta(), ward_rec, _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["safety"]["monthly"] == ward_rec["monthly"]
    assert out["safety"]["comparable_danger_score"] == ward_rec["comparable_danger_score"]
    assert COMPARABLE_DANGER_SCORE_DESC in out["safety"]["score_note"]


def test_build_ward_file_ward_and_ward_padded():
    out = build_ward_file(_meta(), _ward_record("7"), _aldermen(wards=[]),
                          _aldermen_safety_record(aldermen=[]), _menu_spending(), _ward_311(wards=[]))
    assert out["ward"] == "7"
    assert out["ward_padded"] == "07"


def test_build_ward_file_alderman_merge_matching_ward():
    aldermen = _aldermen()
    out = build_ward_file(_meta(), _ward_record("1"), aldermen, _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["alderman"]["alderman"] == "Alder One"
    assert out["alderman"]["as_of"] == aldermen["as_of"]
    assert out["alderman"]["source"] == aldermen["source"]
    assert out["alderman"]["data_tier"] == aldermen["data_tier"]
    assert out["alderman"]["lookup_url"] == aldermen["lookup_url"]


def test_build_ward_file_alderman_null_when_no_entry_plus_honest_note():
    out = build_ward_file(_meta(), _ward_record("2"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["alderman"] is None
    assert "alderman_note" in out
    assert "2" in out["alderman_note"]


def test_build_ward_file_safety_record_two_entries_for_ward_with_two():
    out = build_ward_file(_meta(), _ward_record("1"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert len(out["safety_record"]["entries"]) == 2
    assert {e["sponsor_name"] for e in out["safety_record"]["entries"]} == \
        {"Alder One", "Alder One (former)"}
    assert out["safety_record"]["data_tier"] == "derived"


def test_build_ward_file_safety_record_empty_list_for_ward_with_none():
    out = build_ward_file(_meta(), _ward_record("2"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["safety_record"]["entries"] == []


def test_build_ward_file_menu_spending_absent_ward_is_honest_not_fabricated():
    out = build_ward_file(_meta(), _ward_record("1"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["menu_spending"]["available"] is False
    assert out["menu_spending"]["data_tier"] == "proxy"
    assert "note" in out["menu_spending"]
    assert "total_spent" not in out["menu_spending"]


def test_build_ward_file_menu_spending_present_ward_passes_through():
    menu = _menu_spending(wards={"1": {"total_spent": 12345.0, "categories": {}}})
    out = build_ward_file(_meta(), _ward_record("1"), _aldermen(), _aldermen_safety_record(),
                          menu, _ward_311())
    assert out["menu_spending"]["total_spent"] == 12345.0
    assert out["menu_spending"]["data_tier"] == "proxy"
    assert "available" not in out["menu_spending"]


def test_build_ward_file_sr311_merge_and_honest_absence():
    out_present = build_ward_file(_meta(), _ward_record("1"), _aldermen(),
                                  _aldermen_safety_record(), _menu_spending(), _ward_311())
    assert out_present["sr311"]["total"] == 500
    assert out_present["sr311"]["data_tier"] == "proxy"

    out_absent = build_ward_file(_meta(), _ward_record("2"), _aldermen(),
                                 _aldermen_safety_record(), _menu_spending(), _ward_311())
    assert out_absent["sr311"]["available"] is False
    assert out_absent["sr311"]["data_tier"] == "proxy"


def test_build_ward_file_one_pager_url_unpadded():
    out = build_ward_file(_meta(), _ward_record("7"), _aldermen(wards=[]),
                          _aldermen_safety_record(aldermen=[]), _menu_spending(), _ward_311(wards=[]))
    assert out["one_pager_url"] == SITE_BASE_URL + "/ward.html?ward=7"
    assert "ward=07" not in out["one_pager_url"]


def test_build_ward_file_see_also_links():
    out = build_ward_file(_meta(), _ward_record("1"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["see_also"]["corridors"] == SITE_BASE_URL + "/api/v1/corridors.json"
    assert out["see_also"]["wards_index"] == SITE_BASE_URL + "/api/v1/wards/index.json"


def test_build_ward_file_crashes_url():
    out = build_ward_file(_meta(), _ward_record("7"), _aldermen(wards=[]),
                          _aldermen_safety_record(aldermen=[]), _menu_spending(), _ward_311(wards=[]))
    assert out["crashes_url"] == SITE_BASE_URL + "/api/v1/crashes/ward-07.json"


def test_build_ward_file_no_top_corridors_key():
    # Plan deviation: corridors.json has no ward linkage/geometry, so ward
    # files must not invent a "top corridors for this ward" section.
    out = build_ward_file(_meta(), _ward_record("1"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert "top_corridors" not in out
    assert "corridors" not in out


def test_build_ward_file_envelope_mixed_with_tier_note():
    out = build_ward_file(_meta(), _ward_record("1"), _aldermen(), _aldermen_safety_record(),
                          _menu_spending(), _ward_311())
    assert out["_meta"]["data_tier"] == "mixed"
    assert out["_meta"].get("tier_note")
    assert out["_meta"]["human_page"] == out["one_pager_url"]
