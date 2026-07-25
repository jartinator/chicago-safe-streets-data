# FOIA request log

Tracking every open-records request for this project. One row per request;
full rationale and request bodies live in this folder's per-request files
(see `README.md` for the index).

| # | Date sent | Agency | Contact | Subject | Status | Ref # | Statutory reply due | Follow-up |
|---|-----------|--------|---------|---------|--------|-------|---------------------|-----------|
| 1 | 2026-07-13 | CDOT | GovQA portal | Historical CDOT Bike Lane Mileage Tracker (all versions, source data, GIS install dates) | **Answered 2026-07-24 — granted, records released** | S145367-071326 | 2026-07-20 (+5-day extension taken 2026-07-13) | 4 gaps identified; follow-up request not yet drafted |
| 2 | 2026-07-17 | Office of the City Clerk | GovQA portal | City Council committee records reporting CDOT bikeway/bike-lane mileage | **Response received 2026-07-20** — disposition is in an attached letter (`Base_Template_7202026.pdf`) not yet retrieved from the portal | F145909-071726 | 2026-07-24 | Download the letter and record the disposition (tracker #33) |
| 3 | _(ready to send 2026-07-13 — not yet sent)_ | CDOT | cdotfoia@cityofchicago.org / GovQA portal | Bicycle count data: 2009 count study, 2010–present counts, Chicago/Wells counter records + feed interruption, Replica agreement, 2023 ridership-claims basis | Ready (`docs/outbox/2026-07-13--foia--cdot--bicycle-count-data.md`, anchors verified) | — | 5 business days after send (extendable +5) | +7 business days if no acknowledgment |
| 4 | 2026-07-21 | Dept. of Finance (cc CDOT) | DOFfoia@cityofchicago.org → GovQA | Smart Streets pilot violation-level data (bike/bus lane/bus stop camera enforcement, Nov 2024–present, incl. commercial registrant names + the Tribune production) | **Acknowledged same day**; DOF invoked +5 extension (consultation, 5 ILCS 140/3(e)); CDOT cc closed (not keeper → DOF). Outcome log in the outbox file | F146238-072126 (DOF); S146292-072126 (CDOT, closed) | **2026-08-04** (extension invoked) | Nudge 2026-08-06 if no response |

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

## #1 — outcome (answered 2026-07-24)

**Granted as to items 1, 2, 4, and 5.** No exemptions cited, no fees charged. Released
records are committed under `data/foia/S145367-071326/`; that folder's `README.md` is the
detailed account of what arrived against what was asked, plus the full layer inventory.

The headline: **item 4 was answered.** CDOT's internal bikeway layers carry a per-segment
install year (`INST_YR`, later `BW_INST_YR`) that the public Bike Routes layer omits. And
the Complete Streets program dashboard carries CDOT's own **annual bikeway mileage by
facility type for 2010–2025** — standing network and miles installed per year.

`pipeline/foia_bikeway_history.py` extracts both into `data/cdot_bikeway_history.json`.
Every year's per-category sum reconciles to the total CDOT published in the same sheet.
See `DECISIONS.md` #35 for what this changes about the mileage series.

**Not provided:** item 3 (document version history). Item 6 was optional and moot.

### Gaps worth a follow-up request

1. `2025_Bike Network_internal.shp.zip` ships **without its `.shp`** — 1,008 attribute rows,
   no geometry. Reads like a packaging slip; worth simply asking again.
2. **No GIS layers for 2011–2017.** The series jumps 2010 → 2018.
3. **Annual granularity only** — the individual quarterly tracker snapshots were not produced.
4. **No document version history**, so a figure revised after publication is not detectable.

## On receipt

1. Save returned files under `data/foia/<reference>/records/`, preserving original formats
   and filenames, with a `manifest.json` hashing every released file — including any too
   large to commit. `data/foia/S145367-071326/` is the worked example.
2. If a GIS layer with install dates arrives, it can seed a **retroactive** series — but read
   the survivorship caveat in `foia_bikeway_history.segment_install_years` first: one year's
   layer grouped by install year describes the network that *survived*, not the network as it
   stood in the past.
3. A "no historical versions retained" response is itself a documented result — it confirms the
   forward-only snapshot approach is the only path, and belongs in `DECISIONS.md`.

## Requester identity — standing rule (2026-07-23)

**Default requester is "On Your Left!" (the project), not a personal name.**
Chicago posts requester name + request text in public agency FOIA logs, so
filing personally puts the maintainer's name in a public record every time.
Going forward:

- **The project address exists: `onyourleftopensource@gmail.com`**
  (created 2026-07-23; forwards to the maintainer's personal inbox, and the
  personal Gmail has send-as configured for it). All FOIA correspondence
  uses this address. When sending from Gmail, select the
  onyourleftopensource "From" identity before firing.
- New requests file as the project (organizational requester). Personal
  names appear only where an agency demands a natural person for delivery.
- The three staged letters in `docs/outbox/` were re-headed to the project
  identity on 2026-07-23 — signature "On Your Left!" + the project address.
- Any public template OYL publishes for third parties (the agentic-layer
  "FOIA seed-bank," see `docs/research/agentic-layer/REPORT-agentic-functions.md`)
  defaults to "on behalf of the On Your Left! open-data project" with the
  sender's own delivery details, personal names de-emphasized.

## Notes

- Chicago posts all FOIA requests (requester name + text) in public logs
  (CDOT: chicago.gov/city/en/depts/cdot/dataset/foialog.html; City Clerk: comparable log).
- Sending is done manually by the requester; drafts live in `docs/outbox/`.
- Update the "Date sent," "Status," and "Ref #" columns once each is sent.
- **This table drifts.** Rows 1 and 2 were both recorded as "not yet sent" long after they
  had in fact been filed and answered — caught 2026-07-24 by reconciling against the GovQA
  acknowledgment emails. Reconcile with the mailbox whenever a response lands, not only
  when something is sent.
