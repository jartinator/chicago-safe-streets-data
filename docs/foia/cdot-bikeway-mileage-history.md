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
