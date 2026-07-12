# OSM Off-Street Trails Layer — Design

**Date:** 2026-07-12
**Status:** Approved (pending spec review)

## Problem

Major off-street trails — the Lakefront Trail, the 312 RiverRun, the North Shore
Channel Trail, and the North Branch Trail — appear on neither the geographic map
nor the schematic network. Root cause: the pipeline's only route source is the
CDOT Bike Routes layer (`hvv9-38ut`), which is an **on-street bikeways inventory
only**. Its five `displayrou` values (Bike Lane, Buffered, Protected,
Neighborhood Greenway, Marked Shared Lane) contain no off-street facilities. The
named trails appear in that dataset *only* as cross-street references
(`f_street`/`t_street`), never as route geometry, so nothing renders.

The stack was already *pre-wired* for trails — `config.py` maps `TRAIL` /
`OFF-STREET TRAIL` → `trail` and lists it in `FACILITY_CATEGORIES`, and
`common.js` defines a `trail` color (`#0369a1`) and label ("Off-street trail") —
but no data source ever fed that category in live runs. (The `make_fixtures.py`
fixture injects a fake `LAKEFRONT TRAIL` / `OFF-STREET TRAIL` corridor into the
bike_routes fixture, so the category lit up offline, masking the live gap.)

Investigation of alternative sources (see conversation, 2026-07-12):
- **Chicago Data Portal** — no dedicated off-street trail dataset exists; the
  city publishes trails only as PDF maps.
- **CMAP Bikeway Inventory System** — a live ArcGIS FeatureServer, but 209
  plan-organized layers whose only "existing Chicago" layers are frozen at
  2015–2016. Stale and unwieldy.
- **OpenStreetMap (Overpass API)** — the only single source with complete,
  current coverage of all four named trails (incl. the 2023 312 RiverRun).
  Crowdsourced.

**Decision:** pull named off-street trails from OpenStreetMap via the Overpass
API into a new, standalone, `crowdsourced`-tier layer.

## Design decisions (from brainstorming)

1. **Separate layer (Path A)**, not merged into `bike_routes.geojson`. Keeps the
   CDOT layer uniformly `real`-tier; mirrors how the crowdsourced Mellow layer is
   a distinct file/toggle. No trail data enters `real`-tier derived stats.
2. **Scope: named off-street trails** within a Cook-County-ish bounding box —
   full trail geometry (not clipped at the city line, since a trail dead-ending
   at the border would mislead). Not "all cycleways" (noisy), not the four
   hardcoded (arbitrary).
3. **Visible by default** on both the map and the network — trails are core bike
   infrastructure and their absence is the reported gap. The `crowdsourced` badge
   communicates provenance.
4. **De-dup: query-level `is_sidepath!=yes` filter only.** OSM often maps a
   road-parallel protected lane / cycle track as a separate named
   `highway=cycleway` that CDOT *also* carries; `is_sidepath=yes` marks these, so
   excluding them at query time drops the overlap at the source. No expensive
   geometric de-dup (it risks deleting legitimate trail that runs near a road,
   e.g. the Lakefront Trail alongside Lake Shore Drive). Intra-layer fragment
   duplication (many OSM ways sharing one trail name) is handled by grouping on
   `name`.

## Architecture

Mirrors the Mellow layer end-to-end: **pull archives raw, aggregate shapes,
non-fatal on failure.**

### 1. `pipeline/pull_osm_trails.py` (new)

POST an Overpass QL query to the Overpass API; save the raw response to
`pipeline/raw/osm_trails.json` untouched. Non-fatal, exactly like
`pull_mellow.py`: on any `requests`/parse failure, warn to stderr and leave the
raw file absent so `aggregate.py` ships a stub instead of failing the run.

**Bounding box:** `(41.60, -87.95, 42.20, -87.50)` (south, west, north, east) —
covers Chicago plus the North Branch Trail's northward extent into the forest
preserves.

