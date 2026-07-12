# OSM Off-Street Trails Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add major off-street trails (Lakefront Trail, 312 RiverRun, North Shore Channel Trail, North Branch Trail, and peers) to the map and network as a standalone crowdsourced-tier layer sourced from OpenStreetMap via the Overpass API.

**Architecture:** Mirror the existing Mellow layer end-to-end — a non-fatal `pull_osm_trails.py` archives raw Overpass JSON, `build_osm_trails()` in `aggregate.py` shapes it into one grouped-by-name GeoJSON feature per trail (tier `crowdsourced`, `facility_category: "trail"`), and the two map screens render it as a default-on, toggleable overlay. No trail data enters the `real`-tier CDOT layer or any derived stat.

**Tech Stack:** Python 3.12 (geopandas, shapely, requests), vanilla JS + Leaflet front-end, pytest + node `assert` tests.

## Global Constraints

- Every data layer in the UI carries a real/proxy/mock/crowdsourced/stub tier badge at all times (hard product constraint). The new layer's tier is **`crowdsourced`**.
- Do not add/rename any `site/data/*` output key without bumping `CONTRACT_VERSION` in `config.py` AND updating `SCHEMA.md`. This plan adds a NEW file (`osm_trails.geojson`), so `CONTRACT_VERSION` must be bumped in Task 4.
- Pipeline pull modules follow the split: **the pull module fetches and archives raw untouched; `aggregate.py` does all shaping.**
- Third-party (non-Socrata) pulls are **non-fatal**: on failure warn to stderr, leave the raw file absent, and let `aggregate.py` ship a stub.
- Overpass bounding box (verbatim): `(41.60, -87.95, 42.20, -87.50)` = (south, west, north, east).
- Python tests run with `pytest pipeline/tests`; JS model tests run with `node tests/ui/<file>.test.js` (standalone scripts, no runner).

---

### Task 1: Overpass config constants

**Files:**
- Modify: `pipeline/config.py` (add near `MELLOW_API_URL`, line 27)
- Test: `pipeline/tests/test_config.py`

**Interfaces:**
- Produces: `OVERPASS_API_URL: str`, `OSM_TRAILS_BBOX: tuple[float,float,float,float]`, `OSM_TRAILS_QUERY: str` in `config.py`.

- [ ] **Step 1: Write the failing test**

Add to `pipeline/tests/test_config.py`:

```python
def test_osm_trails_query_config_present_and_filtered():
    import config
    assert config.OVERPASS_API_URL.startswith("https://")
    # bbox is (south, west, north, east) covering Chicago + North Branch Trail north extent
    assert config.OSM_TRAILS_BBOX == (41.60, -87.95, 42.20, -87.50)
    q = config.OSM_TRAILS_QUERY
    # de-dup: road-parallel cycle tracks (is_sidepath=yes) are excluded at query time
    assert '"is_sidepath"!="yes"' in q
    # only named off-street ways
    assert '"name"' in q
    assert '"highway"="cycleway"' in q
    # bbox coordinates are interpolated into the query
    assert "41.6" in q and "-87.95" in q
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/test_config.py::test_osm_trails_query_config_present_and_filtered -v`
Expected: FAIL with `AttributeError: module 'config' has no attribute 'OVERPASS_API_URL'`

- [ ] **Step 3: Add the constants**

In `pipeline/config.py`, immediately after the `MELLOW_API_URL = ...` line (line 27):

```python
# OpenStreetMap Overpass API — source for named off-street trails (Lakefront,
# 312 RiverRun, North Shore Channel, North Branch, etc.) that CDOT's on-street
# Bike Routes layer structurally omits. Crowdsourced tier. Non-fatal like Mellow.
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
# (south, west, north, east) — Chicago plus the North Branch Trail's reach north
# into the forest preserves. Trails are shown full-length, not clipped at the city line.
OSM_TRAILS_BBOX = (41.60, -87.95, 42.20, -87.50)
# Named off-street ways only. is_sidepath!=yes drops road-parallel cycle tracks
# that duplicate CDOT on-street segments (see design doc). out geom returns inline
# per-way coordinate arrays so no second node-resolution pass is needed.
_OSM_BBOX_STR = ",".join(str(c) for c in OSM_TRAILS_BBOX)
OSM_TRAILS_QUERY = f"""[out:json][timeout:90];
(
  way["highway"="cycleway"]["name"]["is_sidepath"!="yes"]({_OSM_BBOX_STR});
  way["highway"="path"]["bicycle"="designated"]["name"]["is_sidepath"!="yes"]({_OSM_BBOX_STR});
  way["highway"="footway"]["bicycle"="designated"]["name"]["is_sidepath"!="yes"]({_OSM_BBOX_STR});
);
out geom;
"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest pipeline/tests/test_config.py::test_osm_trails_query_config_present_and_filtered -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/config.py pipeline/tests/test_config.py
git commit -m "feat: Overpass API config for OSM off-street trails"
```

---

### Task 2: build_osm_trails() shaper in aggregate.py

**Files:**
- Modify: `pipeline/aggregate.py` (new function near `build_mellow`, ~line 344; add imports at line 16)
- Test: `pipeline/tests/test_aggregate_osm_trails.py` (create)

