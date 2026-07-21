# Smart Streets enforcement data — request dossier

**Request body:** [`docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md`](../outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md)
**Status:** ready to send (Gmail draft prepared 2026-07-21) — see `log.md` row 4.
**Target layer:** first real (non-mock, non-proxy) obstruction-adjacent
dataset — see the "Smart Streets Enforcement (pending FOIA)" card on the
Data Sources page and the planned contract in `SCHEMA.md`.

## What this is

Chicago's **Smart Streets pilot** (CDOT + Department of Finance, camera
tech by Hayden AI) automatically tickets vehicles stopped in bike lanes,
bus lanes, and bus stops in a downtown pilot zone (Roosevelt–North
Ave–Ashland–Lake Michigan). Warnings began 2024-11-04, citations
December 2024; October 2025 added ABLE camera units on 6 CTA buses
(routes #66/#36). Fines: $250 bike lane, $90 bus lane. Pilot currently
authorized through December 2026.

The Chicago Tribune (2026-07-19) obtained violation data via a records
request and reported ~$460K in combined fines to Amazon Logistics, FedEx,
and UPS (Nov 2024–early May 2026), ~$2.6M program-wide, ~44,390
warnings+violations to date.

## Why we want it

- **Enforcement-grade obstruction signal.** Every record is a
  camera-verified vehicle in a bike/bus lane — not self-reported like 311,
  not synthetic like the mock obstruction layer. It would be the
  project's first real-tier obstruction-adjacent dataset.
- **Company-level attribution.** Commercial-fleet registrant names
  (Amazon Logistics, FedEx, UPS…) are in the data and already publicly
  disclosed via the Tribune — rare, high-value for the accountability
  angle Bike Lane Uprising works, and credible in alderman conversations.
- **Fits existing schemas.** Records project cleanly into the normalized
  obstruction schema (`obstruction_type: vehicle_in_lane/delivery_vehicle`,
  `company_name`, `occurred_at`) that `SCHEMA.md` already declares
  swappable-in, and/or a first-class enforcement layer (planned contract
  in `SCHEMA.md`).

## Sourcing verification (2026-07-21)

Full checklist with sources at the bottom of the outbox file. Summary:

| Claim | Verdict |
|---|---|
| No Chicago Data Portal dataset for Smart Streets | ✅ none found (search-verified; direct Socrata catalog is egress-blocked here). Speed Camera `hhkd-xvj4` / Red-Light `spqx-js37` are the older fixed-camera system, distinct from Smart Streets |
| Tribune 2026-07-19 report, $460K / $2.6M figures | ✅ corroborated (Wirepoints summary of Tribune/Yahoo; Streetsblog 2026-01-28) |
| Tribune's numbers came from a records request, not an API | ✅ — leveraged in item 2 of the letter (already-compiled production) |
| Ordinance passed March 2023 | ✅ 2023-03-15 (chicago.gov news release; Streetsblog) |
| Citation lookup page is per-ticket only, not bulk | ✅ (chicago.gov Finance Smart Streets page) |
| Prior FOIA extract already posted (MuckRock etc.) | ❌ none found — a fresh request is needed |

## Fallback ladder (if denied or slow)

1. **Statutory clock:** 5 business days + one 5-day extension; nudge at
   +7 business days without acknowledgment (standard program cadence).
2. **Tribune data team outreach.** Ask the reporter/data team whether
   they'll share the underlying extract informally for civic-tech/
   open-source use — many outlets will. If it comes to that, draft the
   outreach as a new `docs/outbox/` file (initiative `foia` is wrong for
   it — use a partnership-style key or add one to the registry).
3. **Static digitization.** Hand-enter the aggregate figures reported in
   the article ($460K commercial-fleet total, $2.6M program-wide,
   warning/violation counts) as an article-sourced static stat on the
   findings/dashboard side — clearly labeled derived-from-reporting, not
   geocoded, never a mappable layer.
4. **Re-request at pilot end.** The pilot's current authorization runs
   through December 2026 — a wrap-up request in early 2027 captures the
   complete pilot dataset.

## On receipt

Follow `docs/foia/README.md` conventions (`data/foia/`, original
filenames/formats), then the integration plan:
`docs/superpowers/plans/2026-07-21-smart-streets-enforcement-integration.md`.
