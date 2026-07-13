import hashlib
import json

import pytest

import emit_api
from config import CRASH_ID_PREFIX_LEN, SITE_BASE_URL, CONTRACT_VERSION
from emit_api import (COMPARABLE_DANGER_SCORE_DESC, build_citywide, build_corridors_api,
                      build_crash_slice, build_index, build_news_api, build_proposed_api,
                      build_ward_file, build_wards_index, crash_id_prefixes, emit_all)


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


def _news_items(items=None):
    if items is None:
        items = [
            {"title": "Ward 1 bike lane wins praise", "url": "https://example.com/a",
             "source": "Example News", "published": "2026-07-01T00:00:00+00:00",
             "matches": {
                 "wards": [{"ward": "1", "via": "'Ward 1' in headline"}],
                 "aldermen": [{"name": "Alder One", "ward": "1",
                              "via": "'Alder One' in headline"}],
                 "routes": [{"id": "halsted", "name": "Halsted Line",
                            "via": "'Halsted' in headline"}],
                 "projects": [{"id": "archer-avenue",
                              "name": "Archer Avenue Traffic Safety Project",
                              "via": "'Archer Avenue' in headline"}],
             }},
            {"title": "Unrelated safety story", "url": "https://example.com/b",
             "source": "Example News", "published": "2026-06-01T00:00:00+00:00",
             "matches": {"wards": [], "aldermen": [], "routes": [], "projects": []}},
        ]
    return {"data_tier": "real", "match_tier": "derived",
           "as_of": "2026-07-13T16:10:11+00:00",
           "note": "Recent public news coverage of Chicago bike/street safety.",
           "items": items}


def _proposed_projects(projects=None):
    if projects is None:
        projects = [
            {"id": "archer-avenue", "name": "Archer Avenue Traffic Safety Project",
             "status": "installed, being modified", "status_as_of": "2026-07-13",
             "status_note": "Protected lanes installed; some parking restored.",
             "description": "Complete Streets redesign of Archer Avenue.",
             "wards": ["12"],
             "official_links": [{"text": "CDOT page", "url": "https://example.com/cdot"}],
             "news_phrases": ["Archer Avenue Traffic Safety"],
             "citations": [{"title": "Cite title", "url": "https://example.com/cite",
                           "source": "Block Club Chicago", "published": "2026-04-30"}],
             "news_phrases_ctx": ["Archer Avenue", "Archer Ave"],
             "coverage": [{"title": "Coverage headline", "url": "https://example.com/cov",
                          "source": "Streetsblog Chicago",
                          "published": "2026-07-02T04:10:00+00:00",
                          "via": "'Archer Avenue' in headline"}]},
        ]
    return {"data_tier": "derived", "coverage_tier": "real", "match_tier": "derived",
           "as_of": "2026-07-13T16:10:11+00:00",
           "note": "Hand-curated roster of active Chicago bikeway/trail proposals.",
           "projects": projects}


def _crash_id(n):
    # 128-hex-char, matching the real crashes_cyclist.geojson crash_id shape.
    return hashlib.sha512(f"crash-{n}".encode()).hexdigest()


def _crash_feature(crash_id, ward="1", date="2024-05-19T11:51:00.000", lon=-87.670612,
                   lat=41.997585, injury_severity="none", dooring=False, hit_and_run=False,
                   street="6346 N CLARK ST", crash_type="PEDALCYCLIST", lighting="DAYLIGHT",
                   segment_id="656", data_tier="real"):
    props = {"crash_id": crash_id, "date": date, "injury_severity": injury_severity,
            "dooring": dooring, "hit_and_run": hit_and_run, "crash_type": crash_type,
            "lighting": lighting, "street": street, "ward": ward, "segment_id": segment_id,
            "data_tier": data_tier}
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
           "properties": props}


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

    # One crash per ward, plus one with ward=null — excluded from every slice
    # and exercised by the null-ward-exclusion test below.
    crash_features = [_crash_feature(_crash_id(n), ward=str(n)) for n in range(1, n_wards + 1)]
    crash_features.append(_crash_feature(_crash_id(9001), ward=None))
    (dir_ / "crashes_cyclist.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": crash_features}))

    (dir_ / "news_items.json").write_text(json.dumps(_news_items()))
    (dir_ / "proposed_projects.json").write_text(json.dumps(_proposed_projects()))


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


