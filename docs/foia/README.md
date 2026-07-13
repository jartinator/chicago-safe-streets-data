# FOIA requests — index

All open-records work lives in this folder: per-request rationale/dossier
files, the supporting research, and the log. **Send-ready request bodies
live in `docs/outbox/`** (one file per outbound message, front-matter
tracked) — this folder links to them.

| Request | File | Status |
|---|---|---|
| CDOT historical Bike Lane Mileage Tracker (+ City Clerk fallback) | `cdot-bikeway-mileage-history.md` | Drafts in Gmail (2026-07-12), not yet sent |
| CDOT bicycle count data (2009 study, counters, Replica, 2023 ridership claims) | [`docs/outbox/2026-07-13--foia--cdot--bicycle-count-data.md`](../outbox/2026-07-13--foia--cdot--bicycle-count-data.md) | Ready to send — anchors verified 2026-07-13 |

- **`log.md`** — one row per request: date sent, tracking #, statutory due
  date, status. Update it the day anything is sent or answered.
- **`cdot-counter-crawl.md`** — the six-agent reference crawl behind the
  counter request (52 ranked citations, dead-end list, named contacts).

## Conventions

- Submission channels: GovQA portal (https://www.chicago.gov/publicrecords)
  or the department FOIA email; portal submissions get tracking numbers.
- Chicago publishes requester name + request text in public FOIA logs.
- Statutory clock: 5 business days, one +5 extension. Nudge at +7 business
  days without acknowledgment.
- Responses land in `data/foia/` (create on first receipt), preserving
  original filenames/formats; a "no records" response is itself a result —
  record it in the log and, where it settles a methodology question, in
  DECISIONS.md.
- Every request follows `docs/projects/collaboration-principles.md`: cite
  the specific artifact (no goose chases), offer the open-data path, keep
  the tone collaborative.
