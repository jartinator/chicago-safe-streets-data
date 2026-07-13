# Bike-Lane Coverage Metrics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish two new coverage metrics — per-ward "% of bikeway miles that are protected" and "% of street miles with any bike infrastructure" (per ward AND citywide) — and surface them in the ward rankings table and the findings page (not the maps).

**Architecture:** A new pull module fetches Chicago's street centerline layer (the coverage denominator). `aggregate.py` gains coverage computation (shared, drift-proof functions), a new published `site/data/road_network.json`, three new fields per ward in `ward_safety_index.json`, and a new citywide finding. A one-shot `refresh_coverage.py` pulls only street centerlines and joins them against already-committed site data so real numbers publish in this PR without a multi-hour full pipeline run. The table UI gains two columns.

**Tech Stack:** Python 3.12, geopandas/shapely, Socrata SODA API, vanilla-JS static site, plain-Node test scripts.

## Global Constraints

- **Street centerlines dataset:** Socrata `pr57-gg9e` ("transportation" — Street Center Lines). The prettier `6imu-meau` map view is NOT usable: its SODA rows come back empty `{}` and its geospatial export endpoint returns a truncated 53-byte body (both verified live 2026-07-12). `pr57-gg9e` is tabular with `the_geom`, 56,338 rows, last updated June 2021.
- **Coverage denominator:** street classes `{"2", "3", "4"}` (arterial, collector, local) with status `"N"` only. Verified live 2026-07-12: that slice sums to ~3,945 centerline miles, matching the city's oft-cited ~4,000 street miles. Excluded: `1` (expressway — cycling prohibited), `9` (ramps), `5`/`7` (alley-type stubs), `99`/`E`/`S` (system artifacts), `RIV` (river channels), and statuses `P` (proposed), `V` (vacated), `UC`, `C`.
- **Coverage numerator:** on-street bikeway miles ONLY — the `trail` facility category is excluded from every coverage numerator and every per-ward protected-share denominator, matching `crash_metrics.protected_share`. Off-street trails never enter these stats.
- **Method consistency:** numerator and denominator of any ratio use projected geometry length in `METRIC_CRS` (EPSG:26916), converted with `_MILES_PER_M = 1/1609.34`.
- **Published-schema discipline:** adding output keys requires bumping `CONTRACT_VERSION` (1.8 → **1.9**) in `pipeline/config.py` and updating `SCHEMA.md` (see `aggregate.py` module docstring).
- **New ward fields (exact names):** `bikeway_pct_protected`, `road_miles`, `bikeway_pct_of_roads` — all nullable; `null` when the input is missing or the denominator is 0, never 0-by-default.
- **New finding id:** `street-coverage`, inserted immediately after `protected-share`.
- **New published file:** `site/data/road_network.json` (shape defined in Task 2).
- **Fixtures pollution:** any `run_all.py --fixtures` or `make_fixtures.py` run writes fixture data into `site/data/` and stamps `pipeline/raw/PROVENANCE` with `fixtures`. After verifying, ALWAYS `git restore site/data` and delete `pipeline/raw/PROVENANCE` — a stale marker mislabels the next live build.
- **No map changes.** `map.js`, `network.js`, `main-routes-model.js` are out of scope.
- **UI tests** are plain Node scripts: run each as `node tests/ui/<file>.test.js` (no `node --test`).
- **Pipeline scripts run from `pipeline/`** (`cd pipeline` first) — they import sibling modules directly.

---

### Task 1: Street-centerline pull module + fixtures

**Files:**
- Modify: `pipeline/config.py` (DATASETS entry + filter constants)
- Create: `pipeline/pull_street_centerlines.py`
- Modify: `pipeline/run_all.py` (LIVE_STAGES + docstring stage list)
- Modify: `pipeline/make_fixtures.py` (synthetic street grid)

**Interfaces:**
- Produces: `raw/street_centerlines.geojson` — GeoJSON FeatureCollection; each feature's `properties` carry `trans_id, class, status, street_nam, street_typ, pre_dir, length` (all strings, straight from Socrata); geometry is MultiLineString (live) or LineString (fixtures) in EPSG:4326.
- Produces: config constants `STREET_CLASSES_INCLUDED = {"2", "3", "4"}` and `STREET_STATUS_INCLUDED = {"N"}` (Task 2 imports these).

- [ ] **Step 1: Add config entries**

In `pipeline/config.py`, add to the `DATASETS` dict:

```python
    "street_centerlines": "pr57-gg9e",  # Street Center Lines ("transportation") — the
                                        # tabular SODA copy. The 6imu-meau map view's rows
                                        # come back empty and its geospatial export is
                                        # truncated server-side (verified 2026-07-12).
                                        # 56,338 segments, last updated 2021-06; the street
                                        # grid changes slowly, fine for a denominator.
```

Below `FACILITY_CATEGORIES`, add:

```python
# Coverage denominator: which street-centerline segments count as the city's
# bikeable surface-street grid. CLASS: 1=expressway (cycling prohibited),
# 2=arterial, 3=collector, 4=local, 5/7=alley-type stubs, 9=ramp,
# 99/E/S=system artifacts, RIV=river channel. STATUS: N=in service (P=proposed,
# V=vacated, UC/C=not usable roadway). Classes 2+3+4 with status N sum to
# ~3,945 centerline miles — matching the city's oft-cited ~4,000 street miles
# (verified live 2026-07-12).
STREET_CLASSES_INCLUDED = {"2", "3", "4"}
STREET_STATUS_INCLUDED = {"N"}
```

- [ ] **Step 2: Create the pull module**

Create `pipeline/pull_street_centerlines.py`:

```python
"""Pull the Street Center Lines layer from the Chicago Data Portal.

Fetches the tabular Socrata copy (pr57-gg9e, "transportation") — the canonical
6imu-meau map view returns empty SODA rows and a truncated geospatial export
(verified 2026-07-12) — paging the SODA rows with a slim $select and archiving
them as a GeoJSON FeatureCollection at raw/street_centerlines.geojson.
Class/status filtering is mapped downstream (aggregate.py); this module only
fetches and archives.
"""
import argparse
from collections import Counter

from config import DATASETS, RAW_DIR
from socrata import fetch_all, write_json

SELECT = "trans_id,the_geom,class,status,street_nam,street_typ,pre_dir,length"


def main():
    parser = argparse.ArgumentParser(
        description="Pull Chicago street center lines from the Chicago Data Portal."
    )
    parser.parse_args()

    feats = []
    classes = Counter()
    for row in fetch_all(DATASETS["street_centerlines"], select=SELECT, order=":id"):
        geom = row.get("the_geom")
        if not geom:
            continue
        props = {k: v for k, v in row.items() if k != "the_geom"}
        feats.append({"type": "Feature", "geometry": geom, "properties": props})
        classes[row.get("class") or "(blank)"] += 1

    write_json(RAW_DIR / "street_centerlines.geojson",
               {"type": "FeatureCollection", "features": feats})
    hist = ", ".join(f"{c}:{n}" for c, n in sorted(classes.items()))
    print(f"street_centerlines: {len(feats)} segments; class counts: {hist}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Wire into run_all.py**

In `LIVE_STAGES`, after the line `["pull_bike_routes.py"], ["pull_wards.py"], ["pull_aldermen.py"],` add `["pull_street_centerlines.py"],` on its own line. In the module docstring's stage list, mention it in stage 3 (e.g. append `pull_street_centerlines` to the stage-3 line).

- [ ] **Step 4: Add the fixture generator**

In `pipeline/make_fixtures.py`, add near `build_wards()`:

```python
def build_street_centerlines():
    """Synthetic surface-street grid covering the fixture wards, plus a few
    excluded-class/status rows so aggregate's denominator filter is exercised."""
    s, w, n, e = BBOX
    feats = []
    tid = 0

    def seg(coords, klass, status):
        nonlocal tid
        tid += 1
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"trans_id": str(tid), "class": klass, "status": status,
                           "street_nam": f"FIXTURE {tid}", "street_typ": "ST",
                           "pre_dir": "N", "length": "0"},
        })

    lat = s
    while lat <= n:                       # E-W locals every ~2.2 km
        seg([[w, lat], [e, lat]], "4", "N")
        lat = round(lat + 0.02, 6)
    lng = w
    while lng <= e:                       # N-S locals every ~2.5 km
        seg([[lng, s], [lng, n]], "4", "N")
        lng = round(lng + 0.03, 6)
    # Excluded rows — must NOT count as road miles downstream:
    seg([[w, s], [e, n]], "1", "N")                        # expressway
    seg([[w, (s + n) / 2], [e, (s + n) / 2]], "9", "N")    # ramp
    seg([[(w + e) / 2, s], [(w + e) / 2, n]], "4", "P")    # proposed local
    return {"type": "FeatureCollection", "features": feats}
```

In `make_fixtures.main()`, alongside the other `write_json(RAW_DIR / ...)` calls, add:

```python
    write_json(RAW_DIR / "street_centerlines.geojson", build_street_centerlines())