def test_envelope_methodology_present_and_follows_human_page():
    out = build_corridors_api(_meta(), _corridors(), _intersections())
    assert out["_meta"]["methodology"] == SITE_BASE_URL + "/methodology.html"
    keys = list(out["_meta"].keys())
    assert keys.index("methodology") == keys.index("human_page") + 1


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
    bytes_ = {"citywide.json": 1234, "corridors.json": 5678, "wards/index.json": 999,
             "news.json": 2222, "proposed.json": 3333}
    bytes_.update(overrides)
    return bytes_


def test_build_index_lists_exactly_the_known_endpoints():
    out = build_index(_meta(), _endpoint_bytes())
    paths = [e["path"] for e in out["endpoints"]]
    assert paths == ["citywide.json", "corridors.json", "wards/index.json",
                     "news.json", "proposed.json"]


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
              SITE_BASE_URL + "/api/v1/wards/ward-40.json",
              SITE_BASE_URL + "/api/v1/crashes/ward-40.json",
              SITE_BASE_URL + "/api/v1/news.json",
              SITE_BASE_URL + "/api/v1/proposed.json"}
    assert 6 <= len(out["fetch_recipes"]) <= 7
    for recipe in out["fetch_recipes"]:
        assert recipe["question"] and recipe["then"]
        for url in recipe["fetch"]:
            assert url in allowed


def test_build_index_news_and_proposed_fetch_recipes_present():
    out = build_index(_meta(), _endpoint_bytes())
    news_recipes = [r for r in out["fetch_recipes"]
                    if SITE_BASE_URL + "/api/v1/news.json" in r["fetch"]]
    proposed_recipes = [r for r in out["fetch_recipes"]
                        if SITE_BASE_URL + "/api/v1/proposed.json" in r["fetch"]]
    assert len(news_recipes) == 1
    assert len(proposed_recipes) == 1


def test_build_index_crashes_fetch_recipe_present():
    out = build_index(_meta(), _endpoint_bytes())
    crash_recipes = [r for r in out["fetch_recipes"]
                     if SITE_BASE_URL + "/api/v1/crashes/ward-40.json" in r["fetch"]]
    assert len(crash_recipes) == 1
    assert "ward 40" in crash_recipes[0]["question"].lower()
    assert "columnar" in crash_recipes[0]["then"].lower()


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


def test_build_index_planned_no_longer_lists_wards_or_crashes():
    out = build_index(_meta(), _endpoint_bytes())
    assert not any("wards/" in entry for entry in out["planned"])
    assert not any("crashes/" in entry for entry in out["planned"])
    # still-unpublished namespaces stay
    assert any("routes/" in entry for entry in out["planned"])
    assert any("council/" in entry for entry in out["planned"])
    assert any("schemas/" in entry for entry in out["planned"])


def test_build_index_omits_ward_and_crash_families_when_no_files_given():
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


def test_build_index_crash_family_present_with_count_and_real_max_bytes():
    crash_files_bytes = {f"crashes/ward-{n:02d}.json": 2000 + n for n in range(1, 51)}
    out = build_index(_meta(), _endpoint_bytes(), crash_files_bytes=crash_files_bytes)
    families = {f["path_template"]: f for f in out["families"]}
    fam = families["crashes/ward-{NN}.json"]
    assert fam["count"] == 50
    assert fam["bytes_approx_max"] == max(crash_files_bytes.values())
    assert fam["example"] == SITE_BASE_URL + "/api/v1/crashes/ward-01.json"


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
    assert "obstruction" not in (api_dir / "crashes" / "ward-01.json").read_text().lower()


