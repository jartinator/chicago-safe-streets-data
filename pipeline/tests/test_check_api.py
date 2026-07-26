"""Regression test for check_api.py: exercises the real committed
site/api/v1/ tree in this worktree (offline, no fixtures) — same "run it
against the real thing" spirit as test_check_provenance.py's coverage of
check_provenance.py, but check_provenance.py's own tests use synthetic
tmp_path fixtures exclusively, so this file also covers check_api.py's
per-check unit behavior with small synthetic trees.
"""
import json
from pathlib import Path

import pytest

import check_api
from check_api import main

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REAL_API_DIR = REPO_ROOT / "site" / "api" / "v1"
REAL_SCHEMAS_DIR = REAL_API_DIR / "schemas"


# --- regression: the real committed site/api/v1/ tree --------------------------

@pytest.mark.skipif(not (REAL_API_DIR / "index.json").exists(),
                    reason="site/api/v1/index.json not present in this checkout")
def test_check_api_passes_against_real_committed_tree(capsys):
    main()  # must not raise SystemExit
    out = capsys.readouterr().out
    assert "OK:" in out
    assert "validate against their schemas" in out
    assert "within their size budgets" in out
    assert "exactly cover" in out
    assert "contract_version/api_version" in out


# --- synthetic tmp_path fixtures for each check in isolation -------------------

_ENVELOPE_REQUIRED = {
    "api_version": "1", "contract_version": "1.14", "generated_at": "2026-07-01T00:00:00+00:00",
    "provenance": "socrata", "data_tier": "real",
    "license": "L", "attribution": "A", "human_page": "https://example.com/h",
    "methodology": "https://example.com/m", "schema": "https://example.com/api/v1/schemas/citywide.schema.json",
}


def _minimal_envelope_schema(schema_id):
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id,
        "type": "object",
        "properties": {"_meta": {"type": "object"}},
        "required": ["_meta"],
        "additionalProperties": True,
    }


def _setup(tmp_path, monkeypatch):
    api_dir = tmp_path / "api" / "v1"
    schemas_dir = api_dir / "schemas"
    schemas_dir.mkdir(parents=True)
    monkeypatch.setattr(check_api, "API_DIR", api_dir)
    monkeypatch.setattr(check_api, "SCHEMAS_DIR", schemas_dir)
    monkeypatch.setattr(check_api, "INDEX_PATH", api_dir / "index.json")
    return api_dir, schemas_dir


def _write_schema(schemas_dir, name, base_url="https://example.com"):
    schema_id = f"{base_url}/api/v1/schemas/{name}"
    (schemas_dir / name).write_text(json.dumps(_minimal_envelope_schema(schema_id)))


def _write_index(api_dir, endpoints=None, families=None, contract_version="1.14",
                 api_version="1"):
    index = {
        "_meta": {**_ENVELOPE_REQUIRED, "contract_version": contract_version,
                 "api_version": api_version,
                 "schema": "https://example.com/api/v1/schemas/index.schema.json"},
        "endpoints": endpoints or [],
        "families": families or [],
    }
    (api_dir / "index.json").write_text(json.dumps(index))
    return index


def test_missing_index_json_skips_cleanly(tmp_path, monkeypatch, capsys):
    _setup(tmp_path, monkeypatch)
    main()  # must not raise
    out = capsys.readouterr().out
    assert "not present" in out
    assert "skipping" in out


def _coherent_citywide():
    """citywide.json came under the co-location contract at phase 6, so a tree
    that is "coherent" now has to carry the contract envelope and the two
    migrated claims — `trend` and `findings[*]`. Check 5 is entitled to fail a
    tree that lists the file as migrated and then ships neither claim.

    The other tests in this file trip an earlier check and never reach Check 5,
    so they keep their bare-envelope fixture.
    """
    return {
        "_meta": {**_ENVELOPE_REQUIRED, "caveat_contract": "v1",
                  "agent_instruction": "Always name the caveat next to the number."},
        "trend": {
            "data_tier": "real", "window_end": "2026-06-30", "note": "n",
            "caveat_tags": ["provisional", "not_ridership_normalized"],
            "caveat": ("Monthly counts of police-reported cyclist crashes "
                       "through 2026-06-30. The last 2 entries are provisional "
                       "and can rise. Counts are not adjusted for ridership."),
            "months": [{"month": "2026-06", "crashes": 10, "injury_crashes": 5,
                       "ksi": 1, "fatal": 0, "caveat_tags": ["provisional"]}],
        },
        "findings": [{
            "id": "ksi-trend", "title": "t", "stat": "216", "description": "d",
            "data_tier": "real",
            "caveat_tags": ["not_ridership_normalized", "provisional"],
            "caveat": ("Crashes over the 12 months ending 2026-06-30 "
                       "(216 crashes). The most recent 2 months are "
                       "provisional. Counts are not adjusted for ridership."),
        }],
    }


