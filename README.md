# On Your Left! (OYL)

On Your Left! (OYL) — a Chicago bike-safety evidence dashboard. *Chicago bike safety, on the record.*

An independent, open-source, **read-only** dashboard that shows where bike
infrastructure type and cyclist-involved traffic crashes overlap across
Chicago — drillable from **ward → corridor → intersection**. Built for
advocates and residents, and to give aldermen ward-specific visibility into
problem areas. OYL publishes no bike-lane-obstruction data of its own — see a
blocked bike lane? report it at Bike Lane Uprising (below).

**This is an evidence layer, not a collection layer.** It accepts no reports,
has no accounts, and no forms. See a problem in the real world? Report it where
reports actually go: [311](https://311.chicago.gov) for city service requests,
[Bike Lane Uprising](https://www.bikelaneuprising.com) for blocked bike lanes.

## How to read this

Everything here is a **directional, visual signal — not statistical analysis**.
The maps show density bands and spatial overlap, not regressions or causal
claims. Raw counts are **not normalized by ridership** (no public cyclist-volume
data is joined yet), so busy corridors look worse than dangerous quiet ones.
Use it to spot patterns worth acting on, not to prove causation.

> **Dooring is undercounted everywhere on this site.** Official crash records
> only include "reportable" crashes (over $1,500 damage or injury), and bike
> dooring is structurally excluded unless it also meets those criteria. Any
> crash density shown here understates dooring risk — especially on
> painted-lane corridors.

## Data sources & limitations

| Source | Tier | Known limitations |
|---|---|---|
| Traffic Crashes — [Crashes](https://data.cityofchicago.org/d/85ca-t3if) / [People](https://data.cityofchicago.org/d/u6pd-qa9d) / [Vehicles](https://data.cityofchicago.org/d/68nd-jvt3) | real | Reliable citywide only from Sept 2017; recent months provisional (records get amended/reclassified); dooring structurally undercounted (above). Cyclist filter lives in People (`person_type = BICYCLE`), joined on `CRASH_RECORD_ID`. |
| [CDOT Bike Routes](https://data.cityofchicago.org/d/hvv9-38ut) | real | No install dates; current-state only; no planned/future layer. The pipeline snapshots this layer on every run into `data/snapshots/` to build install history over time. |
| [OpenStreetMap Off-street Trails](https://www.openstreetmap.org) (Overpass API) | crowdsourced | Named off-street trails (Lakefront, Bloomingdale/606, Major Taylor, North Shore Channel, North Branch, etc.) that CDOT's on-street Bike Routes layer omits. Community-edited, so completeness/naming vary; no install dates; geometry intentionally extends past the city line (trails run into the forest preserves). This environment's egress policy blocks Overpass, so trails currently ship from a hand-traced curated fallback (`data/curated_trails.geojson`, approximate, still crowdsourced tier) instead; falls back further to a stub if that's absent too. See DECISIONS.md #20. |
| [Mellow Bike Map](https://mellowbikemap.com) (jeancochrane/mellow-bike-map) | crowdsourced | Rider-tagged low-stress streets. `mellow_routes.geojson` (the raw pull) still ships for any page that reads it, but the network map no longer loads it directly — it's buffer-matched against CDOT Bike Routes (25 m) and deduped into `mellow_connectors.geojson`: overlapping mellow drops, the non-overlapping remainder renders as connector-tier geometry, and roster greenway segments carry the `mellow` quality grade instead. See DECISIONS.md #24. |
| Main routes (curated line roster, `data/main_routes.json`) | derived | The 21 marquee corridors (14 street lines + 7 trail lines, owner-signed count) drawn as major routes on both maps — each a named corridor end-to-end with facility-grade mileage computed along its length. The roster is editorial: we chose which corridors count as main routes; segment grades and mileage are computed from CDOT Bike Routes + OSM trails each run. Corridor gaps stay holes — geometry is never fabricated; street lines (derived, from CDOT) and trail lines (crowdsourced, from OSM) never blend tiers. On the network map, routes are grouped into three toggleable tiers (Trails / Main routes / Connectors), quality is an opt-in border with four independent grades (protected / paint / mellow / none; off-street trails exempt), and a comfort-floor filter (Any / Paint+ / Protected only) drains below-floor stretches to neutral gray without ever breaking a route's geometry; the transportation map keeps per-segment grade coloring. See DECISIONS.md #24. |
| Ward boundaries (2023 remap) | real | Clean spatial-join target; redrawn only at redistricting. |
| [311 Service Requests](https://data.cityofchicago.org/d/v6vf-nfxy) (bike-related) | proxy | Self-reported — biased toward wards with engaged 311 users; request-type names shift over time (we filter by substring). |
| Camera violations — [speed](https://data.cityofchicago.org/d/hhkd-xvj4) / [red-light](https://data.cityofchicago.org/d/spqx-js37) | proxy | Aggressive-driving proxy, not crashes; exists only at fixed camera locations, so sparse and location-biased. |
| Bike-lane obstructions | *not published* | OYL publishes no obstruction data at all. See a blocked bike lane? Report it at [Bike Lane Uprising](https://www.bikelaneuprising.com). |
| City Council legislation — [Legistar Web API](https://webapi.legistar.com/v1/chicago) | real | Frozen at 2023-06-21 — Chicago's council migrated to a new system (eLMS) after that date with no confirmed public API. The gap is now covered post-2023 by Chicago Councilmatic (below), so `council_records.json` overall is current to the present even though the Legistar half alone is frozen. |
| [Chicago Councilmatic](https://chicago.councilmatic.org) (DataMade) | real | A republished mirror of the official council record, not the city's own system — current post-2023 (covers the Legistar gap, above), but exactly how its scraper reaches Chicago's post-migration source isn't verifiable from outside DataMade. Contested-vote data only surfaces genuine roll-call splits (~1.4% of post-2023 votes); attendance is deliberately not published (see DECISIONS.md). |

Every layer in the UI carries a **real / proxy / mock / crowdsourced / no-data-yet**
badge at all times. Full field documentation: [SCHEMA.md](SCHEMA.md).

## For agents (static API)

Everything under `/api/v1/` is a static, versioned, additive JSON namespace,
generated (`pipeline/emit_api.py`) from the same committed `site/data/`
contract as the human site — not a live service, so there's nothing to
authenticate, rate-limit, or keep running. It never mutates: new fields and
endpoints get added, existing ones don't change shape without a
`CONTRACT_VERSION` bump.

- Start at [`llms.txt`](llms.txt) or [`/api/v1/index.json`](api/v1/index.json)
  — either one lists every endpoint, its size, and a fetch recipe for common
  questions.
- Every file's shape is a hand-written [JSON Schema](site/api/v1/schemas/),
  validated in CI (`pipeline/check_api.py`) — the schemas are the contract,
  not derived from the code that writes them.
- OYL publishes no obstruction data at all — not in this API, not on the
  human site; every response says so.

## Repo layout

```
pipeline/    Python: Socrata pulls -> spatial join (crash -> nearest bikeway
             segment + containing ward) -> aggregation -> site/data/*.json|geojson
site/        Static front-end (vanilla JS + vendored Leaflet):
             index (geographic map), network (schematic map), findings,
             table (+ CSV export), sources, methodology, action, ward
             (printable one-pager, brief/plain registers), contributing
data/snapshots/   Dated copies of the CDOT Bike Routes layer
SCHEMA.md    Published data contracts (the site's data/ files ARE the dataset)
DECISIONS.md Reasoned calls where the project docs were silent
CONTRIBUTING.md   Swap data sources, fill stub layers, fork for another city
```

## Run it locally

```bash
cd pipeline
python3 -m pip install -r requirements.txt
python3 run_all.py               # live pull from the Chicago Data Portal
# or, with no network / for a demo:
python3 run_all.py --fixtures    # synthetic data through the real pipeline

cd ../site
python3 -m http.server 8000      # http://localhost:8000
```

> The committed `site/data/` is a real Chicago Data Portal pull (see
> `meta.json.provenance`). If a fixtures build ever lands instead, every page
> shows a "demo build" banner and `check_provenance.py`/data-guard fail.

## Weekly refresh

Automated: `.github/workflows/data-refresh.yml` runs the live pipeline every
Monday on a GitHub runner and opens a **reviewed PR** (`data/auto-refresh`)
with the sanity output in its body — skim row counts, date ranges, and match
rates, then merge. Trigger it manually anytime from the Actions tab
(workflow_dispatch). One-time setup: repo **Settings → Actions → General →
Workflow permissions → allow GitHub Actions to create pull requests**.

Manual fallback (works from any machine that can reach the portal):

1. `python3 pipeline/run_all.py` (from `pipeline/`)
2. Review the printed sanity output (row counts, date ranges, % of crashes
   matched to a ward/bikeway); run `python3 pipeline/check_provenance.py`.
3. Commit the changed `site/data/` and `data/snapshots/`, PR to `main`.

## Deploy

Merging to `main` triggers `.github/workflows/deploy.yml`
(repo root), which publishes `site/` to GitHub Pages. One-time setup:
repo **Settings → Pages → Source: "GitHub Actions"**. Data refresh arrives
via reviewed PRs (scheduled or manual) — CI only ships what was committed.