```

- [ ] **Step 5: Verify**

```bash
cd pipeline && python make_fixtures.py && python - <<'EOF'
import json
gj = json.load(open("raw/street_centerlines.geojson"))
feats = gj["features"]
assert len(feats) > 20, len(feats)
classes = {f["properties"]["class"] for f in feats}
assert "1" in classes and "9" in classes and "4" in classes, classes
statuses = {f["properties"]["status"] for f in feats}
assert "P" in statuses and "N" in statuses, statuses
print("fixture street grid OK:", len(feats), "features")
EOF
python -c "import pull_street_centerlines"  # import check only; no live pull here
```

Expected: `fixture street grid OK: ...` and a clean import. Then clean up fixture pollution:

```bash
rm -f pipeline/raw/PROVENANCE
```

(`make_fixtures.py` alone does not touch `site/data/`, so no restore needed in this task.)

- [ ] **Step 6: Commit**

```bash
git add pipeline/config.py pipeline/pull_street_centerlines.py pipeline/run_all.py pipeline/make_fixtures.py
git commit -m "feat: pull street centerlines (coverage denominator) + fixtures"
```

---

### Task 2: Coverage metrics in aggregate/crash_metrics/refresh_reporting + schema docs

**Files:**
- Modify: `pipeline/config.py` (CONTRACT_VERSION 1.8 → 1.9)
- Modify: `pipeline/aggregate.py`
- Modify: `pipeline/crash_metrics.py`
- Modify: `pipeline/refresh_reporting.py`
- Modify: `SCHEMA.md`, `DECISIONS.md`

**Interfaces:**
- Consumes (Task 1): `raw/street_centerlines.geojson`; `config.STREET_CLASSES_INCLUDED`, `config.STREET_STATUS_INCLUDED`.
- Produces (Tasks 3–4 rely on these exact names):
  - `aggregate.load_street_centerlines() -> GeoDataFrame | None`
  - `aggregate.street_miles_by_ward(streets_gdf, wards_gdf) -> {ward: miles}`
  - `aggregate.build_road_network(streets_gdf, wards_gdf, routes_gj, as_of_date) -> dict` (the `road_network.json` payload)
  - `aggregate.ward_coverage_fields(cats: {category: miles}, road_miles: float | None) -> dict` with keys `bikeway_pct_protected`, `road_miles`, `bikeway_pct_of_roads`
  - `aggregate.ward_bikeway_miles_by_category` now ALSO accepts the published `bike_routes.geojson` shape (features carrying `facility_category`)
  - `crash_metrics.build_findings_core(..., road_coverage=None)` — `road_coverage` is the `citywide` dict from `road_network.json`; emits finding id `street-coverage` when present
  - `site/data/road_network.json` shape:
    ```
    { data_tier: "real", as_of: "YYYY-MM-DD" | null, note,
      citywide: { road_miles, onstreet_bikeway_miles, pct_with_bike_infra } | null,
      wards: [{ ward, road_miles }] }
    ```
  - `ward_safety_index.json` ward records gain `bikeway_pct_protected`, `road_miles`, `bikeway_pct_of_roads` (all nullable).

- [ ] **Step 1: Bump contract version**

In `pipeline/config.py`: `CONTRACT_VERSION = "1.9"`.

- [ ] **Step 2: Generalize `ward_bikeway_miles_by_category`**

In `pipeline/aggregate.py`, inside `ward_bikeway_miles_by_category`, replace the `recs = [...]` construction so features that already carry a `facility_category` property (published shape) use it directly, while raw snapshot features keep the existing type-key resolution:

```python
    type_key = _first_key(feats[0]["properties"],
                          ["displayroute", "displayrou", "bikeroute", "type", "facility"])
    unmatched = Counter()

    def _cat(f):
        p = f["properties"]
        if p.get("facility_category"):
            return p["facility_category"]
        return facility_category(str(p.get(type_key)) if type_key else "", unmatched)

    recs = [{"facility_category": _cat(f), "geometry": shape(f["geometry"])}
            for f in feats]