def test_all_four_checks_pass_on_a_coherent_minimal_tree(tmp_path, monkeypatch, capsys):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "citywide.schema.json")

    (api_dir / "citywide.json").write_text(json.dumps(_coherent_citywide()))

    _write_index(api_dir, endpoints=[
        {"path": "citywide.json", "url": "https://example.com/api/v1/citywide.json",
         "bytes_approx": (api_dir / "citywide.json").stat().st_size,
         "description": "d", "example_questions": ["q?"]},
    ])

    main()  # must not raise
    out = capsys.readouterr().out
    assert "OK: 2 site/api/v1 files validate against their schemas." in out
    assert "OK: all 2 site/api/v1 files are within their size budgets." in out
    assert "OK: index.json's endpoints/families exactly cover" in out
    assert "OK: all 2 site/api/v1 files agree with index.json" in out


def test_schema_conformance_failure_names_file_and_reason(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "citywide.schema.json")

    # citywide.json missing the required _meta key entirely.
    (api_dir / "citywide.json").write_text(json.dumps({}))
    _write_index(api_dir, endpoints=[
        {"path": "citywide.json", "url": "u", "bytes_approx": 2, "description": "d",
         "example_questions": ["q?"]},
    ])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "citywide.json" in str(excinfo.value)
    assert "does not validate" in str(excinfo.value)


def test_invalid_json_fails_naming_file(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "citywide.schema.json")
    (api_dir / "citywide.json").write_text("{not valid json")
    _write_index(api_dir, endpoints=[
        {"path": "citywide.json", "url": "u", "bytes_approx": 2, "description": "d",
         "example_questions": ["q?"]},
    ])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "citywide.json" in str(excinfo.value)
    assert "not valid JSON" in str(excinfo.value)


def test_size_budget_failure_names_file_and_budget(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "citywide.schema.json")
    monkeypatch.setattr(check_api, "API_SIZE_BUDGET_BYTES", 5)

    citywide = {"_meta": {**_ENVELOPE_REQUIRED}}
    (api_dir / "citywide.json").write_text(json.dumps(citywide))
    _write_index(api_dir, endpoints=[
        {"path": "citywide.json", "url": "u",
         "bytes_approx": (api_dir / "citywide.json").stat().st_size,
         "description": "d", "example_questions": ["q?"]},
    ])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "citywide.json" in str(excinfo.value)
    assert "API_SIZE_BUDGET_BYTES" in str(excinfo.value)


def test_orphan_file_not_in_manifest_fails(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "citywide.schema.json")

    citywide = {"_meta": {**_ENVELOPE_REQUIRED}}
    (api_dir / "citywide.json").write_text(json.dumps(citywide))
    # index.json lists no endpoints — citywide.json is an orphan.
    _write_index(api_dir, endpoints=[])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "citywide.json" in str(excinfo.value)
    assert "not covered" in str(excinfo.value)


def test_dangling_manifest_entry_fails(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    # index.json claims an endpoint that was never written to disk.
    _write_index(api_dir, endpoints=[
        {"path": "citywide.json", "url": "u", "bytes_approx": 2, "description": "d",
         "example_questions": ["q?"]},
    ])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "citywide.json" in str(excinfo.value)
    assert "not present on disk" in str(excinfo.value)


def test_family_count_mismatch_fails(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "ward.schema.json")

    (api_dir / "wards").mkdir()
    ward = {"_meta": {**_ENVELOPE_REQUIRED}}
    (api_dir / "wards" / "ward-01.json").write_text(json.dumps(ward))

    _write_index(api_dir, families=[
        {"path_template": "wards/ward-{NN}.json", "url_template": "u", "count": 2,
         "example": "e", "bytes_approx_max": 100, "description": "d",
         "example_questions": ["q?"]},
    ])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "wards/ward-{NN}.json" in str(excinfo.value)
    assert "count" in str(excinfo.value).lower()


def test_version_incoherence_fails(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")
    _write_schema(schemas_dir, "citywide.schema.json")

    citywide = {"_meta": {**_ENVELOPE_REQUIRED, "contract_version": "1.10"}}
    (api_dir / "citywide.json").write_text(json.dumps(citywide))
    _write_index(api_dir, endpoints=[
        {"path": "citywide.json", "url": "u",
         "bytes_approx": (api_dir / "citywide.json").stat().st_size,
         "description": "d", "example_questions": ["q?"]},
    ], contract_version="1.14")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "citywide.json" in str(excinfo.value)
    assert "contract_version" in str(excinfo.value)


def test_no_known_schema_mapping_fails(tmp_path, monkeypatch):
    api_dir, schemas_dir = _setup(tmp_path, monkeypatch)
    _write_schema(schemas_dir, "index.schema.json")

    (api_dir / "mystery.json").write_text(json.dumps({"_meta": {}}))
    _write_index(api_dir, endpoints=[
        {"path": "mystery.json", "url": "u", "bytes_approx": 2, "description": "d",
         "example_questions": ["q?"]},
    ])

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "mystery.json" in str(excinfo.value)
    assert "no known schema mapping" in str(excinfo.value)
