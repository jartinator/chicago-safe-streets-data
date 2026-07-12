# Chicago Bike Safety Correlation Dashboard

An independent, open-source, **read-only** dashboard that shows where bike-lane
obstructions, bike infrastructure type, and cyclist-involved traffic crashes
overlap across Chicago — drillable from **ward → corridor → intersection**.
Built for advocates and residents, and to give aldermen ward-specific
visibility into problem areas.

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
| [OpenStreetMap Off-street Trails](https://www.openstreetmap.org) (Overpass API) | crowdsourced | Named off-street trails (Lakefront, 312 RiverRun, North Shore Channel, North Branch, etc.) that CDOT's on-street Bike Routes layer omits. Community-edited, so completeness/naming vary; no install dates; geometry intentionally extends past the city line (trails run into the forest preserves). Falls back to a stub if Overpass is unreachable. |
| Ward boundaries (2023 remap) | real | Clean spatial-join target; redrawn only at redistricting. |
| [311 Service Requests](https://data.cityofchicago.org/d/v6vf-nfxy) (bike-related) | proxy | Self-reported — biased toward wards with engaged 311 users; request-type names shift over time (we filter by substring). |
| Camera violations — [speed](https://data.cityofchicago.org/d/hhkd-xvj4) / [red-light](https://data.cityofchicago.org/d/spqx-js37) | proxy | Aggressive-driving proxy, not crashes; exists only at fixed camera locations, so sparse and location-biased. |
| Bike-lane obstructions | **mock** | Entirely synthetic demonstration data. Schema mirrors Bike Lane Uprising's public submission fields (they have no public API); the category enum is a placeholder pending a data-sharing conversation. |
| City Council legislation — [Legistar Web API](https://webapi.legistar.com/v1/chicago) | real | Frozen at 2023-06-21 — Chicago's council migrated to a new system (eLMS) after that date with no confirmed public API. The gap is now covered post-2023 by Chicago Councilmatic (below), so `council_records.json` overall is current to the present even though the Legistar half alone is frozen. |
| [Chicago Councilmatic](https://chicago.councilmatic.org) (DataMade) | real | A republished mirror of the official council record, not the city's own system — current post-2023 (covers the Legistar gap, above), but exactly how its scraper reaches Chicago's post-migration source isn't verifiable from outside DataMade. Contested-vote data only surfaces genuine roll-call splits (~1.4% of post-2023 votes); attendance is deliberately not published (see DECISIONS.md). |

Every layer in the UI carries a **real / proxy / mock / crowdsourced / no-data-yet**
badge at all times. Full field documentation: [SCHEMA.md](SCHEMA.md).

## Repo layout

```
pipeline/    Python: Socrata pulls -> spatial join (crash -> nearest bikeway
             segment + containing ward) -> aggregation -> site/data/*.json|geojson
site/        Static front-end (vanilla JS + vendored Leaflet), 7 screens:
             index (geographic map), network (schematic map), findings,
             table (+ CSV export), sources, action, contributing
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

> **Current data is fixture data.** The committed `site/data/` was built with
> `--fixtures` because the build sandbox could not reach
> `data.cityofchicago.org`. Every page shows a "demo build" banner until
> someone runs `python3 run_all.py` for real and commits the refreshed
> `site/data/`. The pipeline code paths are identical either way.

## Weekly refresh

1. `python3 pipeline/run_all.py`
2. Review the printed sanity output (row counts, date ranges, % of crashes
   matched to a ward/bikeway).
3. Commit the changed `site/data/` and `data/snapshots/`, merge to `main`.

## Deploy

Merging to `main` triggers `.github/workflows/deploy.yml`
(repo root), which publishes `site/` to GitHub Pages. One-time setup:
repo **Settings → Pages → Source: "GitHub Actions"**. Data refresh is
deliberately a local, human-reviewed step — CI only ships what was committed.
