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
  no analysis, no LLMs, no side quests. The one documented exception is
  `classify_safety_topic.py`, which runs *after* all pulls, not as a pull
  module itself — see "LLM topic classification" below and DECISIONS.md #15.
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
- `pipeline/emit_api.py` — writes the agent-facing static API (`site/api/v1/`,
  `site/llms.txt`, `site/sitemap.xml`) from the committed `site/data/`
  contract. If a change to this file alters an endpoint's output shape, the
  matching hand-written schema under `site/api/v1/schemas/` must be updated
  in the same PR — CI (`pipeline/check_api.py`) and reviewers will catch
  drift, but it's on you to know where that source of truth lives.

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

## Mellow Bike Map

`mellow_routes.geojson` is pulled live by `pipeline/pull_mellow.py` from the
[mellow-bike-map](https://github.com/jeancochrane/mellow-bike-map) project's
public GeoJSON API (`mellowbikemap.com/api/routes/`, MIT licensed) — it is
**not** a stub layer, despite shipping as one until the pipeline is first run
with network access. The API returns one MultiLineString feature per
`route_type` (sidewalk/street/route/path); `aggregate.py` keeps each intact
(not exploded into per-segment LineStrings — see SCHEMA.md) and tags every
feature `data_tier: "crowdsourced"`.

This is a small third-party app with no uptime guarantee, so `pull_mellow.py`
treats a failed pull as non-fatal: it warns and leaves `raw/mellow_routes.geojson`
absent, and `aggregate.py` falls back to the stub layer for that run rather than
failing the whole pipeline. If the app ever goes offline for good, the repo's
Django fixtures (`app/mbm/fixtures/mellowroute.json`) only contain OSM way ids,
not geometry, so a real fallback would mean standing up the app locally against
a `chicago_ways` OSM extract — treat that as a last resort, not routine.

## Ward accountability layer (voting records, hearings, menu spending)

`council_records.json`, `aldermen_safety_record.json`, `hearings.json`, and
`menu_spending.json` all pull from third-party-hosted sources outside our
control, so every one of `pull_council_records.py`, `pull_hearings.py`, and
`pull_menu_spending.py` is non-fatal on failure — same posture as
`pull_mellow.py`. See DECISIONS.md #14 for what each source can and can't do
(notably: Legistar's council data is frozen at 2023-06-21, and no working
public API was found for Chicago's newer eLMS system or for a live meeting
calendar — both degrade to an honest stub/link-out rather than fabricating or
silently going stale).

`ward_safety_index.json`'s `infra_growth_trend` needs at least two
`data/snapshots/bike_routes_*.geojson` snapshots to compute a growth rate —
it's `null` until the pipeline has run at least twice over time.

## LLM topic classification

`classify_safety_topic.py` tags each record `pull_council_records.py` already
fetched as `topic_relevant: true/false` (an LLM call, Haiku 4.5 by default,
structured tool-use output) — see DECISIONS.md #15 for why this is an explicit
exception to "no LLMs in pull modules," not a loophole. Ground rules for this
stage specifically:

- It may only classify records that were already deterministically fetched.
  Never let it originate a matter, sponsor, vote, or date.
- Tags are cached (`pipeline/raw/safety_topic_tags.json`) and overridable via
  a hand-maintained `pipeline/raw/safety_topic_corrections.json` — same
  manual-override posture as `aldermen.json`.
- If `ANTHROPIC_API_KEY` is unset or the call fails, fall back to
  `tagged_by: "keyword_fallback"` rather than blocking the pipeline; the UI
  must badge `llm` vs `keyword_fallback` tags distinctly (`derived` tier).

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

## Local git housekeeping

This repo is often open in several worktrees/chats at once, and merged
branches + dead worktree admin dirs pile up locally (the remote side is
handled by GitHub's "delete branch on merge"). Run the sweeper any time:

```
python .claude/tools/git_tidy.py           # dry-run: show what's removable
python .claude/tools/git_tidy.py --apply   # actually remove it
```

It only ever removes a worktree that is idle (no live session-guard
heartbeat), merged into `origin/main`, and clean, and only deletes branches
`git branch -d` accepts — so live sessions and unmerged work are safe. It
also purges the ghost `.git/worktrees/*` dirs that `git worktree prune`
can't delete under OneDrive.