```

Extend the function docstring with one line noting it accepts both the raw snapshot shape and the published shape.

- [ ] **Step 3: Add the coverage functions**

In `pipeline/aggregate.py` (near `ward_bikeway_miles`), add — and add `STREET_CLASSES_INCLUDED, STREET_STATUS_INCLUDED` to the `config` import:

```python
def load_street_centerlines():
    """Filtered surface-street GeoDataFrame from raw/street_centerlines.geojson,
    or None when the pull didn't run. Applies the coverage-denominator filter
    (STREET_CLASSES_INCLUDED x STREET_STATUS_INCLUDED); see DECISIONS.md."""
    path = RAW_DIR / "street_centerlines.geojson"
    if not path.exists():
        print("  WARNING street_centerlines.geojson missing — road coverage metrics "
              "will be null this run (pull_street_centerlines.py did not run)")
        return None
    gj = json.loads(path.read_text())
    feats = [f for f in gj["features"]
             if (f["properties"].get("class") or "") in STREET_CLASSES_INCLUDED
             and (f["properties"].get("status") or "") in STREET_STATUS_INCLUDED
             and f.get("geometry")]
    if not feats:
        return None
    return gpd.GeoDataFrame.from_features(feats, crs=OUTPUT_CRS)


def street_miles_by_ward(streets_gdf, wards_gdf):
    """{ward: surface-street centerline miles} — same clipped-overlay method as
    ward_bikeway_miles, so ratios over the two are method-consistent."""
    streets_m = streets_gdf.to_crs(METRIC_CRS)
    wards_m = wards_gdf.to_crs(METRIC_CRS)[["ward", "geometry"]]
    overlaid = gpd.overlay(streets_m[["geometry"]], wards_m, how="intersection")
    miles = defaultdict(float)
    for _, row in overlaid.iterrows():
        if row.geometry is not None:
            miles[row["ward"]] += row.geometry.length * _MILES_PER_M
    return dict(miles)


def build_road_network(streets_gdf, wards_gdf, routes_gj, as_of_date):
    """road_network.json payload: surface-street miles citywide + per ward, and
    the citywide share of street miles carrying any on-street bike infrastructure.

    routes_gj is the PUBLISHED bike_routes shape (features carry
    facility_category). The numerator excludes the `trail` category — off-street
    trails aren't roads. Both sides of the ratio are projected centerline miles
    (METRIC_CRS), method-consistent even though the citywide mileage series
    prefers CDOT's mi_ctrline field.
    """
    onstreet = [f for f in routes_gj["features"]
                if f["properties"].get("facility_category") != "trail"]
    onstreet_mi = 0.0
    if onstreet:
        g = gpd.GeoDataFrame.from_features(onstreet, crs=OUTPUT_CRS).to_crs(METRIC_CRS)
        onstreet_mi = float(g.geometry.length.sum()) * _MILES_PER_M
    road_mi = float(streets_gdf.to_crs(METRIC_CRS).geometry.length.sum()) * _MILES_PER_M
    ward_road_miles = street_miles_by_ward(streets_gdf, wards_gdf)
    return {
        "data_tier": "real",
        "as_of": as_of_date,
        "note": ("Surface-street centerline miles (Street Center Lines layer, classes "
                 "2/3/4 = arterial/collector/local, status N; expressways, ramps, "
                 "alleys, and river channels excluded) vs on-street bikeway centerline "
                 "miles (trail category excluded). Both sides are projected geometry "
                 "lengths, so the ratio is method-consistent. The city's street "
                 "centerline layer was last updated 2021-06 — the grid changes slowly."),
        "citywide": {
            "road_miles": round(road_mi, 1),
            "onstreet_bikeway_miles": round(onstreet_mi, 1),
            "pct_with_bike_infra": (round(100 * onstreet_mi / road_mi, 1)
                                    if road_mi else None),
        },
        "wards": [{"ward": w, "road_miles": round(m, 2)}
                  for w, m in sorted(ward_road_miles.items(), key=lambda kv: int(kv[0]))],
    }


def ward_coverage_fields(cats, road_miles):
    """The three per-ward coverage fields, from that ward's facility-category miles
    and surface-street miles. Shared by build_ward_safety_index (live) and
    refresh_coverage.py (offline merge) so the two paths cannot drift.
    `trail` is excluded from on-street miles throughout."""
    onstreet = sum(m for c, m in cats.items() if c != "trail")
    rm = road_miles if road_miles and road_miles > 0 else None
    return {
        "bikeway_pct_protected": (round(100 * cats.get("protected", 0.0) / onstreet, 1)
                                  if onstreet > 0 else None),
        "road_miles": round(road_miles, 2) if road_miles is not None else None,
        "bikeway_pct_of_roads": round(100 * onstreet / rm, 1) if rm else None,
    }
```

- [ ] **Step 4: Thread coverage through `build_ward_safety_index`**

Change the signature to `def build_ward_safety_index(crashes, wards_gj, routes_gj, wards_gdf, snapshot_dir=SNAPSHOT_DIR, tuples=None, road_miles_by_ward=None):`. Before the `records = []` loop add:

```python
    cats_by_ward = ward_bikeway_miles_by_category(routes_gj, wards_gdf)
