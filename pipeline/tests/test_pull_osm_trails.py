import json
import sys
import types

import pull_osm_trails


class _Resp:
    def __init__(self, payload, ok=True):
        self._payload = payload
        self._ok = ok
    def raise_for_status(self):
        if not self._ok:
            raise RuntimeError("boom")
    def json(self):
        return self._payload


def test_pull_writes_raw_on_success(tmp_path, monkeypatch):
    payload = {"elements": [{"type": "way", "tags": {"name": "Lakefront Trail"},
                             "geometry": [{"lat": 41.8, "lon": -87.6}]}]}
    monkeypatch.setattr(sys, "argv", ["pull_osm_trails.py"])
    monkeypatch.setattr(pull_osm_trails, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_osm_trails.requests, "post",
                        lambda *a, **k: _Resp(payload))
    pull_osm_trails.main()
    written = json.loads((tmp_path / "osm_trails.json").read_text())
    assert written["elements"][0]["tags"]["name"] == "Lakefront Trail"


def test_pull_is_non_fatal_on_failure(tmp_path, monkeypatch, capsys):
    def _boom(*a, **k):
        raise pull_osm_trails.requests.RequestException("network down")
    monkeypatch.setattr(sys, "argv", ["pull_osm_trails.py"])
    monkeypatch.setattr(pull_osm_trails, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_osm_trails.requests, "post", _boom)
    pull_osm_trails.main()  # must NOT raise
    assert not (tmp_path / "osm_trails.json").exists()
    assert "WARNING" in capsys.readouterr().err