**Overpass QL:**
```
[out:json][timeout:90];
(
  way["highway"="cycleway"]["name"]["is_sidepath"!="yes"](41.60,-87.95,42.20,-87.50);
  way["highway"="path"]["bicycle"="designated"]["name"]["is_sidepath"!="yes"](41.60,-87.95,42.20,-87.50);
  way["highway"="footway"]["bicycle"="designated"]["name"]["is_sidepath"!="yes"](41.60,-87.95,42.20,-87.50);
);
out geom;
```
`out geom;` returns each way's inline `geometry` array (`[{lat, lon}, ...]`),
avoiding a second node-resolution pass.

### 2. `build_osm_trails(raw)` in `aggregate.py` (new)

Parse the Overpass ways and **group by `tags.name`** into one feature per named
trail. Each way becomes a LineString; a trail with multiple ways becomes a
MultiLineString (kept intact, same rationale as `build_mellow` — one Leaflet
layer per trail, not per fragment).

Per-feature properties:
- `segment_id`: `osm-trail-<slug(name)>`
- `name`: the trail name (e.g. "Lakefront Trail")
- `facility_category`: `"trail"` (reuses the pre-wired color/label)
- `length_m`: metric length, rounded to 0.1
- `data_tier`: `"crowdsourced"`

When `pipeline/raw/osm_trails.json` is absent, `main()` writes
`stub_layer("OpenStreetMap off-street trails were not pulled this run ...")` —
identical fallback shape to Mellow.

### 3. `pipeline/config.py`

Add: `OVERPASS_API_URL`, `OSM_TRAILS_BBOX`, and the QL query template constant.

### 4. `pipeline/run_all.py`

Add `["pull_osm_trails.py"]` to `LIVE_STAGES`, adjacent to `["pull_mellow.py"]`.

### 5. Output + `meta.json`

Write `site/data/osm_trails.geojson`. Add a `meta.json` source entry
`{id: "osm_trails", name: "OpenStreetMap Off-street Trails", tier: "crowdsourced",
records: N}`, conditioned on the layer having features (same pattern as the
Mellow source entry).

## Front-end

Both `site/assets/js/map.js` and `site/assets/js/network.js`:
- New `trailsPane`, `L.layerGroup()`, and a toggle **checked (on) by default**.
- Render trail features as polylines in the `trail` color (`#0369a1`), with the
  `crowdsourced` badge on the toggle label.
- Detail panel on click: trail `name`, length, and tier badge.
- Empty-layer / stub handling identical to the Mellow `_mellowStub` path.
- Legend gains an "Off-street trails" entry.

## Docs

- `README.md` — new row in the Data sources table (tier `crowdsourced`;
  limitations: completeness varies by OSM editing, no install dates, geometry
  intentionally extends beyond the city line).
- `SCHEMA.md` — publish the `osm_trails.geojson` contract.
- `site/assets/js/sources.js` — add the OSM trails source card.

## Fixtures & tests

- `make_fixtures.py`:
  - Add `build_osm_trails()` emitting Overpass-shaped raw JSON for a couple of
    named trails (including a Lakefront Trail), written to
    `pipeline/raw/osm_trails.json`.
  - **Remove the `OFF-STREET TRAIL` corridor (`LAKEFRONT TRAIL`) from the
    `CORRIDORS` list** so the bike_routes fixture matches the real on-street-only
    CDOT shape. Lakefront is now represented in the osm_trails fixture instead —
    keeping fixtures faithful and avoiding double representation.
- `pipeline/tests/` — add tests asserting:
  - `build_osm_trails` groups ways by name into one feature per trail,
  - features are tagged `data_tier="crowdsourced"` and
    `facility_category="trail"`,
  - an absent raw file yields a `no_data_yet` stub.

## Out of scope (YAGNI)

- No dated snapshots / install-history for trails (CDOT snapshotting exists for
  mileage-over-time; OSM has no comparable install-date semantics).
- No folding trail mileage into ward / corridor / facility-mix derived stats
  (that was the rejected Path C — would mix crowdsourced data into `real`/derived
  numbers).
- No geometric de-dup against CDOT (query-level sidepath filter only).
- No OSM `route=bicycle` relation handling — named ways are sufficient for a
  visual overlay and avoid relation/way double-pulls.