```

Inside the per-ward loop, after building the record dict, merge the new fields:

```python
        rec = { ...existing keys unchanged... }
        rec.update(ward_coverage_fields(
            cats_by_ward.get(w, {}),
            road_miles_by_ward.get(w) if road_miles_by_ward else None))
        records.append(rec)
```

Extend the top-level `note` with: `"bikeway_pct_protected is the protected share of the ward's on-street (non-trail) bikeway miles; bikeway_pct_of_roads is the share of the ward's surface-street miles (see road_network.json) with any on-street bike infrastructure; both are null when the denominator is missing or zero."`

- [ ] **Step 5: The `street-coverage` finding**

In `pipeline/crash_metrics.py`, change `build_findings_core(tuples, by_category_miles, corridors, ward_counts, as_of_date)` to accept a trailing keyword arg `road_coverage=None`, update its docstring order comment to `ksi-trend, protected-share, street-coverage, top-corridors, hit-and-run, ward-concentration, dooring-undercount`, and insert directly after the `protected-share` block:

```python
    if road_coverage and road_coverage.get("road_miles"):
        rc = road_coverage
        findings.append({
            "id": "street-coverage",
            "title": "How much of the street grid has bike infrastructure",
            "stat": f"{rc['pct_with_bike_infra']:.0f}%",
            "description": (f"Chicago has {rc['road_miles']:,.0f} miles of surface "
                            f"streets (arterials, collectors, and neighborhood "
                            f"streets). {rc['onstreet_bikeway_miles']:,.0f} miles — "
                            f"{rc['pct_with_bike_infra']:.0f}% — have any bike "
                            f"infrastructure at all, counting everything from "
                            f"sharrows to protected lanes."),
            "caveat": ("Centerline miles on both sides of the ratio. Expressways, "
                       "ramps, alleys, and river channels are excluded from street "
                       "miles; off-street trails are excluded from bikeway miles. "
                       "The street centerline layer was last updated in 2021 — the "
                       "grid changes slowly."),
            "map_state": {"screen": "map", "layers": ["mainroutes"], "filters": {}},
            "data_tier": "real",
        })
```

- [ ] **Step 6: Wire the live path in `aggregate.main()`**

After `wards_gj, wards_gdf = build_wards(...)` add:

```python
    streets_gdf = load_street_centerlines()
    as_of_date = datetime.now(timezone.utc).date().isoformat()
    if streets_gdf is not None:
        road_network = build_road_network(streets_gdf, wards_gdf, routes_gj, as_of_date)
    else:
        road_network = {"data_tier": "real", "as_of": None,
                        "note": ("Street centerlines were not pulled this run — road "
                                 "coverage metrics are unavailable. Run "
                                 "pull_street_centerlines.py."),
                        "citywide": None, "wards": []}
    road_miles_by_ward = {r["ward"]: r["road_miles"] for r in road_network["wards"]} or None
```

(`as_of_date` already exists further down for findings — reuse ONE definition; don't define it twice.) Pass `road_miles_by_ward=road_miles_by_ward` to `build_ward_safety_index(...)`. Change `build_findings` to accept and forward `road_coverage`: `def build_findings(tuples, corridors, wards_gj, as_of_date, road_coverage=None)` → `build_findings_core(..., road_coverage=road_coverage)`; call it with `road_coverage=road_network["citywide"]`. Add `write_json(SITE_DATA_DIR / "road_network.json", road_network)` beside the other writes. In `meta["sources"]`, directly after the `bike_routes` entry, add:

```python
            {"id": "street_centerlines", "name": "Street Center Lines (surface-street grid)",
             "tier": "real",
             "records": int(len(streets_gdf)) if streets_gdf is not None else None,
             "date_range": None},
```

Append road coverage to the final sanity print, e.g. `f", street coverage: {road_network['citywide']['pct_with_bike_infra']}%"` when citywide is not None.

- [ ] **Step 7: `refresh_reporting.py` reads the committed road network**

After the `bikeway_mileage_series` load, add:

```python
    road_path = SITE_DATA_DIR / "road_network.json"
    road_coverage = None
    if road_path.exists():
        road_coverage = (json.loads(road_path.read_text()) or {}).get("citywide")
