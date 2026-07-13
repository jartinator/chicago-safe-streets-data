"""build_bna's source priority in aggregate.py: raw pull -> committed site data -> None.

Mirrors the osm-trails fallback chain — the BNA host may be egress-blocked in the
pipeline environment, in which case the committed bna_scores.json keeps shipping
(and keeps producing its finding) until a live pull succeeds somewhere.
"""
import json

import aggregate


RAW = {
    "city": {"id": "chi", "name": "Chicago"},
    "history": [{"id": "r26", "score": 11.08, "version": "26.05",
                 "created_at": "2026-05-08T21:53:50Z"}],
    "latest": {"id": "r26", "score": 11.08, "version": "26.05",
               "infrastructure": {"low_stress_miles": 1834.3,
                                  "high_stress_miles": 6267.2},
               "people": {"people": 5.28}},
    "cities_index": [
        {"id": "chi", "score": 11.08, "population": 2746349},
        {"id": "nyc", "score": 40.0, "population": 8000000},
    ],
}


def test_build_bna_prefers_raw(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"; raw_dir.mkdir()
    site_dir = tmp_path / "site"; site_dir.mkdir()
    (raw_dir / "bna.json").write_text(json.dumps(RAW))
    (site_dir / "bna_scores.json").write_text(json.dumps({"score": 99, "stale": True}))
    monkeypatch.setattr(aggregate, "RAW_DIR", raw_dir)
    monkeypatch.setattr(aggregate, "SITE_DATA_DIR", site_dir)
    out = aggregate.build_bna()
    assert out["score"] == 11.08          # fresh build, not the stale committed file
    assert out["version"] == "26.05"


def test_build_bna_falls_back_to_committed(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"; raw_dir.mkdir()
    site_dir = tmp_path / "site"; site_dir.mkdir()
    committed = {"data_tier": "crowdsourced", "score": 11.08, "version": "26.05",
                 "as_of": "2026-05-08", "history": []}
    (site_dir / "bna_scores.json").write_text(json.dumps(committed))
    monkeypatch.setattr(aggregate, "RAW_DIR", raw_dir)
    monkeypatch.setattr(aggregate, "SITE_DATA_DIR", site_dir)
    out = aggregate.build_bna()
    assert out == committed


def test_build_bna_none_when_nothing_available(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"; raw_dir.mkdir()
    site_dir = tmp_path / "site"; site_dir.mkdir()
    monkeypatch.setattr(aggregate, "RAW_DIR", raw_dir)
    monkeypatch.setattr(aggregate, "SITE_DATA_DIR", site_dir)
    assert aggregate.build_bna() is None