**Interfaces:**
- Consumes: raw Overpass JSON dict `{"elements": [{"type":"way","tags":{"name":...},"geometry":[{"lat":..,"lon":..},...]}, ...]}`.
- Produces: `build_osm_trails(raw: dict) -> dict` — a GeoJSON `FeatureCollection`. One feature per distinct trail `name`, geometry `LineString` (single way) or `MultiLineString` (multiple ways sharing a name). Properties: `segment_id` (`osm-trail-<slug>`), `name`, `facility_category: "trail"`, `length_m: float`, `data_tier: "crowdsourced"`.

- [ ] **Step 1: Write the failing test**

Create `pipeline/tests/test_aggregate_osm_trails.py`:

```python
import aggregate


def _way(name, coords):
    # coords: list of (lat, lon)
    return {"type": "way", "id": abs(hash(name + str(coords))) % 10_000,
            "tags": {"name": name, "highway": "cycleway"},
            "geometry": [{"lat": la, "lon": lo} for la, lo in coords]}


def test_build_osm_trails_groups_by_name_and_tags_crowdsourced():
    raw = {"elements": [
        _way("Lakefront Trail", [(41.75, -87.56), (41.85, -87.61)]),
        _way("Lakefront Trail", [(41.85, -87.61), (41.98, -87.655)]),  # second way, same trail
        _way("North Branch Trail", [(41.98, -87.70), (42.10, -87.78)]),
    ]}
    out = aggregate.build_osm_trails(raw)

    assert out["type"] == "FeatureCollection"
    # two ways sharing "Lakefront Trail" collapse into ONE feature
    names = sorted(f["properties"]["name"] for f in out["features"])
    assert names == ["Lakefront Trail", "North Branch Trail"]

    by_name = {f["properties"]["name"]: f for f in out["features"]}
    lake = by_name["Lakefront Trail"]
    assert lake["geometry"]["type"] == "MultiLineString"       # 2 ways -> multi
    assert lake["properties"]["segment_id"] == "osm-trail-lakefront-trail"
    assert lake["properties"]["facility_category"] == "trail"
    assert lake["properties"]["data_tier"] == "crowdsourced"
    assert lake["properties"]["length_m"] > 0

    nb = by_name["North Branch Trail"]
    assert nb["geometry"]["type"] == "LineString"              # 1 way -> single


def test_build_osm_trails_skips_unnamed_and_non_ways():
    raw = {"elements": [
        {"type": "node", "id": 1, "lat": 41.8, "lon": -87.6},          # not a way
        {"type": "way", "id": 2, "tags": {}, "geometry": [{"lat": 41.8, "lon": -87.6}]},  # no name
    ]}
    out = aggregate.build_osm_trails(raw)
    assert out["features"] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/test_aggregate_osm_trails.py -v`
Expected: FAIL with `AttributeError: module 'aggregate' has no attribute 'build_osm_trails'`

- [ ] **Step 3: Implement build_osm_trails**

In `pipeline/aggregate.py`, change the shapely import (line 16) to add LineString/MultiLineString:

```python
from shapely.geometry import Point, shape, LineString, MultiLineString
```

Add this function immediately after `build_mellow` (after line 344):

```python
def _slug(name):
    """Lowercase, non-alphanumeric runs -> single hyphen; trimmed. For segment ids."""
    out = []
    prev_dash = False
    for ch in name.strip().lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-")


def build_osm_trails(raw):
    """Group Overpass named off-street ways into one feature per trail name.

    Overpass `out geom` returns way elements with an inline `geometry` list of
    {lat, lon} points and a `tags.name`. Ways sharing a name (a trail is chopped
    into many OSM ways) collapse into a single MultiLineString feature — one
    Leaflet layer per trail, not per fragment (same rationale as build_mellow).
    Tier is crowdsourced; facility_category reuses the pre-wired "trail" styling.
    """
    by_name = defaultdict(list)  # name -> list[list[(lon, lat)]]
    for el in raw.get("elements", []):
        if el.get("type") != "way":
            continue
        name = (el.get("tags") or {}).get("name")
        geom = el.get("geometry") or []
        if not name or len(geom) < 2:
            continue
        by_name[name].append([(pt["lon"], pt["lat"]) for pt in geom])

    if not by_name:
        return {"type": "FeatureCollection", "features": []}

    names = sorted(by_name)
    shapes = []
    for name in names:
        parts = by_name[name]  # each part has >=2 coords (filtered above)
        shapes.append(LineString(parts[0]) if len(parts) == 1 else MultiLineString(parts))
    lengths = gpd.GeoDataFrame(geometry=shapes, crs=OUTPUT_CRS).to_crs(METRIC_CRS).geometry.length

    feats = []
    for name, geom, length in zip(names, shapes, lengths):
        feats.append({
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "segment_id": f"osm-trail-{_slug(name)}",
                "name": name,
                "facility_category": "trail",
                "length_m": round(float(length), 1),
                "data_tier": "crowdsourced",
            },
        })
    return {"type": "FeatureCollection", "features": feats}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest pipeline/tests/test_aggregate_osm_trails.py -v`