```

Pass `road_coverage=road_coverage` to `build_findings_core(...)`.

- [ ] **Step 8: Docs**

`SCHEMA.md`: add a `## road_network.json — tier real` section documenting the exact shape from the Interfaces block (including nullability and the class/status filter), and extend the `ward_safety_index.json` section's record shape + prose with the three new nullable fields. `DECISIONS.md`: add the next numbered decision recording the denominator choice (dataset `pr57-gg9e` over broken `6imu-meau`; classes 2/3/4 + status N ≈ 3,945 mi ≈ the city's ~4,000 street miles; expressways/ramps/alleys/rivers excluded; trails excluded from numerators).

- [ ] **Step 9: Verify end-to-end on fixtures**

```bash
cd pipeline && python run_all.py --fixtures
python - <<'EOF'
import json
rn = json.load(open("../site/data/road_network.json"))
cw = rn["citywide"]
assert cw and 0 < cw["pct_with_bike_infra"] < 100, cw
assert cw["road_miles"] > 0 and len(rn["wards"]) > 0
wsi = json.load(open("../site/data/ward_safety_index.json"))
rec = wsi["wards"][0]
for k in ("bikeway_pct_protected", "road_miles", "bikeway_pct_of_roads"):
    assert k in rec, k
some = [r for r in wsi["wards"] if r["bikeway_pct_of_roads"] is not None]
assert some, "no ward got coverage"
fids = [f["id"] for f in json.load(open("../site/data/findings.json"))]
assert "street-coverage" in fids, fids
i_ps, i_sc = fids.index("protected-share"), fids.index("street-coverage")
assert i_sc == i_ps + 1, fids
meta = json.load(open("../site/data/meta.json"))
assert meta["contract_version"] == "1.9"
assert any(s["id"] == "street_centerlines" for s in meta["sources"])
print("fixture aggregate OK; citywide coverage:", cw["pct_with_bike_infra"], "%")
EOF
```

Expected: `fixture aggregate OK; ...`. **Then restore the committed data and clear the marker:**

```bash
cd .. && git restore site/data && rm -f pipeline/raw/PROVENANCE
git status --porcelain site/data   # must print nothing
```

- [ ] **Step 10: Commit**

```bash
git add pipeline/config.py pipeline/aggregate.py pipeline/crash_metrics.py pipeline/refresh_reporting.py SCHEMA.md DECISIONS.md
git commit -m "feat: road-network coverage metrics (per-ward + citywide) and street-coverage finding"
```

---

### Task 3: `refresh_coverage.py` + publish real numbers

**Files:**
- Create: `pipeline/refresh_coverage.py`
- Modify (data): `site/data/road_network.json` (new), `site/data/ward_safety_index.json`, `site/data/findings.json`, `site/data/meta.json` (via the two refresh scripts — no hand-editing)

**Interfaces:**
- Consumes (Task 2): `aggregate.load_street_centerlines`, `aggregate.build_road_network`, `aggregate.ward_bikeway_miles_by_category`, `aggregate.ward_coverage_fields`, `refresh_reporting.guard_provenance`, `config.CONTRACT_VERSION`.
- Produces: real (socrata-provenance) committed coverage data.

- [ ] **Step 1: Create `pipeline/refresh_coverage.py`**

