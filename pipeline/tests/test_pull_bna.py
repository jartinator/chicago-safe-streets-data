import json
import sys

import pull_bna


class _Resp:
    def __init__(self, payload, ok=True):
        self._payload = payload
        self._ok = ok
    def raise_for_status(self):
        if not self._ok:
            raise RuntimeError("boom")
    def json(self):
        return self._payload


CITY_RATINGS = {
    "city": {"id": "ccc7c2d3", "name": "Chicago", "state": "Illinois"},
    "ratings": [
        {"id": "old-rating", "score": 9, "version": "24.01",
         "created_at": "2024-03-08T13:51:00Z"},
        {"id": "new-rating", "score": 11.08, "version": "26.05",
         "created_at": "2026-05-08T21:53:50.740620Z"},
    ],
}
RATING_DETAIL = {"id": "new-rating", "score": 11.08, "version": "26.05",
                 "infrastructure": {"low_stress_miles": 1834.3,
                                    "high_stress_miles": 6267.2},
                 "people": {"people": 5.28}}
CITIES_INDEX = [
    {"id": "ccc7c2d3", "name": "Chicago", "score": 11.08, "population": 2746349},
    {"id": "other", "name": "Lake Zurich", "score": 20.9, "population": 19759},
]


def _fake_get(urls_seen):
    def get(url, timeout=None):
        urls_seen.append(url)
        if "city-ratings" in url:
            return _Resp(CITY_RATINGS)
        if "ratings/" in url:
            return _Resp(RATING_DETAIL)
        if "cities-index" in url:
            return _Resp(CITIES_INDEX)
        raise AssertionError(f"unexpected url {url}")
    return get


def test_pull_writes_raw_on_success(tmp_path, monkeypatch):
    urls = []
    monkeypatch.setattr(sys, "argv", ["pull_bna.py"])
    monkeypatch.setattr(pull_bna, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_bna.requests, "get", _fake_get(urls))
    pull_bna.main()
    written = json.loads((tmp_path / "bna.json").read_text())
    assert written["city"]["name"] == "Chicago"
    assert written["latest"]["version"] == "26.05"
    assert len(written["history"]) == 2
    assert len(written["cities_index"]) == 2
    # the detail fetch must target the NEWEST rating by created_at
    assert any("ratings/new-rating" in u for u in urls)


def test_pull_is_non_fatal_on_failure(tmp_path, monkeypatch, capsys):
    def _boom(*a, **k):
        raise pull_bna.requests.RequestException("egress blocked")
    monkeypatch.setattr(sys, "argv", ["pull_bna.py"])
    monkeypatch.setattr(pull_bna, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_bna.requests, "get", _boom)
    pull_bna.main()  # must NOT raise
    assert not (tmp_path / "bna.json").exists()
    assert "WARNING" in capsys.readouterr().err


def test_pull_is_non_fatal_on_empty_ratings(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["pull_bna.py"])
    monkeypatch.setattr(pull_bna, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_bna.requests, "get",
                        lambda url, timeout=None: _Resp({"city": {}, "ratings": []}))
    pull_bna.main()  # must NOT raise
    assert not (tmp_path / "bna.json").exists()
    assert "WARNING" in capsys.readouterr().err
