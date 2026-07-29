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
from config import CONTRACT_VERSION, SKILL_ENTRY_URL, SKILL_NAME
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


# --- the published skill block (index.json's top-level `skill`) ----------------

def _skill_files():
    return [
        {"path": "skills/x/SKILL.md",
         "url": "https://example.invalid/skills/x/SKILL.md",
         "bytes": 3, "sha256": "a" * 64},
    ]


def test_index_with_skill_block_validates_and_round_trips_the_hashes():
    out = build_index(fx._meta(), fx._endpoint_bytes(), skill_files=_skill_files())
    assert_valid(out, "index.schema.json")
    assert out["skill"]["files"] == _skill_files()
    assert out["skill"]["entry_point"] == SKILL_ENTRY_URL


def test_index_skill_block_carries_a_non_empty_errors_object():
    """The blocker from round 1: R1's error catalogue shipped nowhere. `errors`
    is required inside `skill`'s sub-schema, so a block without it fails
    check_api.py's _check_schema_conformance rather than passing quietly."""
    out = build_index(fx._meta(), fx._endpoint_bytes(), skill_files=_skill_files())
    errors = out["skill"]["errors"]
    assert errors
    for key in ("there_is_no_error_body", "on_404_for_a_skill_url",
                "on_sha256_mismatch", "on_caveat_contract_mismatch",
                "on_the_guide_disagreeing_with_this_manifest",
                "on_this_block_disappearing"):
        assert errors[key].strip(), f"{key} is empty"


def test_index_skill_block_without_errors_fails_the_schema():
    out = build_index(fx._meta(), fx._endpoint_bytes(), skill_files=_skill_files())
    del out["skill"]["errors"]
    schema = SCHEMAS_BY_ID[f"{BASE_SCHEMA_URL}/index.schema.json"]
    errors = list(Draft202012Validator(schema, registry=REGISTRY).iter_errors(out))
    assert any("'errors' is a required property" in e.message for e in errors), errors


def test_index_without_skill_files_emits_no_skill_key():
    """`skill` is NOT in the schema's top-level `required`, so the two existing
    build_index tests keep passing and main is valid before this ships."""
    assert "skill" not in build_index(fx._meta(), fx._endpoint_bytes())
    assert "skill" not in build_index(fx._meta(), fx._endpoint_bytes(), skill_files=[])


def test_index_skill_block_is_pure_ascii():
    """write_json's json.dump defaults to ensure_ascii=True: one em dash costs
    six bytes rather than three and makes the block's measured size depend on a
    serialiser flag."""
    out = build_index(fx._meta(), fx._endpoint_bytes(), skill_files=_skill_files())
    json.dumps(out["skill"]).encode("ascii")


def test_read_published_skill_is_empty_when_the_directory_is_absent(tmp_path):
    assert emit_api.read_published_skill(tmp_path / "nope") == []


def test_read_published_skill_hashes_lf_normalised_bytes(tmp_path):
    """A Windows checkout with autocrlf on must produce the same manifest as the
    Linux runner, or every hash in the committed index.json flips by platform."""
    root = tmp_path / SKILL_NAME
    (root / "reference").mkdir(parents=True)
    (root / "SKILL.md").write_bytes(b"a\r\nb\r\n")
    (root / "reference" / "endpoints.md").write_bytes(b"a\nb\n")

    out = emit_api.read_published_skill(root)
    assert [f["path"] for f in out] == [
        f"skills/{SKILL_NAME}/SKILL.md",
        f"skills/{SKILL_NAME}/reference/endpoints.md",
    ]
    assert out[0]["bytes"] == out[1]["bytes"] == 4
    assert out[0]["sha256"] == out[1]["sha256"]
    assert out[0]["url"].endswith(out[0]["path"])


def test_read_published_skill_orders_by_posix_string_not_path_object(tmp_path):
    """sorted(root.rglob("*")) compares Path objects, and PureWindowsPath is
    case-insensitive while PurePosixPath is not — so SKILL.md sorts before
    reference/ on Linux and after it on Windows. files[] order reaches a
    committed generated file, so it must not depend on the machine that ran the
    build."""
    root = tmp_path / SKILL_NAME
    (root / "reference").mkdir(parents=True)
    (root / "SKILL.md").write_bytes(b"x")
    (root / "reference" / "aaa.md").write_bytes(b"y")
    (root / "reference" / "zzz.md").write_bytes(b"z")

    paths = [f["path"] for f in emit_api.read_published_skill(root)]
    assert paths == sorted(paths), paths
    assert paths[0].endswith("SKILL.md")


def test_index_skill_block_makes_no_publishes_no_numbers_claim():
    """Soren 08-guide-precedence.md section 4, "Not covered": his test forbids the
    claim in llms.txt only. Both strings landed in one commit, so bind the second
    surface too. The claim could never have been made true -- SKILL.md's worked
    question-and-answer is the guide's teaching device, and deleting it to make
    the sentence true would destroy the thing that moved qualifier survival from
    0.188 to 0.753."""
    out = build_index(fx._meta(), fx._endpoint_bytes(), skill_files=_skill_files())
    assert "publishes no numbers" not in json.dumps(out)
