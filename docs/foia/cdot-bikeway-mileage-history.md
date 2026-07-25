# FOIA request — CDOT historical Bike Lane Mileage Tracker

**Purpose.** The public CDOT Bike Routes portal layer (`data.cityofchicago.org`, dataset
`hvv9-38ut`) is *current-state only* — no install date per segment — and the quarterly Bike
Lane Mileage Tracker on the Complete Streets "Existing Bike Network" page is overwritten each
quarter with no published archive. To build a bikeway-mileage time series (and correlate
infrastructure growth against crash trends), we need the historical quarterly values CDOT
retains internally. This request targets those records.

**How to submit.**
- Online portal (GovQA): https://www.chicago.gov/publicrecords → "All Other Departments" →
  Department of Transportation
- Or email the body below to **CDOTfoia@cityofchicago.org** (an officially listed channel)
- Statutory response: 5 business days (may be extended 5 more). First 50 B&W pages free;
  electronic records are typically provided at no or minimal cost.
- Note: in Chicago, the requester name and request text are published in the public CDOT FOIA log.

---

## Request body

Moved to the outbox (canonical send-ready copy):
`docs/outbox/2026-07-12--foia--cdot--bikeway-mileage-history.md`.
The City Clerk fallback request:
`docs/outbox/2026-07-12--foia--city-clerk--bikeway-mileage-council-records.md`.
---

## Notes for the requester

- **The core items are 1, 2, and 4.** They are the ones most likely to yield a clean historical time
  series. If you want to minimize the chance of a "burdensome" pushback, you can submit only those
  three and add the others later.
- **Why item 4 matters:** a GIS layer with a per-segment install date would let us reconstruct the
  full historical mileage-by-quarter series *retroactively* — something the overwritten tracker and
  the date-less public portal layer cannot give us. It is the single highest-value record here.
- **If CDOT says no historical versions are retained:** that answer is itself useful — it confirms
  the pipeline's forward-only snapshot approach (`data/snapshots/`, `infra_growth_trend()`) is the
  only viable path, and the FOIA log will document that the data does not exist.
- **Cross-reference:** see `DECISIONS.md` (#18) and `log.md` (this folder) for how any returned data would
  feed `bikeway_mileage_series.json` and the per-ward `infra_growth_trend`.

---

## Outcome — granted 2026-07-24 (ref S145367-071326)

Sent 2026-07-13 via the GovQA portal; CDOT took its 5-day extension the same day and
released records on 2026-07-24. No exemptions cited, no fees charged.

**Item 4 — the one that mattered — was answered.** CDOT's internal bikeway layers carry a
per-segment install year (`INST_YR` in the 2020–2022 schema, `BW_INST_YR` in 2023–2025).
Better still, `CompleteStreets_Dashboard.xlsx` carries CDOT's own **annual bikeway mileage
by facility type for 2010–2025** — both the standing network at each year end and the miles
installed during the year. That is the historical series this request existed to obtain.

The note above — "if CDOT says no historical versions are retained, that confirms the
forward-only snapshot approach is the only path" — is now moot. They were retained.

**What this changed in the repo:**

- `pipeline/foia_bikeway_history.py` extracts the series into `data/cdot_bikeway_history.json`.
- Released records committed under `data/foia/S145367-071326/`, with a full-release hash manifest.
- `DECISIONS.md` #35 records what it means for `bikeway_mileage_series.json`.

**Two things to carry forward:**

1. **CDOT's "miles installed" includes concrete upgrades of existing protected lanes.** In
   2023 CDOT reports 50.42 miles installed against 25.09 miles of actual network growth. Any
   published comparison against a "miles built" claim has to say which of the two it means.
2. **A single year's GIS layer cannot reconstruct the past.** Grouped by install year it
   describes the network that *survived* to that year — removed lanes are gone, and upgraded
   lanes carry the upgrade year. CDOT's buffered mileage falls after 2022 for exactly this
   reason. Use the dashboard series for history.

Detail, layer inventory, and the four known gaps in the release:
[`data/foia/S145367-071326/README.md`](../../data/foia/S145367-071326/README.md).