# --- 6. emit_all IO orchestration ----------------------------------------------

def test_emit_all_writes_all_files(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    # phase-1 (2) + wards/index.json (1) + 50 ward files + 50 crash files
    # + news.json (1) + proposed.json (1) + index.json (1) = 106
    assert len(written) == 106
    expected = {"citywide.json", "corridors.json", "index.json", "wards/index.json",
               "news.json", "proposed.json"}
    expected |= {f"wards/ward-{n:02d}.json" for n in range(1, 51)}
    expected |= {f"crashes/ward-{n:02d}.json" for n in range(1, 51)}
    assert set(written) == expected
    for name in written:
        assert (api_dir / name).exists()


def test_emit_all_files_within_budget(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    for path, size in written.items():
        budget = (emit_api.API_CRASH_SLICE_BUDGET_BYTES if path.startswith("crashes/")
                 else emit_api.API_SIZE_BUDGET_BYTES)
        assert size <= budget, f"{path} over budget: {size}"


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
    stale_crash = api_dir / "crashes" / "ward-99.json"
    stale_crash.parent.mkdir(parents=True, exist_ok=True)
    stale_crash.write_text("{}")
    schema = api_dir / "schemas" / "whatever.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_text("{}")

    emit_all()

    assert not stale.exists()
    assert not stale.parent.exists()  # emptied routes/ dir pruned too
    assert not stale_ward.exists()  # stale ward-99.json pruned; wards/ itself stays (real files)
    assert not stale_crash.exists()  # same, for crashes/
    assert (api_dir / "wards").exists()
    assert (api_dir / "crashes").exists()
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


# --- 10. crash_id_prefixes -------------------------------------------------------

def test_crash_id_prefixes_unique_ids_all_get_the_short_prefix():
    ids = [_crash_id(1), _crash_id(2), _crash_id(3)]
    out = crash_id_prefixes(ids)
    assert set(out) == set(ids)
    for full_id in ids:
        assert out[full_id] == full_id[:CRASH_ID_PREFIX_LEN]
        assert len(out[full_id]) == CRASH_ID_PREFIX_LEN


def test_crash_id_prefixes_collision_falls_back_to_full_id_both_sides():
    shared = "a" * CRASH_ID_PREFIX_LEN
    id_a = shared + "1" * 20
    id_b = shared + "2" * 20
    id_c = "b" * CRASH_ID_PREFIX_LEN + "3" * 20  # distinct prefix, unaffected

    out = crash_id_prefixes([id_a, id_b, id_c])

    assert out[id_a] == id_a
    assert out[id_b] == id_b
    assert out[id_c] == id_c[:CRASH_ID_PREFIX_LEN]


def test_crash_id_prefixes_returns_full_length_map():
    ids = [_crash_id(n) for n in range(1, 6)]
    out = crash_id_prefixes(ids)
    assert len(out) == len(ids)


def test_crash_id_prefixes_skips_missing_ids_without_crashing():
    ids = [_crash_id(1), None, ""]
    out = crash_id_prefixes(ids)  # must not raise
    assert out[_crash_id(1)] == _crash_id(1)[:CRASH_ID_PREFIX_LEN]
    assert None not in out
    assert "" not in out


# --- 11. build_crash_slice --------------------------------------------------------

def test_build_crash_slice_columns_exact():
    out = build_crash_slice(_meta(), "40", [], {})
    assert out["columns"] == ["crash_id", "date", "lat", "lng", "injury_severity",
                              "dooring", "hit_and_run", "street"]


def test_build_crash_slice_row_values_rounded_ordered_and_verbatim_date():
    full_id = _crash_id(1)
    feature = _crash_feature(full_id, lon=-87.1234567, lat=41.7654321,
                             injury_severity="fatal", dooring=True, hit_and_run=False,
                             street="123 N MAIN ST", date="2024-05-19T11:51:00.000")
    id_map = crash_id_prefixes([full_id])

    out = build_crash_slice(_meta(), "40", [feature], id_map)

    assert out["rows"] == [[
        full_id[:CRASH_ID_PREFIX_LEN],
        "2024-05-19T11:51:00.000",
        round(41.7654321, 5),
        round(-87.1234567, 5),
        "fatal",
        True,
        False,
        "123 N MAIN ST",
    ]]


def test_build_crash_slice_missing_property_becomes_null():
    full_id = _crash_id(2)
    feature = _crash_feature(full_id)
    del feature["properties"]["hit_and_run"]  # simulate a genuinely absent property
    id_map = crash_id_prefixes([full_id])

    out = build_crash_slice(_meta(), "40", [feature], id_map)

    assert out["rows"][0][6] is None


def test_build_crash_slice_explicit_null_property_becomes_null():
    full_id = _crash_id(3)
    feature = _crash_feature(full_id, dooring=None)
    id_map = crash_id_prefixes([full_id])

    out = build_crash_slice(_meta(), "40", [feature], id_map)

    assert out["rows"][0][5] is None


def test_build_crash_slice_count_matches_row_count_and_preserves_order():
    features = [_crash_feature(_crash_id(n), street=f"{n} N ORDER ST") for n in range(3)]
    ids = [f["properties"]["crash_id"] for f in features]
    id_map = crash_id_prefixes(ids)

    out = build_crash_slice(_meta(), "40", features, id_map)

    assert out["count"] == 3
    assert len(out["rows"]) == 3
    assert [row[7] for row in out["rows"]] == ["0 N ORDER ST", "1 N ORDER ST", "2 N ORDER ST"]


def test_build_crash_slice_note_mentions_prefix_len_rounding_and_dropped_columns():
    out = build_crash_slice(_meta(), "40", [], {})
    note = out["note"]
    assert str(CRASH_ID_PREFIX_LEN) in note
    assert "5 decimal" in note
    for dropped_column in ("crash_type", "lighting", "segment_id"):
        assert dropped_column in note


def test_build_crash_slice_empty_ward_has_columns_but_no_rows():
    out = build_crash_slice(_meta(), "40", [], {})
    assert out["columns"]
    assert out["rows"] == []
    assert out["count"] == 0


def test_build_crash_slice_links_and_envelope():
    out = build_crash_slice(_meta(), "7", [], {})
    assert out["ward"] == "7"
    assert out["ward_url"] == SITE_BASE_URL + "/api/v1/wards/ward-07.json"
    assert out["full_data_url"] == SITE_BASE_URL + "/data/crashes_cyclist.geojson"
    assert out["_meta"]["data_tier"] == "real"
    assert out["_meta"]["human_page"] == SITE_BASE_URL + "/index.html"


def test_build_crash_slice_worst_case_1200_rows_stays_under_budget():
    # A synthetic ward bigger than the real worst ward (27, 1,187 crashes),
    # with realistic field values: unique 128-hex ids (so all get the short
    # prefix — no collisions), a weighted injury_severity mix matching the
    # real dataset's distribution (non_incapacitating is most common, not
    # the shortest value), and street strings around the real ~17-char
    # average length.
    severities_weighted = (["non_incapacitating"] * 49 + ["none"] * 28 +
                           ["reported_not_evident"] * 13 + ["incapacitating"] * 9 +
                           ["fatal"] * 1)
    streets = ["6346 N CLARK ST", "2000 S DAMEN AVE", "100 W MADISON ST",
              "1500 N HALSTED ST", "4200 S KING DR"]

    features = []
    for i in range(1200):
        full_id = hashlib.sha512(f"worst-case-{i}".encode()).hexdigest()
        features.append(_crash_feature(
            full_id, ward="27",
            injury_severity=severities_weighted[i % len(severities_weighted)],
            street=streets[i % len(streets)],
            dooring=bool(i % 2), hit_and_run=bool((i + 1) % 2)))
    ids = [f["properties"]["crash_id"] for f in features]
    id_map = crash_id_prefixes(ids)

    out = build_crash_slice(_meta(), "27", features, id_map)
    size = len(json.dumps(out).encode("utf-8"))

    assert out["count"] == 1200
    assert size < emit_api.API_CRASH_SLICE_BUDGET_BYTES


# --- 12. _enforce_budget per-family budgets ---------------------------------------

def test_enforce_budget_crash_file_between_100kb_and_150kb_passes():
    written = {"crashes/ward-01.json": 120_000, "citywide.json": 5_000}
    emit_api._enforce_budget(written)  # must not raise


def test_enforce_budget_crash_file_over_150kb_raises_naming_file():
    written = {"crashes/ward-01.json": 160_000}
    with pytest.raises(SystemExit) as excinfo:
        emit_api._enforce_budget(written)
    assert "crashes/ward-01.json" in str(excinfo.value)
    assert "160,000" in str(excinfo.value)


def test_enforce_budget_non_crash_file_still_fails_at_100kb():
    written = {"citywide.json": 100_001}
    with pytest.raises(SystemExit) as excinfo:
        emit_api._enforce_budget(written)
    assert "citywide.json" in str(excinfo.value)


# --- 13. emit_all crash-slice extension --------------------------------------------

def test_emit_all_writes_50_crash_files(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    crash_files = {f"crashes/ward-{n:02d}.json" for n in range(1, 51)}
    assert crash_files <= set(written)
    for rel in crash_files:
        assert (api_dir / rel).exists()


def test_emit_all_excludes_null_ward_crashes_without_crashing(tmp_path, monkeypatch, capsys):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)  # includes one ward=null crash feature
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_all()  # must not raise

    out = capsys.readouterr().out
    assert "1 features with no ward assignment excluded from slices" in out


def test_emit_all_crash_slice_rows_only_include_matching_ward(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_all()

    ward_1 = json.loads((api_dir / "crashes" / "ward-01.json").read_text())
    assert ward_1["count"] == 1
    ward_1_columns = dict(zip(ward_1["columns"], ward_1["rows"][0]))
    assert ward_1_columns["crash_id"] == _crash_id(1)[:CRASH_ID_PREFIX_LEN]


def test_emit_all_index_has_crash_family_planned_removed_and_fetch_recipe(
        tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_all()

    index = json.loads((api_dir / "index.json").read_text())

    families = {f["path_template"]: f for f in index["families"]}
    fam = families["crashes/ward-{NN}.json"]
    assert fam["count"] == 50
    actual_sizes = [(api_dir / "crashes" / f"ward-{n:02d}.json").stat().st_size
                    for n in range(1, 51)]
    assert fam["bytes_approx_max"] == max(actual_sizes)
    assert fam["example"] == SITE_BASE_URL + "/api/v1/crashes/ward-01.json"

    assert not any("crashes/" in entry for entry in index["planned"])

    crash_recipes = [r for r in index["fetch_recipes"]
                     if any("crashes/ward-40.json" in u for u in r["fetch"])]
    assert len(crash_recipes) == 1


# --- 14. build_news_api ---------------------------------------------------------

def test_build_news_api_trims_via_and_flattens_matches():
    out = build_news_api(_meta(), _news_items())
    item = out["items"][0]
    assert item["title"] == "Ward 1 bike lane wins praise"
    assert item["url"] == "https://example.com/a"
    assert item["source"] == "Example News"
    assert item["published"] == "2026-07-01T00:00:00+00:00"
    assert item["wards"] == ["1"]
    assert item["aldermen"] == ["Alder One"]
    assert item["routes"] == ["halsted"]
    assert item["projects"] == ["archer-avenue"]
    assert "matches" not in item
    assert "via" not in json.dumps(item)


def test_build_news_api_keeps_empty_match_lists_as_empty_arrays():
    out = build_news_api(_meta(), _news_items())
    item = out["items"][1]
    assert item["wards"] == []
    assert item["aldermen"] == []
    assert item["routes"] == []
    assert item["projects"] == []


def test_build_news_api_top_level_note_and_as_of():
    news = _news_items()
    out = build_news_api(_meta(), news)
    assert out["as_of"] == news["as_of"]
    assert out["note"] == news["note"]


def test_build_news_api_envelope_is_mixed_with_tier_note():
    out = build_news_api(_meta(), _news_items())
    assert out["_meta"]["data_tier"] == "mixed"
    assert "verbatim" in out["_meta"]["tier_note"]
    assert "derived" in out["_meta"]["tier_note"]
    assert out["_meta"]["human_page"] == SITE_BASE_URL + "/action.html"


def test_build_news_api_item_count_matches_source():
    news = _news_items()
    out = build_news_api(_meta(), news)
    assert len(out["items"]) == len(news["items"])


# --- 15. build_proposed_api -----------------------------------------------------

def test_build_proposed_api_drops_news_phrases_and_coverage_via():
    out = build_proposed_api(_meta(), _proposed_projects())
    project = out["projects"][0]
    assert "news_phrases" not in project
    assert "news_phrases_ctx" not in project
    assert "via" not in json.dumps(project)


def test_build_proposed_api_keeps_everything_else():
    proposed = _proposed_projects()
    out = build_proposed_api(_meta(), proposed)
    project = out["projects"][0]
    source = proposed["projects"][0]
    assert project["id"] == source["id"]
    assert project["name"] == source["name"]
    assert project["status"] == source["status"]
    assert project["status_as_of"] == source["status_as_of"]
    assert project["status_note"] == source["status_note"]
    assert project["description"] == source["description"]
    assert project["wards"] == source["wards"]
    assert project["official_links"] == source["official_links"]
    assert project["citations"] == source["citations"]


def test_build_proposed_api_coverage_keeps_fields_minus_via():
    out = build_proposed_api(_meta(), _proposed_projects())
    coverage = out["projects"][0]["coverage"][0]
    assert coverage == {"title": "Coverage headline", "url": "https://example.com/cov",
                        "source": "Streetsblog Chicago",
                        "published": "2026-07-02T04:10:00+00:00"}


def test_build_proposed_api_top_level_note_and_as_of():
    proposed = _proposed_projects()
    out = build_proposed_api(_meta(), proposed)
    assert out["as_of"] == proposed["as_of"]
    assert out["note"] == proposed["note"]


def test_build_proposed_api_envelope_is_mixed_with_tier_note():
    out = build_proposed_api(_meta(), _proposed_projects())
    assert out["_meta"]["data_tier"] == "mixed"
    assert "curated" in out["_meta"]["tier_note"].lower()
    assert out["_meta"]["human_page"] == SITE_BASE_URL + "/action.html"


# --- 16. emit_all writes news.json and proposed.json ----------------------------

def test_emit_all_writes_news_and_proposed_under_budget(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    written = emit_all()

    assert "news.json" in written
    assert "proposed.json" in written
    assert (api_dir / "news.json").exists()
    assert (api_dir / "proposed.json").exists()
    assert written["news.json"] <= emit_api.API_SIZE_BUDGET_BYTES
    assert written["proposed.json"] <= emit_api.API_SIZE_BUDGET_BYTES


def test_emit_all_index_lists_news_and_proposed_with_example_questions(
        tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    _write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_all()

    index = json.loads((api_dir / "index.json").read_text())
    by_path = {e["path"]: e for e in index["endpoints"]}
    assert "news.json" in by_path
    assert "proposed.json" in by_path
    for path in ("news.json", "proposed.json"):
        assert 2 <= len(by_path[path]["example_questions"]) <= 3
        assert by_path[path]["bytes_approx"] == (api_dir / path).stat().st_size