Expected: PASS (both tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/aggregate.py pipeline/tests/test_aggregate_osm_trails.py
git commit -m "feat: build_osm_trails groups OSM ways into per-trail features"
```

---

### Task 3: pull_osm_trails.py fetcher

**Files:**
- Create: `pipeline/pull_osm_trails.py`
- Test: `pipeline/tests/test_pull_osm_trails.py` (create)

**Interfaces:**
- Consumes: `config.OVERPASS_API_URL`, `config.OSM_TRAILS_QUERY`, `config.RAW_DIR`, `socrata.write_json`.
- Produces: on success writes `pipeline/raw/osm_trails.json` (raw Overpass response). On failure writes nothing and returns without raising. Module exposes `main()`.

- [ ] **Step 1: Write the failing test**

Create `pipeline/tests/test_pull_osm_trails.py`:

```python
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
    monkeypatch.setattr(pull_osm_trails, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_osm_trails.requests, "post",
                        lambda *a, **k: _Resp(payload))
    pull_osm_trails.main()
    written = json.loads((tmp_path / "osm_trails.json").read_text())
    assert written["elements"][0]["tags"]["name"] == "Lakefront Trail"


def test_pull_is_non_fatal_on_failure(tmp_path, monkeypatch, capsys):
    def _boom(*a, **k):
        raise pull_osm_trails.requests.RequestException("network down")
    monkeypatch.setattr(pull_osm_trails, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pull_osm_trails.requests, "post", _boom)
    pull_osm_trails.main()  # must NOT raise
    assert not (tmp_path / "osm_trails.json").exists()
    assert "WARNING" in capsys.readouterr().err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/test_pull_osm_trails.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pull_osm_trails'`

- [ ] **Step 3: Create the puller**

Create `pipeline/pull_osm_trails.py`:

```python
"""Pull named off-street trails from the OpenStreetMap Overpass API.

CDOT's Bike Routes layer is on-street only, so the Lakefront Trail, 312 RiverRun,
North Shore Channel Trail, North Branch Trail (and peers) never appear. This
fetches named off-street ways from OSM and archives the raw Overpass response to
pipeline/raw/osm_trails.json untouched; build_osm_trails() in aggregate.py groups
them by name, assigns ids/lengths, and tags the crowdsourced tier — same
pull-archives / aggregate-shapes split as pull_mellow.py.

Like pull_mellow.py this is a single third-party service with no uptime SLA, so a
failure here is non-fatal: it warns and leaves raw/osm_trails.json absent, and
aggregate.py falls back to the stub layer rather than failing the whole run.
"""
import argparse
import sys

import requests

from config import OVERPASS_API_URL, OSM_TRAILS_QUERY, RAW_DIR
from socrata import write_json


def main():
    parser = argparse.ArgumentParser(
        description="Pull named off-street trails from the OSM Overpass API.")
    parser.parse_args()

    try:
        resp = requests.post(OVERPASS_API_URL, data={"data": OSM_TRAILS_QUERY}, timeout=120)
        resp.raise_for_status()
        payload = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"WARNING: OSM trails pull failed ({exc}) — osm_trails.geojson will "
              f"ship as a stub this run. See CONTRIBUTING.md.", file=sys.stderr)
        return

    output_path = RAW_DIR / "osm_trails.json"
    write_json(output_path, payload)
    print(f"Element count: {len(payload.get('elements', []))}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest pipeline/tests/test_pull_osm_trails.py -v`
Expected: PASS (both tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/pull_osm_trails.py pipeline/tests/test_pull_osm_trails.py
git commit -m "feat: pull_osm_trails fetches named OSM off-street trails (non-fatal)"
```

---

### Task 4: Wire osm_trails into aggregate main() + meta.json

**Files:**
- Modify: `pipeline/aggregate.py` (`main()` — mellow block ~line 875, meta `sources` ~line 901, write block ~line 938)
- Modify: `pipeline/config.py` (`CONTRACT_VERSION` bump)

**Interfaces:**
- Consumes: `build_osm_trails` (Task 2), `stub_layer` (existing).
- Produces: `site/data/osm_trails.geojson` written every run; a `meta.json` `sources` entry `{id: "osm_trails", name: "OpenStreetMap Off-street Trails", tier: "crowdsourced", records: N}` present only when the layer has features.

- [ ] **Step 1: Add the build + stub-fallback block**

In `pipeline/aggregate.py` `main()`, immediately after the mellow block (after line 882, the closing of the `mellow_gj = ... else: stub_layer(...)`), add:

```python
    osm_trails_raw_path = RAW_DIR / "osm_trails.json"
    if osm_trails_raw_path.exists():
        osm_trails_gj = build_osm_trails(json.loads(osm_trails_raw_path.read_text()))
    else:
        osm_trails_gj = stub_layer(
            "OpenStreetMap off-street trails (Lakefront, 312 RiverRun, North Shore "
            "Channel, North Branch, etc.) were not pulled this run (pull_osm_trails.py "
            "didn't run, or Overpass was unreachable). See CONTRIBUTING.md.")
```

- [ ] **Step 2: Add the meta.json source entry**

In the `meta` dict's `sources` list, mirror the conditional Mellow entry. Immediately after the Mellow conditional block (the `] + ([{"id": "mellow_routes", ...}] if mellow_gj["features"] else []) + [` construct, lines 901-903), insert a second conditional splice. Change:

```python
        ] + ([{"id": "mellow_routes", "name": "Mellow Bike Map (crowdsourced low-stress streets)",
               "tier": "crowdsourced", "records": len(mellow_gj["features"]), "date_range": None}]
             if mellow_gj["features"] else []) + [
```

to:

```python
        ] + ([{"id": "mellow_routes", "name": "Mellow Bike Map (crowdsourced low-stress streets)",
               "tier": "crowdsourced", "records": len(mellow_gj["features"]), "date_range": None}]
             if mellow_gj["features"] else []) + (
            [{"id": "osm_trails", "name": "OpenStreetMap Off-street Trails",
              "tier": "crowdsourced", "records": len(osm_trails_gj["features"]), "date_range": None}]
             if osm_trails_gj["features"] else []) + [
```

- [ ] **Step 3: Write the output file**

In the write block, immediately after the `write_json(SITE_DATA_DIR / "mellow_routes.geojson", mellow_gj)` line (line 938), add:

```python
    write_json(SITE_DATA_DIR / "osm_trails.geojson", osm_trails_gj)
```

- [ ] **Step 4: Bump the contract version**

A new published `site/data/*` file is a contract change. In `pipeline/config.py`, find `CONTRACT_VERSION` and increment it (e.g. `"1.4.0"` → `"1.5.0"`; match the existing format).

Run: `grep -n "CONTRACT_VERSION" pipeline/config.py` to see the current value before editing.

- [ ] **Step 5: Verify end-to-end with fixtures**

Trails come from fixtures in Task 6; for now verify the stub path works (no raw file present):

```bash
rm -f pipeline/raw/osm_trails.json
cd pipeline && python -c "import json, aggregate; \
  gj = aggregate.stub_layer('x'); print('stub ok', gj['properties']['status'])"
```
Expected: `stub ok no_data_yet`

Then confirm `main()` wiring imports cleanly:
```bash
cd pipeline && python -c "import aggregate; print('import ok')"
```
Expected: `import ok`

- [ ] **Step 6: Commit**

```bash
git add pipeline/aggregate.py pipeline/config.py
git commit -m "feat: write osm_trails.geojson + meta source entry; bump contract version"
```

---

### Task 5: Add pull_osm_trails to run_all.py

**Files:**
- Modify: `pipeline/run_all.py` (`LIVE_STAGES`, line ~43; docstring line ~10)
- Test: `pipeline/tests/test_run_all_order.py`

**Interfaces:**
- Consumes: `run_all.LIVE_STAGES`.
- Produces: `"pull_osm_trails.py"` present in `LIVE_STAGES`.

- [ ] **Step 1: Write the failing test**

Add to `pipeline/tests/test_run_all_order.py`:

```python
def test_osm_trails_pull_is_a_live_stage():
    # Off-street trails come from OSM, pulled alongside the other non-fatal
    # third-party layer (Mellow), before the COMMON aggregate stage.
    live = _flat(run_all.LIVE_STAGES)
    assert "pull_osm_trails.py" in live
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/test_run_all_order.py::test_osm_trails_pull_is_a_live_stage -v`
Expected: FAIL with `assert 'pull_osm_trails.py' in [...]`

- [ ] **Step 3: Add the stage**

In `pipeline/run_all.py`, change the Mellow stage line (line 43) from:

```python
    ["pull_mellow.py"],
```

to:

```python
    ["pull_mellow.py"], ["pull_osm_trails.py"],
```

Also update the docstring bullet (line 10) from `pull_cameras, pull_mellow` to `pull_cameras, pull_mellow, pull_osm_trails`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest pipeline/tests/test_run_all_order.py -v`
Expected: PASS (all tests in file)

- [ ] **Step 5: Commit**

```bash
git add pipeline/run_all.py pipeline/tests/test_run_all_order.py
git commit -m "feat: run pull_osm_trails.py as a live pipeline stage"
```

---

### Task 6: Fixtures — add osm_trails, drop fake trail from bike_routes

**Files:**
- Modify: `pipeline/make_fixtures.py` (`CORRIDORS` line 27; new fixture fn; `main()`)
- Test: `pipeline/tests/test_fixtures_osm_trails.py` (create)

**Interfaces:**
- Consumes: `config.RAW_DIR`, `socrata.write_json`, `aggregate.build_osm_trails`.
- Produces: `make_fixtures.build_osm_trails_raw() -> dict` (Overpass-shaped); `main()` writes `pipeline/raw/osm_trails.json`. The bike_routes fixture no longer contains any `OFF-STREET TRAIL` corridor.

- [ ] **Step 1: Write the failing test**

Create `pipeline/tests/test_fixtures_osm_trails.py`:

```python
import make_fixtures
import aggregate


def test_bike_routes_fixture_has_no_offstreet_trail():
    # CDOT's real layer is on-street only; the fixture must match that shape so
    # trails don't appear in two layers. Off-street trails live in osm_trails now.
    labels = {c[2] for c in make_fixtures.CORRIDORS}
    assert "OFF-STREET TRAIL" not in labels


def test_osm_trails_fixture_shapes_into_trail_features():
    raw = make_fixtures.build_osm_trails_raw()
    out = aggregate.build_osm_trails(raw)
    names = {f["properties"]["name"] for f in out["features"]}
    assert "Lakefront Trail" in names
    assert all(f["properties"]["data_tier"] == "crowdsourced" for f in out["features"])
    assert all(f["properties"]["facility_category"] == "trail" for f in out["features"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/test_fixtures_osm_trails.py -v`
Expected: FAIL — first test fails (`OFF-STREET TRAIL` still present), and `build_osm_trails_raw` doesn't exist.

- [ ] **Step 3: Remove the fake trail corridor**

In `pipeline/make_fixtures.py`, delete the `LAKEFRONT TRAIL` entry from `CORRIDORS` (line 27):

```python
    ("LAKEFRONT TRAIL", [(41.750, -87.560), (41.850, -87.610), (41.980, -87.655)], "OFF-STREET TRAIL"),
```

- [ ] **Step 4: Add the osm_trails fixture builder**

In `pipeline/make_fixtures.py`, add this function (near the other `build_*` functions):

```python
# Two named off-street trails in the Overpass `out geom` shape (way elements with
# inline {lat, lon} geometry + tags.name). Lakefront moved here from CORRIDORS so
# the bike_routes fixture matches the real on-street-only CDOT layer.
def build_osm_trails_raw():
    def way(name, pts):
        return {"type": "way", "id": abs(hash(name)) % 100000,
                "tags": {"name": name, "highway": "cycleway"},
                "geometry": [{"lat": la, "lon": lo} for la, lo in pts]}
    return {"elements": [
        way("Lakefront Trail", [(41.750, -87.560), (41.850, -87.610), (41.980, -87.655)]),
        way("North Branch Trail", [(41.980, -87.700), (42.060, -87.760), (42.150, -87.785)]),
    ]}
```

- [ ] **Step 5: Write the fixture in main()**

In `make_fixtures.py` `main()`, next to the other `write_json(RAW_DIR / ..., ...)` calls (near line 373), add:

```python
    write_json(RAW_DIR / "osm_trails.json", build_osm_trails_raw())
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest pipeline/tests/test_fixtures_osm_trails.py -v`
Expected: PASS (both tests)

- [ ] **Step 7: Regenerate fixtures and full aggregate, verify the site file**

```bash
cd pipeline && python make_fixtures.py && python run_all.py --fixtures
```
Then verify trails landed in the site output:
```bash
cd pipeline && python -c "import json; \
  d = json.load(open('../site/data/osm_trails.geojson')); \
  print('features', len(d['features'])); \
  print('names', [f['properties']['name'] for f in d['features']]); \
  print('tier', {f['properties']['data_tier'] for f in d['features']})"
```
Expected: `features 2`, names include `Lakefront Trail` and `North Branch Trail`, tier `{'crowdsourced'}`.

> **Note:** `run_all.py --fixtures` writes a `fixtures` PROVENANCE marker. Per the standing project memory, clear it before any later live build: `rm -f pipeline/raw/PROVENANCE`. Do NOT commit `site/data/*` changes produced by a fixtures run — commit only the code below.

- [ ] **Step 8: Commit**

```bash
git add pipeline/make_fixtures.py pipeline/tests/test_fixtures_osm_trails.py
git commit -m "feat: osm_trails fixture; drop fake off-street trail from bike_routes fixture"
```

---

### Task 7: Render trails on the geographic map (map.js)

**Files:**
- Modify: `site/assets/js/map.js` (`LAYERS` line 57; default `state.layers` line 47; `Promise.all` load lines 70-82; `buildLayers` line 151; new `showTrail`; toggle stub note line 338)

**Interfaces:**
- Consumes: `site/data/osm_trails.geojson`, `B.FACILITY_COLORS.trail`, `B.FACILITY_LABELS.trail`, `B.badgeHTML`.
- Produces: a `trails` entry in `LAYERS`/`groups`, on by default, click → `showTrail`.

- [ ] **Step 1: Add trails to the default layers and LAYERS list**

Line 47 — add `trails` to the default set:

```javascript
    layers: new Set((B.qs().get("layers") || "crashes,infrastructure,trails").split(",").filter(Boolean)),
```

Lines 57-64 — add a `trails` entry to `LAYERS` (after `infrastructure`):

```javascript
  const LAYERS = [
    { id: "crashes", label: "Cyclist crashes", tier: "real" },
    { id: "obstructions", label: "Obstructions", tier: "mock" },
    { id: "infrastructure", label: "Bike infrastructure", tier: "real" },
    { id: "trails", label: "Off-street trails", tier: "crowdsourced" },
    { id: "planned", label: "Planned routes", tier: "stub" },
    { id: "cameras", label: "Camera violations", tier: "proxy" },
    { id: "wards", label: "Ward boundaries", tier: "real" },
  ];
```

- [ ] **Step 2: Load the file**

In the `Promise.all` (lines 70-82), add a load (after the `planned` load) and its destructured name. Add after line 74 (`B.loadJSON("data/planned_routes.geojson"),`):

```javascript
    B.loadJSON("data/osm_trails.geojson").catch(() => ({ features: [] })),
```

Update the destructuring on line 82 to include `trails` in the same position (after `planned`):

```javascript
  ]).then(([crashes, obstructions, routes, planned, trails, cameras, wards, corridors, intersections, aldermen, safety, menu]) => {
    Object.assign(data, { crashes, obstructions, routes, planned, trails, cameras, wards, corridors, intersections });
```

> IMPORTANT: the new `osm_trails.geojson` load must be inserted at the SAME index in both the `Promise.all` array and the destructuring list, immediately after `planned`, or every later variable shifts by one.

- [ ] **Step 3: Build the trails group**

In `buildLayers()` (after the `infrastructure` group, line 171), add:

```javascript
    groups.trails = L.layerGroup((data.trails.features || []).map(f =>
      L.geoJSON(f, {
        style: { color: B.FACILITY_COLORS.trail, weight: 3.5, opacity: 0.9 },
      }).on("click", () => showTrail(f.properties))));
```

- [ ] **Step 4: Add the showTrail detail view**

Add near `showSegment` (after line 510):

```javascript
  function showTrail(p) {
    setDetail(`
      <h3>${B.esc(p.name || "Off-street trail")} ${B.badgeHTML("crowdsourced")}</h3>
      <div class="notice">${B.esc(B.TIER_INFO.crowdsourced)}</div>
      <dl>
        <dt>Type</dt><dd>${B.esc(B.FACILITY_LABELS.trail)}</dd>
        <dt>Length</dt><dd>${B.fmt(Math.round(p.length_m))} m</dd>
      </dl>
      <p class="muted">Off-street trail geometry from OpenStreetMap — crowdsourced, coverage varies.</p>`);
  }
```

- [ ] **Step 5: Show the stub note when toggled on with no data**

In the `[data-layer]` change handler (after the `planned` stub block, lines 340-342), add a `trails` branch:

```javascript
      if (cb.dataset.layer === "trails" && cb.checked && !(data.trails.features || []).length) {
        setDetail(`<h3>Off-street trails ${B.badgeHTML("stub")}</h3><p class="muted">${B.esc(data.trails.properties?.note || "No trail data this run.")}</p>`);
      }
```

- [ ] **Step 6: Manual verification in the browser**

Serve the site and confirm trails render on load:

```bash
cd site && python -m http.server 8000
```
Open `http://localhost:8000/index.html`. Expected:
- "Off-street trails" checkbox is present, checked, with a `crowdsourced` badge.
- Trail lines render in the trail blue (`#0369a1`) — the Lakefront Trail arc is visible along the lakefront.
- Clicking a trail shows its name, length, and the crowdsourced notice.
- Unchecking hides them; the URL gains `layers=...` without `trails`.

- [ ] **Step 7: Commit**

```bash
git add site/assets/js/map.js
git commit -m "feat: render OSM off-street trails on the geographic map (on by default)"
```

---

### Task 8: Render trails on the network + default overlay (network.js)

**Files:**
- Modify: `site/assets/js/network-model.js` (`DEFAULT_OVERLAYS` line 84)
- Modify: `tests/ui/network-model.test.js` (default-overlay assertions lines 118-123)
- Modify: `site/assets/js/network.js` (panes 23, layers 32, load 61-68, draw block, mount ~215, toggle, legend note, `showDetail`, stub restore ~337)

**Interfaces:**
- Consumes: `site/data/osm_trails.geojson`, `BSDNet.toLatLngs`, `BSD.FACILITY_COLORS.trail`.
- Produces: `"trails"` in `DEFAULT_OVERLAYS`; a `trails` pane/layer/toggle on the network, default-on, with stub handling mirroring Mellow.

- [ ] **Step 1: Update the JS model test (failing first)**

In `tests/ui/network-model.test.js`, update the two default-overlay assertions (lines 118-123) to expect `trails`:

```javascript
assert.deepStrictEqual(
  [...N.parseOverlays(null)], ["heat", "stations", "trails"],
  "parseOverlays: null (param absent) falls back to defaults heat+stations+trails"
);
assert.deepStrictEqual(
  [...N.parseOverlays(undefined)], ["heat", "stations", "trails"],
  "parseOverlays: undefined falls back to defaults heat+stations+trails"
);
```

- [ ] **Step 2: Run the JS test to verify it fails**

Run: `node tests/ui/network-model.test.js`
Expected: FAIL — an `AssertionError` on the default-overlays comparison.

- [ ] **Step 3: Add trails to DEFAULT_OVERLAYS**

In `site/assets/js/network-model.js` line 84:

```javascript
  const DEFAULT_OVERLAYS = ["heat", "stations", "trails"];
```

- [ ] **Step 4: Run the JS test to verify it passes**

Run: `node tests/ui/network-model.test.js`
Expected: PASS (script exits 0, no AssertionError).

- [ ] **Step 5: Add the trails pane and layer group**

In `network.js`, add `"trailsPane"` to `PANE_ORDER` (line 23) — place it right after `"mellowPane"` so trails sit above the Mellow background but below casing:

```javascript
  const PANE_ORDER = [
    "wardsPane", "mellowPane", "trailsPane", "heatPane", "casingPane", "plannedCasingPane",
    "linesPane", "plannedPane", "crashesPane", "stationsPane",
  ];
```

Add a `trails` layer group to the `layers` object (line 32-42):

```javascript
    trails: L.layerGroup(),
```

- [ ] **Step 6: Load the file**

In the `Promise.all` (lines 61-68), add the load and destructured name (after `plannedData`):

```javascript
  const [bikeRoutes, obstructionsData, mellowData, plannedData, osmTrailsData, wardsData, stations] = await Promise.all([
    BSD.loadJSON("data/bike_routes.geojson"),
    BSD.loadJSON("data/obstructions_mock.geojson"),
    BSD.loadJSON("data/mellow_routes.geojson"),
    BSD.loadJSON("data/planned_routes.geojson"),
    BSD.loadJSON("data/osm_trails.geojson"),
    BSD.loadJSON("data/wards.geojson"),
    BSD.loadJSON("data/intersections.json"),
  ]);
```

> IMPORTANT: `osm_trails.geojson` is inserted after `planned_routes.geojson` in BOTH the destructuring and the array — keep the positions aligned or `wardsData`/`stations` shift.

- [ ] **Step 7: Draw the trails**

After the Mellow draw block (after line 180), add — solid line in trail color with a stub sentinel exactly like Mellow:

```javascript
  if (osmTrailsData.features.length === 0) {
    const noDataMarker = L.marker([41.8781, -87.6298], { opacity: 0 });
    noDataMarker._trailsStub = true;
    layers.trails.addLayer(noDataMarker);
  } else {
    osmTrailsData.features.forEach((feature) => {
      const line = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        { color: BSD.FACILITY_COLORS.trail, weight: 4, opacity: 0.9, lineCap: "round", pane: "trailsPane" }
      );
      line.on("click", () => showDetail({ ...feature, _trail: true }));
      layers.trails.addLayer(line);
    });
  }
```

- [ ] **Step 8: Mount trails per state**

After the mellow mount (line 215), add:

```javascript
  if (state.overlays.has("trails")) layers.trails.addTo(map);
```

- [ ] **Step 9: Add the toggle to the side panel**

In the side-panel `.layer-control` HTML, after the Mellow toggle block (lines 296-299), add:

```html
        <div class="filter-row">
          <input type="checkbox" id="trails-toggle" ${state.overlays.has("trails") ? "checked" : ""}>
          <label for="trails-toggle">Off-street trails ${BSD.badgeHTML("crowdsourced")}</label>
        </div>
```

- [ ] **Step 10: Add the toggle handler + URL-restore stub note**

After the mellow toggle handler (after line 384), add:

```javascript
  document.getElementById("trails-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("trails"); else state.overlays.delete("trails");
    if (e.target.checked) {
      layers.trails.addTo(map);
      if (osmTrailsData.features.length === 0) {
        showDetail({ _trailsStub: true, properties: osmTrailsData.properties });
      }
    } else {
      map.removeLayer(layers.trails);
      if (osmTrailsData.features.length === 0) {
        document.getElementById("detail").innerHTML = "";
      }
    }
    syncURL();
  });
```

And next to the mellow/planned URL-restore stub checks (after line 342), add:

```javascript
  if (state.overlays.has("trails") && osmTrailsData.features.length === 0) {
    showDetail({ _trailsStub: true, properties: osmTrailsData.properties });
  }
```

- [ ] **Step 11: Handle the trail detail + stub in showDetail**

In `showDetail` (after the `_mellowStub` block, line 415), add a stub branch and a real-trail branch:

```javascript
    if (feature._trailsStub) {
      detail.innerHTML = `
        <div>
          <strong>Off-street trails</strong>
          <p class="muted">${BSD.esc(feature.properties.note)}</p>
        </div>
      `;
      return;
    }

    if (feature._trail) {
      const props = feature.properties;
      detail.innerHTML = `
        <div>
          <strong>${BSD.esc(props.name || "Off-street trail")}</strong> ${BSD.badgeHTML("crowdsourced")}
          <dl>
            <dt>Type</dt><dd>${BSD.esc(BSD.FACILITY_LABELS.trail)}</dd>
            <dt>Length</dt><dd>${BSD.fmt(Math.round(props.length_m))} m</dd>
          </dl>
          <p class="muted">Trail geometry from OpenStreetMap — crowdsourced, coverage varies.</p>
        </div>
      `;
      return;
    }
```

- [ ] **Step 12: Manual verification in the browser**

```bash
cd site && python -m http.server 8000
```
Open `http://localhost:8000/network.html`. Expected:
- "Off-street trails" toggle present, checked, `crowdsourced` badge.
- Trail lines render in trail blue on the metro canvas (Lakefront arc visible).
- Clicking a trail shows name + length + crowdsourced note.
- Unchecking removes them and updates `?overlays=` in the URL.
- The facility-types legend already lists "Off-street trail" (it iterates `FACILITY_LABELS`) — confirm it shows.

- [ ] **Step 13: Commit**

```bash
git add site/assets/js/network.js site/assets/js/network-model.js tests/ui/network-model.test.js
git commit -m "feat: render OSM off-street trails on the network (on by default)"
```

---

### Task 9: Documentation — README, SCHEMA, sources page

**Files:**
- Modify: `README.md` (Data sources & limitations table, ~line 30-40)
- Modify: `SCHEMA.md` (new section after mellow_routes, ~line 131)
- Modify: `site/assets/js/sources.js` (new SOURCES entry after `mellow_map`, line 107; fix CDOT description line 25)

**Interfaces:**
- Consumes: nothing (docs only).
- Produces: user-facing documentation of the `osm_trails.geojson` layer.

- [ ] **Step 1: Add the README data-source row**

In `README.md`, add a row to the Data sources table, after the CDOT Bike Routes row:

```markdown
| [OpenStreetMap Off-street Trails](https://www.openstreetmap.org) (Overpass API) | crowdsourced | Named off-street trails (Lakefront, 312 RiverRun, North Shore Channel, North Branch, etc.) that CDOT's on-street Bike Routes layer omits. Community-edited, so completeness/naming vary; no install dates; geometry intentionally extends past the city line (trails run into the forest preserves). Falls back to a stub if Overpass is unreachable. |
```

- [ ] **Step 2: Add the SCHEMA.md contract**

In `SCHEMA.md`, after the `mellow_routes.geojson` section (after line 131), add:

```markdown
## osm_trails.geojson — tier crowdsourced (falls back to stub)
LineString/MultiLineString FeatureCollection of named off-street trails, pulled
from the OpenStreetMap Overpass API by `pull_osm_trails.py`/`aggregate.py`. CDOT's
`bike_routes.geojson` is on-street only, so these trails (Lakefront, 312 RiverRun,
North Shore Channel, North Branch, etc.) come from OSM instead. OSM ways sharing a
`name` are grouped into one feature (a MultiLineString when the trail spans several
ways). Properties:

| key | type | notes |
|---|---|---|
| segment_id | string | `osm-trail-<slug>`, e.g. `osm-trail-lakefront-trail` |
| name | string | trail name from OSM `tags.name` |
| facility_category | "trail" | reuses the shared facility styling |
| length_m | float | total length across all parts |
| data_tier | "crowdsourced" | |

The query pulls only named off-street ways (`highway=cycleway`, or
`path`/`footway` with `bicycle=designated`) and excludes `is_sidepath=yes` to drop
road-parallel cycle tracks that duplicate CDOT on-street segments. If the pull
didn't run or Overpass was unreachable, this file falls back to the stub shape
(`properties.status = "no_data_yet"`).
```

- [ ] **Step 3: Fix the CDOT description and add the sources.js entry**

In `site/assets/js/sources.js` line 25, remove the misleading ", trails" from the CDOT description (that layer is on-street only):

```javascript
      description: "Current bike facility inventory (protected lanes, buffered lanes, painted lanes, greenways, shared-lane markings). On-street only — off-street trails come from the separate OpenStreetMap trails layer. We snapshot the layer on every run to build install history over time.",
```

Then add a new SOURCES entry immediately after the `mellow_map` object (after line 107, before the `ward_safety_index` entry):

```javascript
    {
      id: "osm_trails",
      name: "OpenStreetMap Off-street Trails",
      origin: "OpenStreetMap via the Overpass API",
      tier: "crowdsourced",
      cadence: "weekly pipeline run, best-effort (public Overpass instance, no uptime SLA)",
      description: "Named off-street trails — Lakefront Trail, 312 RiverRun, North Shore Channel Trail, North Branch Trail, and peers — that CDOT's on-street Bike Routes layer structurally omits. Pulled as named off-street ways and grouped into one feature per trail.",
      limitations: "Community-edited, so completeness and naming vary by contributor. No install dates. Geometry intentionally extends beyond the city line where a trail continues into the forest preserves. Road-parallel cycle tracks (is_sidepath) are excluded to avoid duplicating CDOT segments. Falls back to a stub if Overpass is unreachable during a run.",
      links: [
        { text: "OpenStreetMap", url: "https://www.openstreetmap.org" },
        { text: "Overpass API", url: "https://overpass-api.de" }
      ],
      metaId: "osm_trails"
    },
```

- [ ] **Step 4: Verify the sources page renders**

```bash
cd site && python -m http.server 8000
```
Open `http://localhost:8000/sources.html`. Expected: an "OpenStreetMap Off-street Trails" card with a `crowdsourced` badge, a record count (if the fixtures run populated `meta.json`), and the limitations text. Confirm the CDOT card no longer says "trails".

- [ ] **Step 5: Commit**

```bash
git add README.md SCHEMA.md site/assets/js/sources.js
git commit -m "docs: document OSM off-street trails layer; correct CDOT on-street scope"
```

---

## Final verification (all tasks)

- [ ] **Run the full Python test suite:**

Run: `pytest pipeline/tests -v`
Expected: all pass, including the new `test_aggregate_osm_trails.py`, `test_pull_osm_trails.py`, `test_fixtures_osm_trails.py`, and the added cases in `test_config.py` / `test_run_all_order.py`.

- [ ] **Run the JS model tests:**

Run: `node tests/ui/network-model.test.js` (and the other `tests/ui/*.test.js` for regressions)
Expected: each exits 0 with no AssertionError.

- [ ] **Rebuild fixtures and eyeball both screens** (map.html + network.html) with trails visible by default, then clear the fixtures provenance marker:

```bash
cd pipeline && python make_fixtures.py && python run_all.py --fixtures
rm -f pipeline/raw/PROVENANCE
```

Do NOT commit `site/data/*` artifacts from the fixtures run.