```python
"""One-shot live refresh of the road-coverage metrics from committed site data.

Pulls ONLY the street centerline layer (pull_street_centerlines.py) and joins
it against the already-committed bike_routes.geojson / wards.geojson, so the
coverage numbers (road_network.json, the per-ward coverage fields in
ward_safety_index.json, meta.json's street_centerlines source) can publish
without a multi-hour full pipeline run. All numbers come from the exact same
aggregate.py functions as the live path — no logic drift. The weekly
`python run_all.py` recomputes everything from scratch and remains canonical.

Run refresh_reporting.py AFTER this script — it rebuilds findings.json from
the road_network.json written here.

Provenance guard: same as refresh_reporting — refuses to touch fixture data.

Usage: python refresh_coverage.py [--skip-pull]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

from aggregate import (build_road_network, load_street_centerlines,
                       ward_bikeway_miles_by_category, ward_coverage_fields)
from config import RAW_DIR, SITE_DATA_DIR, CONTRACT_VERSION, OUTPUT_CRS
from refresh_reporting import guard_provenance
from socrata import write_json

HERE = Path(__file__).resolve().parent


def _load(name):
    return json.loads((SITE_DATA_DIR / name).read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skip-pull", action="store_true",
                    help="reuse an existing raw/street_centerlines.geojson")
    args = ap.parse_args()

    guard_provenance(_load("meta.json"))

    if not (args.skip_pull and (RAW_DIR / "street_centerlines.geojson").exists()):
        subprocess.run([sys.executable, str(HERE / "pull_street_centerlines.py")],
                       cwd=HERE, check=True)

    streets_gdf = load_street_centerlines()
    if streets_gdf is None:
        raise SystemExit("refresh_coverage: no usable street centerlines")

    routes_gj = _load("bike_routes.geojson")
    wards_gj = _load("wards.geojson")
    wards_gdf = gpd.GeoDataFrame.from_features(wards_gj["features"], crs=OUTPUT_CRS)
    wards_gdf["ward"] = wards_gdf["ward"].astype(str)
    wards_gdf = wards_gdf[["ward", "geometry"]]

    as_of = datetime.now(timezone.utc).date().isoformat()
    road_network = build_road_network(streets_gdf, wards_gdf, routes_gj, as_of)
    write_json(SITE_DATA_DIR / "road_network.json", road_network)

    road_miles = {r["ward"]: r["road_miles"] for r in road_network["wards"]}
    cats_by_ward = ward_bikeway_miles_by_category(routes_gj, wards_gdf)

    wsi = _load("ward_safety_index.json")
    for rec in wsi["wards"]:
        rec.update(ward_coverage_fields(cats_by_ward.get(rec["ward"], {}),
                                        road_miles.get(rec["ward"])))
    write_json(SITE_DATA_DIR / "ward_safety_index.json", wsi)

    meta = _load("meta.json")
    meta["contract_version"] = CONTRACT_VERSION
    entry = {"id": "street_centerlines",
             "name": "Street Center Lines (surface-street grid)",
             "tier": "real", "records": int(len(streets_gdf)), "date_range": None}
    ids = [s.get("id") for s in meta["sources"]]
    if "street_centerlines" in ids:
        meta["sources"][ids.index("street_centerlines")] = entry
    else:  # same position as aggregate.py's list: right after bike_routes
        pos = ids.index("bike_routes") + 1 if "bike_routes" in ids else len(ids)
        meta["sources"].insert(pos, entry)
    write_json(SITE_DATA_DIR / "meta.json", meta)

    cw = road_network["citywide"]
    print(f"refresh_coverage: {cw['road_miles']} road mi, "
          f"{cw['onstreet_bikeway_miles']} on-street bikeway mi -> "
          f"{cw['pct_with_bike_infra']}% coverage across {len(road_miles)} wards")
    print("  now run: python refresh_reporting.py  (rebuilds findings.json)")


if __name__ == "__main__":
    main()
```

Note: the ward-safety-index note text about the new fields (written by `build_ward_safety_index`) will only appear after the next full live run; this script deliberately merges fields without rewriting the committed note. Do not "fix" that — the note update rides the weekly run.

- [ ] **Step 2: Run it live (network required, ~56k rows, a few minutes)**

```bash
cd pipeline && python refresh_coverage.py && python refresh_reporting.py && python check_provenance.py
```

Expected: `refresh_coverage: ~39xx.x road mi, ~44x.x on-street bikeway mi -> ~11.x% coverage across 50 wards`; refresh_reporting prints findings ids including `street-coverage`; check_provenance passes.

- [ ] **Step 3: Sanity-check the published numbers**

```bash
python - <<'EOF'
import json
rn = json.load(open("../site/data/road_network.json"))
cw = rn["citywide"]
assert 3500 < cw["road_miles"] < 4500, cw          # ~3,945 expected
assert 300 < cw["onstreet_bikeway_miles"] < 600, cw
assert 5 < cw["pct_with_bike_infra"] < 20, cw      # ~11% expected
assert len(rn["wards"]) == 50
assert all(r["road_miles"] > 0 for r in rn["wards"])
wsi = json.load(open("../site/data/ward_safety_index.json"))
vals = [r["bikeway_pct_of_roads"] for r in wsi["wards"]]
assert all(v is None or 0 <= v <= 100 for v in vals)
assert sum(v is not None for v in vals) >= 45, "most wards should have coverage"
prot = [r["bikeway_pct_protected"] for r in wsi["wards"]]
assert all(v is None or 0 <= v <= 100 for v in prot)
fids = [f["id"] for f in json.load(open("../site/data/findings.json"))]
assert "street-coverage" in fids
print("live coverage data OK:", cw)
EOF
```

- [ ] **Step 4: Commit code + data**

```bash
cd .. && git add pipeline/refresh_coverage.py site/data/road_network.json site/data/ward_safety_index.json site/data/findings.json site/data/meta.json
git commit -m "feat: refresh_coverage script; publish real road-coverage data (~11% citywide)"
```

