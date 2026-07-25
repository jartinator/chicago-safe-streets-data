"""Schema-conformance tests for pipeline/emit_api.py's build_* functions,
against the hand-written JSON Schemas in site/api/v1/schemas/.

TDD note: these tests validate real build_* output (constructed the same way
test_emit_api.py does, reusing its fixtures) against the committed schema
files — they exercise the schemas as a normative contract, not just the
builders' own logic (already covered by test_emit_api.py).
"""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

import emit_api
import test_emit_api as fx  # reuse the fixture builders (all _foo() helpers)
from config import CONTRACT_VERSION
from emit_api import (build_aldermen_api, build_citywide, build_corridors_api,
                      build_council_index, build_council_records_api, build_crash_slice,
                      build_index, build_line_file, build_news_api, build_proposed_api,
                      build_routes_index, build_ward_file, build_wards_index,
                      crash_id_prefixes)

SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "site" / "api" / "v1" / "schemas"


def _registry():
    resources = []
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources), {sid: r.contents for sid, r in resources}


REGISTRY, SCHEMAS_BY_ID = _registry()
BASE_SCHEMA_URL = "https://jartinator.github.io/chicago-safe-streets-data/api/v1/schemas"


def assert_valid(payload, schema_name):
    """Validate payload against the named schema (e.g. "citywide.schema.json"),
    resolving $refs (envelope.schema.json) via the local registry — no network.
    """
    schema_id = f"{BASE_SCHEMA_URL}/{schema_name}"
    assert schema_id in SCHEMAS_BY_ID, f"no such schema: {schema_name}"
    validator = Draft202012Validator(SCHEMAS_BY_ID[schema_id], registry=REGISTRY)
    errors = list(validator.iter_errors(payload))
    if errors:
        e = errors[0]
        loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
        pytest.fail(f"{schema_name} validation failed at {loc!r}: {e.message}")


# --- schemas load and reference envelope.schema.json cleanly -----------------

def test_all_thirteen_schemas_exist_and_load():
    expected = {
        "envelope.schema.json", "index.schema.json", "citywide.schema.json",
        "corridors.schema.json", "wards-index.schema.json", "ward.schema.json",
        "crash-slice.schema.json", "news.schema.json", "proposed.schema.json",
        "routes-index.schema.json", "route-line.schema.json",
        "council-index.schema.json", "council-records.schema.json",
        "council-aldermen.schema.json",
    }
    on_disk = {p.name for p in SCHEMAS_DIR.glob("*.schema.json")}
    assert expected <= on_disk


def test_envelope_schema_requires_the_documented_field_set():
    envelope_schema = SCHEMAS_BY_ID[f"{BASE_SCHEMA_URL}/envelope.schema.json"]
    required = set(envelope_schema["required"])
    assert required == {"api_version", "contract_version", "generated_at", "provenance",
                        "data_tier", "license", "attribution", "human_page",
                        "methodology", "schema", "caveat_contract", "agent_instruction"}
    assert "tier_note" not in required  # optional, mixed-tier only
    # caveat_contract/agent_instruction are required, not optional: the contract
    # declaration and the imperative go in every file or the promise is empty.
    assert "caveats" not in required  # optional, only when one applies


# --- citywide.json: with and without protected_share --------------------------

def test_citywide_with_protected_share_validates():
    out = build_citywide(fx._meta(), fx._citywide_trend(), fx._findings(), fx._mileage_series())
    assert "protected_share" in out
    assert_valid(out, "citywide.schema.json")


def test_citywide_without_protected_share_validates():
    out = build_citywide(fx._meta(), fx._citywide_trend(), fx._findings(),
                         fx._mileage_series(series=[]))
    assert "protected_share" not in out
    assert_valid(out, "citywide.schema.json")


# --- ward file: missing alderman entry (alderman: null + alderman_note) -------

def test_ward_file_missing_alderman_validates():
    out = build_ward_file(fx._meta(), fx._ward_record("2"), fx._aldermen(),
                          fx._aldermen_safety_record(), fx._menu_spending(), fx._ward_311())
    assert out["alderman"] is None
    assert "alderman_note" in out
    assert_valid(out, "ward.schema.json")


def test_ward_file_present_alderman_validates():
    out = build_ward_file(fx._meta(), fx._ward_record("1"), fx._aldermen(),
                          fx._aldermen_safety_record(), fx._menu_spending(), fx._ward_311())
    assert out["alderman"] is not None
    assert_valid(out, "ward.schema.json")


def test_ward_file_honest_gap_menu_and_sr311_shapes_validate():
    # ward "2" has no menu_spending/sr311 entries — {"available": False, ...}.
    out = build_ward_file(fx._meta(), fx._ward_record("2"), fx._aldermen(),
                          fx._aldermen_safety_record(), fx._menu_spending(), fx._ward_311())
    assert out["menu_spending"]["available"] is False
    assert out["sr311"]["available"] is False
    assert_valid(out, "ward.schema.json")


# --- crash slice: zero rows ----------------------------------------------------

