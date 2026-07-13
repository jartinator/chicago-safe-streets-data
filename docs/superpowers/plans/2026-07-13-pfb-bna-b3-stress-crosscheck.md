# B3 — PFB BNA Segment Stress Cross-Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Buffer-match PeopleForBikes BNA per-segment Level of Traffic Stress ratings onto OYL's bikeway network, first as an internal QA report, later as an aggregate public finding — never as a third geometry layer.

**Architecture:** Pull `neighborhood_ways.geojson` → buffer-match stress attributes onto CDOT bike-routes segments (same 25 m technique as the Mellow dedup, `MELLOW_DEDUPE_BUFFER_M`, DECISIONS.md #24) → phase 1: a QA report (CSV artifact, not site data) listing grade-vs-stress disagreements with OSM-recency triage → phase 2 (gated): one aggregate finding card. Per-segment public flags are explicitly out of scope until a correction path exists.

**Tech Stack:** Python (requests, geopandas/shapely — already in pipeline), vanilla JS site (phase 2 only).

## Global Constraints

- **GATE G1 (blocks Phase 2, Tasks 5+):** PFB license answer recorded in DECISIONS.md (shared with the B2 plan — same Linear issue).
- **Two-surface rule (validation verdict):** disagreements are *published and explained* on expert surfaces (methodology/sources/findings/CSV) and *never shown as two competing numbers* on resident surfaces (maps keep OYL's single adjudicated grade). US's kill condition is silent reconciliation; RIDER's kill condition is being made to adjudicate. Both bind.
- **Artifact triage before naming any segment (CDOT's kill condition):** a disagreement row is only reportable when the segment's OSM `osm_id` was edited on/after the facility's earliest snapshot appearance; otherwise it is bucketed `possible-osm-lag`, not `disagreement`.
- **Per-segment public flags are OUT OF SCOPE for this plan.** They need a documented correction path (issue template + review) — a follow-up decision, not a task here.
- **Anti-disinvestment copy rule (P1):** the aggregate finding is worded as an upgrade case ("N miles of bikeways still rate high-stress — here's where upgrades buy the most"), never as infrastructure-isn't-worth-it.
- **Buffer-match error disclosure (US):** the methodology page states the match technique, the 25 m buffer, and the measured unmatched rate from the QA report.
- Tier: `crowdsourced`. Source facts: `docs/research/followups/peopleforbikes-bna-evaluation.md` (ways properties: `osm_id`, `functional_class`, `speed_limit`, `ft_seg_stress`/`tf_seg_stress`, `ft_int_stress`/`tf_int_stress`, `ft_bike_infra`/`tf_bike_infra`).

---

### Task 1: Pull the ways file

**Files:**
- Create: `pipeline/pull_bna_ways.py`
- Test: `pipeline/tests/test_pull_bna_ways.py`
- Modify: `pipeline/config.py` (only if the B2 plan's `BNA_FILES_BASE_URL`/`BNA_CITY_PATH` aren't merged yet — same two constants, define once), `pipeline/run_all.py` (LIVE_STAGES after `pull_bna_blocks.py`, or after `pull_bna.py` if B2 unmerged)

**Interfaces:**
- Consumes: `raw/bna.json` (version string, from B1's `pull_bna.py`).
- Produces: `raw/bna_ways.geojson` — verbatim upstream FeatureCollection, LineString features with the properties listed in Global Constraints.

- [ ] **Step 1: Failing tests** — copy the three-test pattern from the B2 plan's Task 1 verbatim (success writes raw / failure non-fatal / missing `raw/bna.json` warns and returns), with `neighborhood_ways.geojson` as the URL tail, `bna_ways.geojson` as the output, and a LineString fixture feature:

```python
{"type": "Feature",
 "properties": {"osm_id": 4476759, "name": "East Walton Place",
                "functional_class": "residential", "speed_limit": None,
                "ft_bike_infra": None, "tf_bike_infra": None,
                "ft_seg_stress": 3, "tf_seg_stress": 3,
                "ft_int_stress": 1, "tf_int_stress": 1},
 "geometry": {"type": "LineString",
              "coordinates": [[-87.6218, 41.9000], [-87.6219, 41.9000]]}}
```

- [ ] **Step 2:** `python -m pytest tests/test_pull_bna_ways.py -v` → fails (module missing).
- [ ] **Step 3:** Implement — identical structure to `pull_bna_blocks.py` (B2 plan Task 1 Step 3) with the two names swapped; `timeout=600` (the ways file is the largest artifact).
- [ ] **Step 4:** Tests pass. **Step 5:** Add to `LIVE_STAGES`; fix `test_run_all_order.py` if needed. **Step 6: Commit** `feat(pipeline): pull BNA LTS ways (non-fatal)`.

### Task 2: Snapshot

- [ ] Extend `pipeline/snapshot_bna.py` (B2 plan Task 2) to also snapshot `raw/bna_ways.geojson` → `data/snapshots/bna/ways_<version>.geojson`, same idempotency rule and test pattern. If the B2 plan is unexecuted, implement its Task 2 first — it is a strict prerequisite. **Commit** `feat(pipeline): snapshot BNA ways per version`.

### Task 3: Buffer-match + disagreement classification module

**Files:**
- Create: `pipeline/bna_stress.py`
- Test: `pipeline/tests/test_bna_stress.py`

**Interfaces:**
- Consumes: bike-routes FeatureCollection (the `facility_category` property as mapped by `FACILITY_CATEGORY_MAP`), ways FeatureCollection, snapshot dates per segment (from `data/snapshots/` — the earliest snapshot containing the segment; reuse whatever helper `refresh_coverage.py`/`aggregate.py` already has for snapshot iteration — read those modules before coding).
- Produces:

```python
def match_stress(bike_routes_gj, ways_gj, buffer_m=25.0) -> list[dict]
# one dict per bike-route segment:
# {"segment_id", "facility_category",
#  "bna_stress": "low"|"high"|None,     # worst direction: max(ft_seg_stress, tf_seg_stress) — LTS 1-2 = low, 3+ = high; None = no way within buffer
#  "matched_osm_id": int|None}

def classify(matches, osm_edit_dates, segment_first_seen) -> dict
# {"agree": [...], "disagreement": [...], "possible_osm_lag": [...], "unmatched": [...]}
# disagreement = facility_category in {"protected","buffered"} AND bna_stress == "high"
#                AND osm_edit_dates[matched_osm_id] >= segment_first_seen[segment_id]
# possible_osm_lag = same but osm edit predates the facility's first snapshot appearance
```

- [ ] **Step 1: Failing tests:** synthetic geometry — a protected segment with a coincident high-stress way (→ disagreement when OSM edit is recent, → possible_osm_lag when stale); a painted segment matching a low-stress way (→ agree); a segment with no way within 25 m (→ unmatched, `bna_stress: None`); directionality: `ft=1, tf=3` → "high" (worst direction).
- [ ] **Step 2:** Fail. **Step 3:** Implement in `METRIC_CRS` with an STRtree/sjoin_nearest, midpoint-sampling the route segment against buffered ways — read `build_mellow_connectors` in `aggregate.py` first and reuse its buffering idiom. OSM edit dates come from the way's `osm_id` via the OSM API only if already available offline — **they are not**: use the BNA version date as the conservative stand-in (documented limitation in the module docstring; a segment is `possible_osm_lag` unless its facility predates the BNA run). **Step 4:** Pass. **Step 5: Commit** `feat(pipeline): BNA stress buffer-match + disagreement triage`.

### Task 4: Internal QA report (Phase 1 deliverable — no site changes)

**Files:**
- Create: `pipeline/report_bna_stress.py` (writes `pipeline/raw/reports/bna_stress_crosscheck.csv` — gitignored raw artifact, printed summary table to stdout)
- Test: `pipeline/tests/test_report_bna_stress.py`
- Modify: `pipeline/run_all.py` (COMMON_STAGES, after `spatial_join.py`; non-fatal)

Report columns: `segment_id, street_name, facility_category, bna_stress, bucket, matched_osm_id, speed_limit, functional_class`. Summary printed: counts per bucket + unmatched rate (the number the methodology page will later cite).

- [ ] Failing test (given classified buckets → CSV rows + summary counts) → implement → pass → **Commit** `feat(pipeline): internal BNA stress QA report`.
- [ ] **Deliverable checkpoint:** run the report against a real pull; sanity-review the disagreement list (are flagged segments plausible? is the unmatched rate < ~15%?). This human review is the Linear issue "Review first BNA stress QA report" and must be Done before Phase 2.

### Task 5: 🔒 GATE G1 — license answer (same gate as B2 plan Task 5)

- [ ] Linear "License ask to PeopleForBikes" Done, answer in DECISIONS.md, or stop here. Phase 1 artifacts are internal and safe regardless.

### Task 6: Aggregate finding card (Phase 2)

**Files:**
- Modify: `pipeline/aggregate.py` (append finding from the classification buckets when raw present), `SCHEMA.md` (findings id `bna-stress-gap`, changelog + contract bump), `pipeline/make_fixtures.py` (synthetic ways over fixture routes)
- Test: `pipeline/tests/test_aggregate_bna_stress.py`

Finding card content rules (all from the verdict): stat = miles of on-street bikeways whose matched BNA stress is high (`disagreement` + `possible_osm_lag` buckets combined — the split is explained on the methodology page, not the card); description worded as an upgrade case; caveat carries the OSM-currency disclosure and "measures the street, not the rider"; `data_tier: "crowdsourced"`; `map_state` deep-links the main-routes layer, NOT a per-segment flag view.

- [ ] Failing test (buckets → finding dict with exact required copy elements present; raw absent → no finding) → implement → pass → **Commit** `feat: BNA stress aggregate finding (contract vX.Y)`.

### Task 7: Methodology page section (Phase 2)

**Files:**
- Modify: `site/methodology.html` + `site/assets/js/methodology.js` (a "Where our grades and BNA disagree" section: the match technique, 25 m buffer, measured unmatched rate, the triage buckets and what each means, and why residents see one adjudicated grade while this page shows the conflict — the two-surface rule, stated openly)
- Test: `tests/ui/methodology-model.test.js` (extend if the page is model-driven; read it first)

- [ ] Implement → test → **Commit** `docs(site): BNA disagreement methodology section`.

## Self-review checklist

- Verdict coverage: two-surface rule (Global + Tasks 6/7), triage before naming (Global + Task 3 classify, and per-segment flags out of scope), correction-path dependency (explicitly out of scope, documented), buffer error disclosure (Task 4 unmatched rate → Task 7), anti-disinvestment copy (Task 6), license gate (Task 5).
- Phase 1 (Tasks 1–4) is shippable and useful with no license answer and no site changes — it's the internal QA CDOT's persona endorsed.
- Type consistency: `match_stress`/`classify` signatures used identically in Tasks 3, 4, 6.
