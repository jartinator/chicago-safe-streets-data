# B2 — PFB BNA Ward Access Scores Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish per-ward bike-access aggregates computed from PeopleForBikes BNA census-block scores, on ward pages and the ward one-pager only.

**Architecture:** New pipeline pull of the BNA block GeoJSON → annual snapshot → spatial join blocks→wards (existing geopandas pattern) → `site/data/ward_bna_access.json` → new ward-page section + one-pager line. No table column, ever (validation verdict: sortability defeats access framing).

**Tech Stack:** Python (requests, geopandas — already in pipeline/requirements.txt), vanilla JS site.

## Global Constraints

- **GATE G1 (blocks Tasks 5+, i.e. anything user-visible):** PFB redistribution license answer received and recorded in DECISIONS.md. Tracked in Linear ("PFB BNA integration" project). Tasks 1–4 (pull/snapshot/join, unpublished) may proceed.
- **GATE G2 (blocks public launch):** read-aloud test of the access copy with real humans (validation verdict, ORG's precondition). Tracked in Linear.
- **No sortable surface.** The per-ward number must not appear in `site/assets/js/table.js` or any sortable/comparable grid (verdict: WARD).
- **Differential OSM disclosure, verbatim rule:** every surface showing a B2 number carries, in body text (not a footnote): "This score depends on what volunteers have mapped in OpenStreetMap, and mapping is uneven across neighborhoods — it can understate what a neighborhood has, or miss hazards it doesn't." (verdict: ORG, both failure directions.)
- **Anti-disinvestment copy rule (P1):** a low access score is always framed as an investment case; never render or phrase as "low demand".
- **Distribution, not just average** (verdict: US): the ward page shows the block-score spread, not a single number.
- **Plain sentences with neighborhood names** (verdict: RIDER): lead with "Most of [community areas in ward] can't reach a grocery store on low-stress streets", not "Ward 35: 22%".
- Tier: `crowdsourced` on every badge. Source URL pattern and schema: `docs/research/followups/peopleforbikes-bna-evaluation.md`.
- `data/snapshots/bna/` follows the CDOT snapshot convention (`pipeline/snapshot_bike_routes.py`).

---

### Task 1: Pull the census-block file

**Files:**
- Create: `pipeline/pull_bna_blocks.py`
- Test: `pipeline/tests/test_pull_bna_blocks.py`
- Modify: `pipeline/config.py` (append constants), `pipeline/run_all.py` (LIVE_STAGES, after `pull_osm_trails.py`)

**Interfaces:**
- Consumes: `BNA_FILES_BASE_URL`, `BNA_CITY_PATH` from config (Task 1 defines them); `pipeline/pull_bna.py`'s `raw/bna.json` from the B1 build — the current `version` string is read from it so the URL matches the live analysis version.
- Produces: `raw/bna_census_blocks.geojson` (verbatim upstream FeatureCollection; properties per feature include `geoid20`, `pop20`, and `*_score` fields).

- [ ] **Step 1: Write the failing tests** (mirror `test_pull_osm_trails.py` exactly):

```python
import json, sys
import pull_bna_blocks

class _Resp:
    def __init__(self, payload, ok=True):
        self._payload, self._ok = payload, ok
    def raise_for_status(self):
        if not self._ok:
            raise RuntimeError("boom")
    def json(self):
        return self._payload

def test_pull_writes_raw_on_success(tmp_path, monkeypatch):
    payload = {"type": "FeatureCollection", "features": [
        {"type": "Feature",
         "properties": {"geoid20": "170316611004005", "pop20": 64.0,
                        "pop_score": 0.017, "grocery_score": 0.0},
         "geometry": {"type": "Polygon", "coordinates": [[[-87.7, 41.76],
                       [-87.7, 41.77], [-87.69, 41.77], [-87.7, 41.76]]]}}]}
    (tmp_path / "bna.json").write_text(json.dumps({"latest": {"version": "26.05"}}))
    monkeypatch.setattr(sys, "argv", ["pull_bna_blocks.py"])
    monkeypatch.setattr(pull_bna_blocks, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_bna_blocks.requests, "get", lambda *a, **k: _Resp(payload))
    pull_bna_blocks.main()
    written = json.loads((tmp_path / "bna_census_blocks.geojson").read_text())
    assert written["features"][0]["properties"]["geoid20"] == "170316611004005"

def test_pull_is_non_fatal_on_failure(tmp_path, monkeypatch, capsys):
    (tmp_path / "bna.json").write_text(json.dumps({"latest": {"version": "26.05"}}))
    def _boom(*a, **k):
        raise pull_bna_blocks.requests.RequestException("egress blocked")
    monkeypatch.setattr(sys, "argv", ["pull_bna_blocks.py"])
    monkeypatch.setattr(pull_bna_blocks, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_bna_blocks.requests, "get", _boom)
    pull_bna_blocks.main()  # must NOT raise
    assert not (tmp_path / "bna_census_blocks.geojson").exists()
    assert "WARNING" in capsys.readouterr().err

def test_pull_skips_when_no_bna_version(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["pull_bna_blocks.py"])
    monkeypatch.setattr(pull_bna_blocks, "RAW_DIR", tmp_path)
    pull_bna_blocks.main()  # no raw/bna.json → warn and return
    assert "WARNING" in capsys.readouterr().err
```

- [ ] **Step 2: Run to verify failure:** `cd pipeline && python -m pytest tests/test_pull_bna_blocks.py -v` — expect `ModuleNotFoundError: pull_bna_blocks`.
- [ ] **Step 3: Implement.** In `config.py` add (below the B1 `BNA_API_URL` block):

```python
# PFB BNA raw result files (see docs/research/followups/peopleforbikes-bna-evaluation.md).
# Only the CURRENT analysis version is hosted upstream — older versions 404 — hence
# the annual snapshot in data/snapshots/bna/ (Task 2). Non-fatal like Mellow/Overpass.
BNA_FILES_BASE_URL = "https://files.storage.bna.peopleforbikes.org"
BNA_CITY_PATH = "united%20states/illinois/chicago"
```

`pull_bna_blocks.py` (module docstring: what/why/non-fatal, matching `pull_mellow.py` tone):

```python
import argparse, json, sys
import requests
from config import BNA_FILES_BASE_URL, BNA_CITY_PATH, RAW_DIR
from socrata import write_json

def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    bna_meta = RAW_DIR / "bna.json"
    if not bna_meta.exists():
        print("WARNING: raw/bna.json absent (pull_bna.py didn't run?) — skipping "
              "block pull; ward BNA access will ship from the committed data.",
              file=sys.stderr)
        return
    version = json.loads(bna_meta.read_text())["latest"]["version"]
    url = f"{BNA_FILES_BASE_URL}/{BNA_CITY_PATH}/{version}/neighborhood_census_blocks.geojson"
    try:
        resp = requests.get(url, timeout=600)  # large file (10^5 features)
        resp.raise_for_status()
        geojson = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"WARNING: BNA block pull failed ({exc}) — ward BNA access will "
              f"ship from the committed data this run.", file=sys.stderr)
        return
    write_json(RAW_DIR / "bna_census_blocks.geojson", geojson)
    print(f"Feature count: {len(geojson.get('features', []))}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify pass.** `python -m pytest tests/test_pull_bna_blocks.py -v` → 3 passed.
- [ ] **Step 5:** Add `["pull_bna_blocks.py"]` to `LIVE_STAGES` in `run_all.py` directly after the `pull_bna.py` entry (it consumes `raw/bna.json`); update `test_run_all_order.py` if it asserts the stage list.
- [ ] **Step 6: Commit** `feat(pipeline): pull BNA census-block scores (non-fatal)`.

### Task 2: Annual snapshot

**Files:**
- Create: `pipeline/snapshot_bna.py`
- Test: `pipeline/tests/test_snapshot_bna.py`
- Modify: `pipeline/run_all.py` (COMMON_STAGES, after `snapshot_bike_routes.py`)

**Interfaces:**
- Consumes: `raw/bna_census_blocks.geojson`, `raw/bna.json` (version string).
- Produces: `data/snapshots/bna/census_blocks_<version>.geojson` — written once per version; if the file for the current version already exists, it is left untouched (idempotent weekly runs; the upstream file for a given version is immutable).

- [ ] **Step 1: Failing test:** writes snapshot named by version on first run; second run with same version does not rewrite (assert mtime/content unchanged); absent raw → no-op, no error.
- [ ] **Step 2:** Verify fail. **Step 3:** Implement following `snapshot_bike_routes.py` (read it first — copy its guard/naming conventions, swapping date for version). **Step 4:** Verify pass. **Step 5: Commit** `feat(pipeline): version-keyed BNA block snapshots`.

### Task 3: Ward join + aggregation module

**Files:**
- Create: `pipeline/bna_access.py`
- Test: `pipeline/tests/test_bna_access.py`

**Interfaces:**
- Consumes: block FeatureCollection (dict), wards FeatureCollection (dict, `raw/wards.geojson` shape used by `spatial_join.py` — read that module for the ward-id property name before coding).
- Produces: `build_ward_access(blocks_gj, wards_gj) -> dict` with shape:

```python
{
  "as_of_version": "26.05",
  "wards": {
    "35": {
      "population": 55432,               # sum pop20 of joined blocks
      "pop_weighted_mean_score": 14.2,   # 0-100 scale (upstream *_score * 100)
      "pct_pop_low_stress_grocery": 22.4,  # % of pop on blocks with grocery_score >= 0.5
      "block_score_histogram": [n0_9, n10_19, ..., n90_100],  # overall block scores
      "blocks": 412
    }, ...
  }
}
```

- [ ] **Step 1: Failing tests:** synthetic 2-ward, 4-block fixture (blocks fully inside wards); assert population weighting math exactly; assert a block with `pop20: 0` doesn't NaN the mean; assert blocks outside every ward are dropped; assert histogram bins sum to block count.
- [ ] **Step 2:** Verify fail. **Step 3:** Implement with geopandas `sjoin` (predicate `within` on block centroids — blocks nest inside wards except at boundaries; centroid assignment matches how BNA itself treats blocks as atomic). Project to `METRIC_CRS` for centroid math, mirror `spatial_join.py` idioms. **Step 4:** Verify pass. **Step 5: Commit** `feat(pipeline): ward-level BNA access aggregation`.

### Task 4: Wire into aggregate.py + SCHEMA

**Files:**
- Modify: `pipeline/aggregate.py` (call `bna_access.build_ward_access`, write `site/data/ward_bna_access.json`, add meta source entry `bna_blocks` with `records` = block count and the version in `date_range`), `SCHEMA.md` (new file contract + meta entry + changelog, bump CONTRACT_VERSION per repo convention), `pipeline/config.py` (CONTRACT_VERSION), `pipeline/make_fixtures.py` (synthetic `raw/bna_census_blocks.geojson` over fixture wards + synthetic `raw/bna.json` if B1's fixture didn't already add it)
- Test: `pipeline/tests/test_aggregate_bna_access.py`

Fallback rule (mirror mellow/osm): raw absent → do not write the file, do not add the meta source entry (SCHEMA.md rule: "meta.json never claims a source ran when it didn't"); committed `ward_bna_access.json` continues to ship.

- [ ] Failing test → implement → pass → **Commit** `feat(pipeline): publish ward_bna_access.json (contract vX.Y)`.

### Task 5: 🔒 GATE G1 — license answer

- [ ] Confirm the Linear issue "License ask to PeopleForBikes" is Done and the answer recorded in DECISIONS.md. **If the answer is no or unanswered, stop here** — Tasks 1–4 produce unpublished pipeline artifacts only; do not proceed to site surfaces.

### Task 6: Ward page section

**Files:**
- Modify: `site/assets/js/ward-model.js` (pure data shaping — testable), `site/assets/js/ward.js` (render), `site/ward.html` (section container)
- Test: `tests/ui/ward-model.test.js` (extend)

Requirements (all four are Global Constraints, restated): plain-sentence lead with community-area names (the ward→community-area names come from the existing ward page data — check `ward-model.js` for what's available; if absent, use "this ward"); histogram rendering of `block_score_histogram` (10 bins, neutral palette); the differential-OSM disclosure paragraph in body text; crowdsourced badge; no cross-ward comparison links.

- [ ] Failing model test (given a ward's `ward_bna_access` slice → sentence string + histogram bins + badge tier) → implement → pass → render in `ward.js` → **Commit** `feat(site): ward BNA access section (no sortable surface)`.

### Task 7: One-pager line

**Files:**
- Modify: the ward one-pager generator (locate via `grep -ri "one-pager\|printable" site/assets/js docs` — it's the ward print register from the prior study's P3) — one sentence + disclosure footnote.
- [ ] Model test → implement → **Commit** `feat(site): BNA access line on ward one-pager`.

### Task 8: 🔒 GATE G2 — read-aloud test, then launch

- [ ] Confirm the Linear issue "Read-aloud test of B2 access copy" is Done; fold wording changes back into Task 6/7 copy strings; run `pipeline/check_provenance.py` and the full test suite; only then merge the site-surface tasks.

## Self-review checklist

- Verdict coverage: no-sortable-surface (Global + Task 6), differential disclosure (Global + Task 6/7), distribution (Task 3 histogram + Task 6), neighborhood names (Task 6), read-aloud gate (Task 8), license gate (Task 5) — all present.
- Fixtures + non-fatal fallback keep `--fixtures` and egress-blocked runs green (Tasks 1, 4).