def test_crash_slice_zero_rows_validates():
    out = build_crash_slice(fx._meta(), "40", [], {})
    assert out["rows"] == []
    assert out["count"] == 0
    assert_valid(out, "crash-slice.schema.json")


def test_crash_slice_with_rows_validates():
    full_id = fx._crash_id(1)
    feature = fx._crash_feature(full_id)
    id_map = crash_id_prefixes([full_id])
    out = build_crash_slice(fx._meta(), "40", [feature], id_map)
    assert_valid(out, "crash-slice.schema.json")


# --- route line file: trail segment (crashes: null) ---------------------------

def test_route_line_file_trail_segment_null_crashes_validates():
    main_routes = fx._main_routes()
    trail_line = next(l for l in main_routes["lines"] if l["source"] == "osm_trails")
    out = build_line_file(fx._meta(), trail_line, main_routes["features"], fx._network_nodes())
    assert any(m["crashes"] is None for m in out["member_segments"])
    assert_valid(out, "route-line.schema.json")


def test_route_line_file_trail_line_with_no_pct_protected_key_is_null_and_validates():
    # A trail line whose source record genuinely omits pct_protected/
    # crashes_total (the real main_routes.geojson shape) — line.get(...)
    # surfaces that as null, not KeyError or a fabricated 0.
    line = fx._main_routes_line("lakefront-bare", source="osm_trails")
    del line["pct_protected"], line["crashes_total"]
    main_routes = fx._main_routes()
    out = build_line_file(fx._meta(), line, main_routes["features"], fx._network_nodes())
    assert out["pct_protected"] is None
    assert out["crashes_total"] is None
    assert_valid(out, "route-line.schema.json")


def test_route_line_file_street_segment_validates():
    main_routes = fx._main_routes()
    street_line = next(l for l in main_routes["lines"] if l["source"] == "bike_routes")
    out = build_line_file(fx._meta(), street_line, main_routes["features"], fx._network_nodes())
    assert_valid(out, "route-line.schema.json")


# --- the remaining build_* functions, one representative call each ------------

def test_corridors_api_validates():
    out = build_corridors_api(fx._meta(), fx._corridors(), fx._intersections())
    assert_valid(out, "corridors.schema.json")


def test_wards_index_validates():
    out = build_wards_index(fx._meta(), fx._ward_safety_index())
    assert_valid(out, "wards-index.schema.json")


def test_news_api_validates():
    out = build_news_api(fx._meta(), fx._news_items())
    assert_valid(out, "news.schema.json")


def test_proposed_api_validates():
    out = build_proposed_api(fx._meta(), fx._proposed_projects())
    assert_valid(out, "proposed.schema.json")


def test_routes_index_validates():
    out = build_routes_index(fx._meta(), fx._main_routes(), fx._network_nodes())
    assert_valid(out, "routes-index.schema.json")


def test_council_index_validates():
    out = build_council_index(fx._meta(), fx._hearings(), fx._council_records())
    assert_valid(out, "council-index.schema.json")


def test_council_records_api_validates():
    out = build_council_records_api(fx._meta(), fx._council_records())
    assert_valid(out, "council-records.schema.json")


def test_aldermen_api_validates():
    out = build_aldermen_api(fx._meta(), fx._aldermen(), fx._aldermen_safety_record(),
                             fx._menu_spending())
    assert_valid(out, "council-aldermen.schema.json")


def test_index_validates():
    out = build_index(fx._meta(), fx._endpoint_bytes())
    assert_valid(out, "index.schema.json")


def test_index_with_families_validates():
    ward_files_bytes = {f"wards/ward-{n:02d}.json": 1000 + n for n in range(1, 51)}
    crash_files_bytes = {f"crashes/ward-{n:02d}.json": 2000 + n for n in range(1, 51)}
    line_files_bytes = {"routes/line-milwaukee.json": 500, "routes/line-lakefront.json": 400}
    out = build_index(fx._meta(), fx._endpoint_bytes(), ward_files_bytes, crash_files_bytes,
                      line_files_bytes)
    assert_valid(out, "index.schema.json")


# --- emit_api._envelope now threads a schema URL -------------------------------

def test_envelope_schema_field_points_at_matching_schema_file():
    out = build_citywide(fx._meta(), fx._citywide_trend(), fx._findings(), fx._mileage_series())
    assert out["_meta"]["schema"] == f"{BASE_SCHEMA_URL}/citywide.schema.json"


def test_emit_all_output_carries_schema_field_and_validates(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "api"
    fx._write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)

    emit_api.emit_all()

    citywide = json.loads((api_dir / "citywide.json").read_text())
    assert citywide["_meta"]["schema"] == f"{BASE_SCHEMA_URL}/citywide.schema.json"
    assert_valid(citywide, "citywide.schema.json")

    ward = json.loads((api_dir / "wards" / "ward-01.json").read_text())
    assert ward["_meta"]["schema"] == f"{BASE_SCHEMA_URL}/ward.schema.json"
    assert_valid(ward, "ward.schema.json")
