"""refresh_reporting's BNA block: findings.json is fully rebuilt by an offline
refresh, so the BNA finding must be re-appended from whatever source is
available (raw pull > committed bna_scores.json) — but the committed file and
its meta entry are only rewritten when a real raw pull is present (the same
never-mutate-what-you-can't-rebuild invariant as osm_trails)."""
import json

import aggregate
import refresh_reporting
from refresh_reporting import apply_bna, upsert_meta_sources


RAW = {
    "city": {"id": "chi", "name": "Chicago"},
    "history": [{"id": "r26", "score": 11.08, "version": "26.05",
                 "created_at": "2026-05-08T21:53:50Z"}],
    "latest": {"id": "r26", "score": 11.08, "version": "26.05",
               "infrastructure": {"low_stress_miles": 1834.3,
                                  "high_stress_miles": 6267.2},
               "people": {"people": 5.28}},
    "cities_index": [{"id": "chi", "score": 11.08, "population": 2746349}],
}
COMMITTED = {"data_tier": "crowdsourced", "score": 11.08, "version": "26.05",
             "as_of": "2026-05-08", "history": [
                 {"version": "26.05", "score": 11.08, "as_of": "2026-05-08"}],
             "context": {}, "subscores": {},
             "low_stress_miles": 1834.3, "high_stress_miles": 6267.2,
             "note": "OpenStreetMap-derived."}


def _dirs(tmp_path, monkeypatch, raw=None, committed=None):
    raw_dir = tmp_path / "raw"; raw_dir.mkdir()
    site_dir = tmp_path / "site"; site_dir.mkdir()
    if raw is not None:
        (raw_dir / "bna.json").write_text(json.dumps(raw))
    if committed is not None:
        (site_dir / "bna_scores.json").write_text(json.dumps(committed))
    for mod in (aggregate, refresh_reporting):
        monkeypatch.setattr(mod, "RAW_DIR", raw_dir)
        monkeypatch.setattr(mod, "SITE_DATA_DIR", site_dir)
    return raw_dir, site_dir


def test_apply_bna_from_committed_appends_finding_without_rewriting(tmp_path, monkeypatch):
    raw_dir, site_dir = _dirs(tmp_path, monkeypatch, committed=COMMITTED)
    before = (site_dir / "bna_scores.json").read_text()
    findings = [{"id": "ksi-trend"}]
    bna, rebuilt = apply_bna(findings)
    assert not rebuilt
    assert [f["id"] for f in findings] == ["ksi-trend", "bna-score"]
    assert (site_dir / "bna_scores.json").read_text() == before  # untouched


def test_apply_bna_from_raw_rewrites_committed_file(tmp_path, monkeypatch):
    raw_dir, site_dir = _dirs(tmp_path, monkeypatch, raw=RAW,
                              committed={"score": 99, "stale": True})
    findings = []
    bna, rebuilt = apply_bna(findings)
    assert rebuilt
    assert findings and findings[0]["id"] == "bna-score"
    written = json.loads((site_dir / "bna_scores.json").read_text())
    assert written["score"] == 11.08  # rebuilt from raw, stale file replaced


def test_apply_bna_noop_when_no_source(tmp_path, monkeypatch):
    _dirs(tmp_path, monkeypatch)
    findings = [{"id": "ksi-trend"}]
    bna, rebuilt = apply_bna(findings)
    assert bna is None and not rebuilt
    assert [f["id"] for f in findings] == ["ksi-trend"]


def test_upsert_meta_places_bna_between_osm_trails_and_main_routes():
    meta = {"sources": [
        {"id": "crashes"}, {"id": "mellow_routes"},
        {"id": "ward_safety_index"},
    ]}
    months = [{"month": "2020-01"}]
    mellow_connectors = {"features": [{"properties": {"parts": 3}}]}
    osm_trails = {"features": [{"id": 1}]}
    main_routes = {"lines": [{"id": "a"}]}
    network_nodes = {"nodes": [{"id": "n1"}]}
    upsert_meta_sources(meta, months, "2020-01-15", mellow_connectors, osm_trails,
                        main_routes, network_nodes,
                        bna_scores=COMMITTED, upsert_bna=True)
    ids = [s["id"] for s in meta["sources"]]
    assert ids.index("bna_scores") == ids.index("osm_trails") + 1
    assert ids.index("main_routes") == ids.index("bna_scores") + 1
    entry = meta["sources"][ids.index("bna_scores")]
    assert entry["tier"] == "crowdsourced"
    assert entry["records"] == 1  # one history entry


def test_upsert_meta_skips_bna_when_not_rebuilt():
    meta = {"sources": [{"id": "crashes"}, {"id": "ward_safety_index"}]}
    upsert_meta_sources(meta, [{"month": "2020-01"}], "2020-01-15",
                        {"features": []}, {"features": []},
                        {"lines": []}, {"nodes": []},
                        bna_scores=COMMITTED, upsert_bna=False)
    assert "bna_scores" not in [s["id"] for s in meta["sources"]]
