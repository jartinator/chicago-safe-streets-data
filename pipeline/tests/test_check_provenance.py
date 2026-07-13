import json

import pytest

import check_provenance
from check_provenance import main


def _write_meta(path, provenance="socrata", generated_at="2026-07-01T00:00:00+00:00",
                contract_version="1.11", sources=None):
    path.write_text(json.dumps({
        "provenance": provenance, "generated_at": generated_at,
        "contract_version": contract_version, "sources": sources or [],
    }))


def _write_api_index(path, provenance="socrata", generated_at="2026-07-01T00:00:00+00:00",
                     contract_version="1.11"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "_meta": {"provenance": provenance, "generated_at": generated_at,
                  "contract_version": contract_version},
    }))


def _setup(tmp_path, monkeypatch):
    meta_path = tmp_path / "meta.json"
    api_index_path = tmp_path / "api" / "v1" / "index.json"
    monkeypatch.setattr(check_provenance, "META_PATH", meta_path)
    monkeypatch.setattr(check_provenance, "API_INDEX_PATH", api_index_path)
    monkeypatch.setattr("sys.argv", ["check_provenance.py"])
    return meta_path, api_index_path


def test_missing_api_index_passes_with_note(tmp_path, monkeypatch, capsys):
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path)
    assert not api_index_path.exists()

    main()  # must not raise

    out = capsys.readouterr().out
    assert "not present" in out
    assert "skipping" in out


def test_coherent_api_index_passes(tmp_path, monkeypatch, capsys):
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path, provenance="socrata", generated_at="2026-07-01T00:00:00+00:00",
               contract_version="1.11")
    _write_api_index(api_index_path, provenance="socrata",
                     generated_at="2026-07-01T00:00:00+00:00", contract_version="1.11")

    main()  # must not raise

    out = capsys.readouterr().out
    assert "OK: site/api/v1/index.json provenance/version coherent with meta.json." in out


def test_api_index_fixtures_provenance_fails(tmp_path, monkeypatch):
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path)
    _write_api_index(api_index_path, provenance="fixtures")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "fixtures" in str(excinfo.value).lower()
    assert "emit_api.py" in str(excinfo.value)


def test_api_index_stale_generated_at_fails(tmp_path, monkeypatch):
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path, generated_at="2026-07-01T00:00:00+00:00")
    _write_api_index(api_index_path, generated_at="2026-06-01T00:00:00+00:00")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "stale" in str(excinfo.value).lower()
    assert "emit_api.py" in str(excinfo.value)


def test_api_index_mismatched_contract_version_fails(tmp_path, monkeypatch):
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path, contract_version="1.11")
    _write_api_index(api_index_path, contract_version="1.10")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "stale" in str(excinfo.value).lower()
    assert "emit_api.py" in str(excinfo.value)


def test_api_index_invalid_json_fails(tmp_path, monkeypatch):
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path)
    api_index_path.parent.mkdir(parents=True, exist_ok=True)
    api_index_path.write_text("{not valid json")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "not valid JSON" in str(excinfo.value)


def test_still_fails_on_bad_meta_before_reaching_api_check(tmp_path, monkeypatch):
    # Pre-existing meta.json behavior must be untouched by the API extension.
    meta_path, api_index_path = _setup(tmp_path, monkeypatch)
    _write_meta(meta_path, provenance="fixtures")
    _write_api_index(api_index_path)  # coherent API — must not matter, meta fails first

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert "synthetic fixtures build" in str(excinfo.value)