---

### Task 4: Ward-rankings table columns + sources entry + UI tests

**Files:**
- Modify: `site/assets/js/table.js`
- Modify: `site/assets/js/sources.js`
- Test: `tests/ui/table-datasets.test.js`

**Interfaces:**
- Consumes (Task 2 schema): ward records with nullable `bikeway_pct_protected`, `road_miles`, `bikeway_pct_of_roads`; meta source id `street_centerlines`.

- [ ] **Step 1: Extend the failing test first**

In `tests/ui/table-datasets.test.js`, add the three new fields to the two existing sample ward objects — first ward: `bikeway_pct_protected: 24.6, road_miles: 71.3, bikeway_pct_of_roads: 11.5`; second (nulls-edge) ward: `bikeway_pct_protected: null, road_miles: null, bikeway_pct_of_roads: null` — and add assertions after the existing `buildSafetyIndexRows` ones:

```js
assert.strictEqual(siRows[0].bikeway_pct_protected, 24.6, "coverage: pct protected passes through");
assert.strictEqual(siRows[0].road_miles, 71.3, "coverage: road miles passes through");
assert.strictEqual(siRows[0].bikeway_pct_of_roads, 11.5, "coverage: pct of roads passes through");
assert.strictEqual(siRows[1].bikeway_pct_protected, null, "coverage: null preserved (not 0)");
assert.strictEqual(siRows[1].bikeway_pct_of_roads, null, "coverage: null preserved (not 0)");
```

- [ ] **Step 2: Run to verify it fails**

Run: `node tests/ui/table-datasets.test.js` — expected: AssertionError (fields come back `undefined`).

- [ ] **Step 3: Implement**

In `site/assets/js/table.js`:

1. `buildSafetyIndexRows` — add to the returned object (preserving null vs undefined the same way the trend fields do):

```js
      bikeway_pct_protected: w.bikeway_pct_protected != null ? w.bikeway_pct_protected : null,
      road_miles: w.road_miles != null ? w.road_miles : null,
      bikeway_pct_of_roads: w.bikeway_pct_of_roads != null ? w.bikeway_pct_of_roads : null,
```

2. In `renderSafetyIndexSection`'s `COLS`, insert after the `bikeway_miles` column:

```js
        { key: "bikeway_pct_protected", label: "% protected",
          title: "Share of the ward's on-street bikeway miles that are physically protected lanes" },
        { key: "bikeway_pct_of_roads", label: "% streets w/ bikeways",
          title: "Share of the ward's surface-street miles with any bike infrastructure (off-street trails excluded)" },
```

3. In the row renderer, insert matching cells after the `bikeway_miles` cell (nulls render as an em dash, numbers get a `%` suffix):

```js
            row.bikeway_pct_protected == null ? "—" : row.bikeway_pct_protected + "%",
            row.bikeway_pct_of_roads == null ? "—" : row.bikeway_pct_of_roads + "%",
```

(These are plain values in the `plainCells` array — numeric sorting still works because sorting reads the raw row fields, and `compareNullsLast` already handles nulls.)

4. CSV export `cols`: add `"bikeway_pct_protected", "road_miles", "bikeway_pct_of_roads"` after `"bikeway_miles"`.

5. The "About this score" explainer `<details>`: append one sentence — `% protected is the protected share of the ward's on-street bikeway miles; % streets w/ bikeways is the share of the ward's surface-street miles with any bike infrastructure.`

In `site/assets/js/sources.js`: add a detail entry with `id: "street_centerlines"` right after the `bike_routes` entry, matching the existing entries' shape exactly (read a neighboring entry for the field names), describing: Chicago Data Portal Street Center Lines (`pr57-gg9e`), tier real, used as the surface-street denominator for coverage metrics (classes 2/3/4, status N; expressways/ramps/alleys/rivers excluded), layer last updated June 2021.

- [ ] **Step 4: Run all UI tests**

```bash
for f in tests/ui/*.test.js; do node "$f" || echo "FAIL $f"; done
```

Expected: no FAIL lines.

- [ ] **Step 5: Commit**

```bash
git add site/assets/js/table.js site/assets/js/sources.js tests/ui/table-datasets.test.js
git commit -m "feat: coverage columns in ward rankings table + street-centerlines source entry"
```

---

## Final verification (controller)

- All UI test files pass; `python check_provenance.py` passes.
- Browser check: table.html safety-index tab shows the two new columns with real values; findings.html shows the `street-coverage` card; sources.html shows the street-centerlines card.
- Final whole-branch code review, then PR to `main`.
