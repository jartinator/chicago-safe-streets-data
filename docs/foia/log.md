# FOIA request log

Tracking every open-records request for this project. One row per request;
full rationale and request bodies live in this folder's per-request files
(see `README.md` for the index).

| # | Date sent | Agency | Contact | Subject | Status | Ref # | Statutory reply due | Follow-up |
|---|-----------|--------|---------|---------|--------|-------|---------------------|-----------|
| 1 | _(draft prepared 2026-07-12 — not yet sent)_ | CDOT | CDOTfoia@cityofchicago.org | Historical CDOT Bike Lane Mileage Tracker (all versions, source data, GIS install dates) | Ready in outbox (reconcile w/ Gmail) | — | 5 business days after send (extendable +5) | +7 business days if no acknowledgment |
| 2 | _(draft prepared 2026-07-12 — not yet sent)_ | Office of the City Clerk | clerkfoia@cityofchicago.org | City Council committee records reporting CDOT bikeway/bike-lane mileage | Ready in outbox (reconcile w/ Gmail) | — | 5 business days after send (extendable +5) | +7 business days if no acknowledgment |
| 3 | _(ready to send 2026-07-13 — not yet sent)_ | CDOT | cdotfoia@cityofchicago.org / GovQA portal | Bicycle count data: 2009 count study, 2010–present counts, Chicago/Wells counter records + feed interruption, Replica agreement, 2023 ridership-claims basis | Ready (`docs/outbox/2026-07-13--foia--cdot--bicycle-count-data.md`, anchors verified) | — | 5 business days after send (extendable +5) | +7 business days if no acknowledgment |
| 4 | 2026-07-21 | Dept. of Finance (cc CDOT) | DOFfoia@cityofchicago.org | Smart Streets pilot violation-level data (bike/bus lane/bus stop camera enforcement, Nov 2024–present, incl. commercial registrant names + the Tribune production) | **Sent** — awaiting acknowledgment (`docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md`) | — (email; none assigned yet) | 2026-07-28 (extendable to 2026-08-04) | Nudge 2026-07-30 if no acknowledgment |

## What each request seeks

- **#1 (CDOT) — primary.** Every version of the mileage tracker, the source spreadsheet/database,
  file version history/timestamps, and — highest value — a **GIS bikeway layer with per-segment
  install dates** (would allow retroactive reconstruction of the full quarterly series). Plus
  annual/quarterly miles-installed figures with backup calculations.
- **#2 (City Clerk) — fallback/corroboration.** Bikeway-mileage figures CDOT presented to the
  Committee on Pedestrian and Traffic Safety and the Committee on Transportation and Public Way
  (presentations, annual reports to Council, minutes), 2015–present. Backstops #1 if CDOT claims it
  does not retain old tracker versions.
- **#4 (DOF, cc CDOT) — Smart Streets enforcement data.** Violation-level records of the bike/bus
  lane camera enforcement pilot (date/time, location, type, warning vs. citation, fine, commercial
  registrant name, ward), plus a copy of the already-compiled production behind the Tribune's
  2026-07-19 delivery-company-fines report and the data dictionary. Would be the project's first
  real-tier obstruction-adjacent layer, with company-level attribution. Dossier:
  `smart-streets-enforcement.md`; integration plan:
  `docs/superpowers/plans/2026-07-21-smart-streets-enforcement-integration.md`.

## On receipt

1. Save returned files under `data/snapshots/` (if dated network layers) or a new
   `data/foia/` directory, preserving original formats and filenames.
2. If a GIS layer with install dates arrives, it can seed a **retroactive** per-quarter series —
   feed it into `build_bikeway_mileage_series()` / `infra_growth_trend()` (see the plan in
   `docs/superpowers/plans/`).
3. A "no historical versions retained" response is itself a documented result — it confirms the
   forward-only snapshot approach is the only path, and belongs in `DECISIONS.md`.

## Notes

- Chicago posts all FOIA requests (requester name + text) in public logs
  (CDOT: chicago.gov/city/en/depts/cdot/dataset/foialog.html; City Clerk: comparable log).
- Both drafts were prepared in Gmail; sending is done manually by the requester.
- Update the "Date sent," "Status," and "Ref #" columns once each is sent.
