# CDOT FOIA S145367-071326 — historical Bike Lane Mileage Tracker

**Agency:** Chicago Department of Transportation
**Submitted:** 2026-07-13 (GovQA / Chicago Public Records Center)
**Responded:** 2026-07-24 by G. Rubenstein, CDOT FOIA Officer
**Disposition:** Granted. Responsive records released, no exemptions cited, no fees charged.
**Released as:** `OneDrive_2026-07-24.zip`, folder `2026-07-20 - Bike Lane Mileage Tracker`

The request and its rationale live in
[`docs/foia/cdot-bikeway-mileage-history.md`](../../../docs/foia/cdot-bikeway-mileage-history.md);
the request body is in
[`docs/outbox/2026-07-12--foia--cdot--bikeway-mileage-history.md`](../../../docs/outbox/2026-07-12--foia--cdot--bikeway-mileage-history.md).

## Why this release matters

It answers the question the pipeline could not: **what the bike network looked like
before we started watching it.**

The public CDOT Bike Routes layer (`hvv9-38ut`) is current-state only, with no
install date per segment, and the quarterly mileage tracker on the Complete Streets
page is overwritten in place. So `aggregate.build_bikeway_mileage_series()` builds
its series *forward* from `data/snapshots/` — which begins 2026-07-11.

Two records here change that:

- **`CompleteStreets_Dashboard.xlsx`** carries CDOT's own annual bikeway mileage by
  facility type for **2010–2025** — standing network and miles installed per year.
- **The 2020–2025 GIS layers** carry a per-segment install year (`INST_YR`, later
  `BW_INST_YR`) — the field item 4 of the request asked for, and the field the
  public layer omits.

`pipeline/foia_bikeway_history.py` extracts both into
[`data/cdot_bikeway_history.json`](../../cdot_bikeway_history.json). Every year's
per-category sum reconciles to the total CDOT published in the same sheet.

## What was released, against what was asked

| # | Requested | Outcome |
|---|-----------|---------|
| 1 | Every version of the mileage tracker | **Partial.** Annual values 2010–2025 in the dashboards, not the individual quarterly snapshots. |
| 2 | Source spreadsheet / database | **Yes.** Both dashboard workbooks, including a `Network_Bikeways` sheet holding a GIS export dated 2022-11-28. |
| 3 | File version history and timestamps | **Not provided.** No SharePoint/OneDrive version history. Partial substitute: the GIS layers carry per-segment `EDIT_DATE_` / `QAQC_DATE` fields. |
| 4 | GIS bikeway layer with install dates | **Yes** — the core win. See the layer table below. |
| 5 | Annual/quarterly miles installed, with backup | **Annual yes**, quarterly no. The dashboard's "Bikeways Installs" block gives miles installed per year by facility type. |
| 6 | Transmittal records (marked optional) | Not provided; the request said items 1–5 could make it moot. |

## Contents

`records/` holds the release as received. Directory layout and filenames are CDOT's,
not ours.

### GIS layers (`records/GIS/`)

| Year | File | Segments | CRS | Install-date field |
|------|------|----------|-----|--------------------|
| 2010 | `2010_Bike-Network_Final.zip` | 358 | EPSG:3435 | `Yr_Install` (populated for only 21 segments) |
| 2018 | `2018_EOY_Bike_Routes.shp` | 759 | EPSG:4326 | none — KML-style export |
| 2019 | `2019_Bike-Network.shp` | 774 | WGS84 | none |
| 2020 | `WORKING_2020_BIKE_FACILITIES_09.22.shp` | 828 | EPSG:6455 | `INST_YR` / `INST_MO` |
| 2021 | `2021_Bike_Network.shp` | 882 | EPSG:6455 | `INST_YR` / `INST_MO` |
| 2022 | `2022_Bike_Network-final.shp` | 953 | EPSG:6455 | `INST_YR` / `INST_MO` |
| 2023 | `2023_Bike-Network.shp` | 841 | EPSG:6455 | `BW_INST_YR` / `BW_INST_MO` |
| 2024 | `Bikeway_Network_2024_Final.shp` | 931 | EPSG:6455 | `BW_INST_YR` / `BW_INST_MO` |
| 2025 | `2025_Bike Network_internal.shp.zip` | 1008 | — | `BW_INST_YR` / `BW_INST_MO` (attributes only — see gaps) |

The schema changes three times across the series: a 2010 form, a 2018–2019
export-style form with no install dates, an `INST_*` form (2020–2022), and a `BW_*`
form (2023–2025). Anything reading these layers must handle all four.

### Spreadsheets

- `records/CompleteStreets_Dashboard.xlsx` — the program dashboard. Sheet
  `R_Dashboard` is the machine-readable form (stable `R_*` row labels); sheet
  `Dashboard` is the same numbers laid out for people.
- `records/_archive/BikeProgram_Dashboard.xlsx` — an earlier archived dashboard,
  network totals as of a 2022-11-28 GIS export.

### Not in git

Seven scanned year-end report PDFs (2011–2015, 2017, 2018 — about 69 MB) are part of
the release but excluded for repo weight. `manifest.json` records every released
file with its SHA-256, including these, so the omitted originals stay verifiable.
They are narrative reports; the numbers this project publishes all come from the
spreadsheets and GIS layers above.

## Known gaps in the release

Candidates for a follow-up request — see `docs/foia/log.md`.

1. **The 2025 layer has no geometry.** `2025_Bike Network_internal.shp.zip` contains
   `.dbf`, `.shx`, `.prj`, `.cpg`, `.sbn`, `.sbx` — but no `.shp`. The 1,008 attribute
   rows are readable; the lines are not. Almost certainly a packaging slip.
2. **No GIS layers for 2011–2017.** The series jumps 2010 → 2018. The 2011–2015
   year-end report PDFs cover part of that window in narrative form only.
3. **Annual granularity only.** The request asked for each quarterly tracker update;
   what came back is year-end values.
4. **No document version history** (item 3), so we cannot show when a published
   figure was revised after the fact.

## Caveat on reconstructing history from the GIS layers

Grouping a single year's layer by install year gives the network *that survived to
that year*, not the network as it stood in the past. Removed lanes are absent, and a
lane upgraded in place carries its upgrade year. CDOT's own buffered mileage falls
after 2022 (115.6 → 106.5) precisely because buffered lanes became protected.

Use the annual dashboard series for history. Use the segment data for segment-level
questions.
