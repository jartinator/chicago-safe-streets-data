# FOIA requests — index

All open-records work lives in this folder: per-request rationale/dossier
files, the supporting research, and the log. **Send-ready request bodies
live in `docs/outbox/`** (one file per outbound message, front-matter
tracked) — this folder links to them.

| Request | File | Status |
|---|---|---|
| CDOT historical Bike Lane Mileage Tracker | `cdot-bikeway-mileage-history.md` → records in [`data/foia/S145367-071326/`](../../data/foia/S145367-071326/README.md) | **Answered 2026-07-24 — granted** (S145367-071326). 2010–2025 annual series + per-segment install dates recovered |
| City Clerk fallback — Council records reporting bikeway mileage | `cdot-bikeway-mileage-history.md` → letter in [`data/foia/F145909-071726/`](../../data/foia/F145909-071726/README.md) | **Answered 2026-07-20 — denied**, no responsive records (Clerk is not the keeper). Moot: the CDOT request above was granted in full |
| CDOT follow-up — gaps in the S145367-071326 release (missing 2025 `.shp`, 2011–2017 layers, quarterly snapshots, file metadata) | [`docs/outbox/2026-07-25--foia--cdot--bikeway-history-gaps.md`](../outbox/2026-07-25--foia--cdot--bikeway-history-gaps.md) | Ready to send — item 1 stands alone; 2–4 optional |
| CDOT bicycle count data (2009 study, counters, Replica, 2023 ridership claims) | [`docs/outbox/2026-07-13--foia--cdot--bicycle-count-data.md`](../outbox/2026-07-13--foia--cdot--bicycle-count-data.md) | Ready to send — anchors verified 2026-07-13 |
| DOF/CDOT Smart Streets enforcement data (bike/bus lane camera violations, commercial fleet attribution) | `smart-streets-enforcement.md` → [`docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md`](../outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md) | **Sent + acknowledged 2026-07-21** (DOF F146238-072126, +5 extension) — response due 2026-08-04 |

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
- Responses land in `data/foia/<reference>/records/`, preserving original
  filenames/formats, with a `manifest.json` hashing every released file —
  including any excluded from git for size, so the omitted originals stay
  verifiable. `data/foia/S145367-071326/` is the worked example. A "no
  records" response is itself a result — record it in the log and, where it
  settles a methodology question, in DECISIONS.md.
- Every request follows `docs/projects/collaboration-principles.md`: cite
  the specific artifact (no goose chases), offer the open-data path, keep
  the tone collaborative.
