# CONTRIBUTING

This project is built to be extended and forked. The short version: all the
knobs live in `pipeline/config.py`, all the published schemas live in
`SCHEMA.md`, and the UI never has to change when you swap a data source that
honors those schemas.

## Code layout

- `pipeline/config.py` — every dataset id, path, filter, date threshold, and
  mapping table. Swapping a source means editing this file, not the modules.
- `pipeline/socrata.py` — shared fetch helpers (paging, batched id lookups,
  GeoJSON export). All pull modules go through it.
- `pipeline/pull_*.py` — one dataset each. Deterministic data fetching only:
  no analysis, no LLMs, no side quests.
- `pipeline/spatial_join.py` — crash → containing ward + nearest bikeway
  segment (30 m cap, distances computed in EPSG:26916 / UTM 16N).
- `pipeline/aggregate.py` — owns every published schema; writes `site/data/`.
- `pipeline/make_mock_obstructions.py` — generates the mock obstruction layer.
- `pipeline/make_fixtures.py` — synthetic raw inputs for offline runs and CI.
- `pipeline/run_all.py` — one-command entry point (`--fixtures` for offline).
- `site/` — static vanilla JS + vendored Leaflet. One `<name>.html` +
  `assets/js/<name>.js` pair per screen; shared `assets/js/common.js` owns
  nav, data-quality badges, and disclaimers. **All tier labeling must go
  through `BSD.badgeHTML()` / `BSD.noticeHTML()`** so "data quality is always
  visible" stays uniform.

## Swap the obstruction data source

The mock layer exists to be replaced. Produce `site/data/obstructions_mock.geojson`'s
exact schema (see SCHEMA.md → "obstructions_mock.geojson") from any source:

- a Bike Lane Uprising export, once a data-sharing agreement exists;
- a 311-derived extract (set `data_tier: "proxy"`);
- another city's crowdsourced feed.

Keep every field, set `data_tier` honestly, and nothing downstream
re-architects. The `obstruction_type` enum is a placeholder pending
consultation with Bike Lane Uprising — treat it as swappable.

## Fill the stub layers

- `planned_routes.geojson` — CDOT publishes planned bikeways only as PDF maps
  (Chicago Cycling Strategy). Digitizing them is manual work; include a
  "last verified" date in `properties.note` and keep the dashed styling.
- `mellow_routes.geojson` — the open-source
  [mellow-bike-map](https://github.com/jeancochrane/mellow-bike-map) project
  tags low-stress OSM ways; its Django fixtures can be exported
  (`manage.py dumpdata`) and converted to LineStrings. Tag every feature
  `data_tier: "crowdsourced"` — it is curated, not verified.

## Fork for another city

1. Edit `pipeline/config.py`: dataset ids (any Socrata portal works as-is),
   `METRIC_CRS` if you're outside UTM zone 16N, `FACILITY_CATEGORY_MAP` for
   your DOT's taxonomy, `SR311_TYPE_SUBSTRINGS` for your 311 system.
2. Point the wards pull at your city's council-district polygons (any polygon
   layer with a district id property works — see `_first_key` candidates in
   `spatial_join.py`).
3. Update site copy (city name, links). Schemas and UI are city-agnostic.

## Ground rules for PRs

- Data-fetching modules stay deterministic. Analysis lives in `aggregate.py`.
- Every new layer or metric carries a data-quality tier and a visible badge.
  No exceptions — that's the product's credibility.
- No submission or collection features. This stays an evidence layer; report
  flows link out to 311 / Bike Lane Uprising.
- Changing any published schema means bumping `CONTRACT_VERSION` in
  `pipeline/config.py` and updating `SCHEMA.md` in the same PR.
- Never invent alderman names — `site/data/aldermen.json` is filled manually
  from the official lookup or left null.
