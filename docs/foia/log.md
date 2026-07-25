# FOIA request log

Tracking every open-records request for this project. One row per request;
full rationale and request bodies live in this folder's per-request files
(see `README.md` for the index).

| # | Date sent | Agency | Contact | Subject | Status | Ref # | Statutory reply due | Follow-up |
|---|-----------|--------|---------|---------|--------|-------|---------------------|-----------|
| 1 | 2026-07-13 | CDOT | GovQA portal | Historical CDOT Bike Lane Mileage Tracker (all versions, source data, GIS install dates) | **Answered 2026-07-24 — granted, records released** | S145367-071326 | 2026-07-20 (+5-day extension taken 2026-07-13) | Follow-up drafted → row 5 |
| 2 | 2026-07-12 (received by agency 07-13) | Office of the City Clerk | clerkfoia@cityofchicago.org → GovQA | City Council committee records reporting CDOT bikeway/bike-lane mileage | **Answered 2026-07-20 — denied, no responsive records** (Clerk is not the keeper; redirected to the department and to eLMS / Journals of Proceedings) | F145909-071726 | 2026-07-20 (met) | None. #1 was granted in full, so the fallback is moot |
| 3 | _(ready to send 2026-07-13 — not yet sent)_ | CDOT | cdotfoia@cityofchicago.org / GovQA portal | Bicycle count data: 2009 count study, 2010–present counts, Chicago/Wells counter records + feed interruption, Replica agreement, 2023 ridership-claims basis | Ready (`docs/outbox/2026-07-13--foia--cdot--bicycle-count-data.md`, anchors verified) | — | 5 business days after send (extendable +5) | +7 business days if no acknowledgment |
| 4 | 2026-07-21 | Dept. of Finance (cc CDOT) | DOFfoia@cityofchicago.org → GovQA | Smart Streets pilot violation-level data (bike/bus lane/bus stop camera enforcement, Nov 2024–present, incl. commercial registrant names + the Tribune production) | **Acknowledged same day**; DOF invoked +5 extension (consultation, 5 ILCS 140/3(e)); CDOT cc closed (not keeper → DOF). Outcome log in the outbox file | F146238-072126 (DOF); S146292-072126 (CDOT, closed) | **2026-08-04** (extension invoked) | Nudge 2026-08-06 if no response |
| 5 | **2026-07-25** (Sat — agency receipt expected Mon 07-27) | CDOT | cdotfoia@cityofchicago.org → GovQA | Follow-up to S145367-071326: the 2025 layer's missing `.shp`, plus 2011–2017 layers, quarterly snapshots, and dashboard file metadata (items 2–4 optional) | **Sent** — awaiting acknowledgment. First request filed as the project (`onyourleftopensource@gmail.com`) | — (pending) | ~**2026-08-03** (5 business days from expected 07-27 receipt; +5 extension → ~08-10) | Nudge **2026-08-05** if no acknowledgment |

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

### Gaps worth a follow-up request — drafted, see row 5

Drafted 2026-07-25 as `docs/outbox/2026-07-25--foia--cdot--bikeway-history-gaps.md`.
Item 1 is written to stand alone; items 2–4 each carry an explicit drop-it line so the
whole thing can be answered in minutes if CDOT only wants to fix the packaging slip.

1. `2025_Bike Network_internal.shp.zip` ships **without its `.shp`** — 1,008 attribute rows,
   no geometry, while every other year arrived complete. Reads like a packaging slip; the
   follow-up leads with it and asks for nothing else as a hard requirement.
2. **No GIS layers for 2011–2017.** The series jumps 2010 → 2018. Asked as optional, with
   "not retained" named up front as a complete answer.
3. **Annual granularity only** — the quarterly tracker snapshots were not produced. Narrowed
   to *saved files that already exist*; explicitly not a request to reconstruct figures.
4. **No document version history.** Narrowed from the original item 3 to just the
   created/modified/author metadata for `CompleteStreets_Dashboard.xlsx` — enough to state
   how current a cited figure was, and answerable from a properties pane.

The letter also carries the standing open-data off-ramp (collaboration principle 3):
publishing the `BW_INST_YR` / `BW_INST_MO` columns CDOT already maintains onto the public
Bike Routes layer (`hvv9-38ut`) would retire most future requests of this kind.

## #2 — outcome (answered 2026-07-20)

**Denied: no responsive records.** The Office of the City Clerk is not the office that
maintains these records — each City department is a separate "public body" under
5 ILCS 140/2(a) (*Duncan Publishing v. City of Chicago*, 304 Ill. App. 3d 778, 784), so the
request had to go to CDOT, which is where the parallel request already went. #1 was granted
in full four days later, so **this fallback is moot and needs no appeal.** The denial rests
on the law rather than evasion, arrived inside the statutory window, and came with a
concrete redirect; no PAC review is warranted.

The letter is committed at `data/foia/F145909-071726/`.

**The lead was followed — 2026-07-25. See `elms-attachment-sweep.md`.** The Clerk's
"search within attachments" tip maps to `includeAttachments=true` on the undocumented eLMS
`/search` API, and it is decisive: `bikeway mileage` returns 0 results without it and 95
with it. Two findings, no FOIA required:

1. **The denial is independently corroborated.** Across 394 committee meetings and 1,378
   files (2010–2026), there is not one presentation, handout, or exhibit — only notices,
   agendas, summaries, and their superseded versions. Every mileage phrase returns 0 when
   filtered to either committee. Request #2 could not have succeeded against any office;
   the records are not in Council's system at all.
2. **Mileage reaches Council through the annual Budget Overview**, filed under "City
   Council" rather than any committee — which is why committee-filtered searches came back
   empty. `O2015-6370` (Budget 2016) claims "the first 100 miles of protected bike lanes"
   by end of 2015; CDOT's own FOIA'd figures put protected at **21.35 mi**, reaching 108.35
   only if buffered lanes are counted as protected. Its "additional 50 miles of protected
   by 2019" delivered **+2.95 mi**. A third claim — 100 new miles in Lightfoot's first term
   — does hold up (117.03 genuinely new miles, 2019–2022).

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
- **In force as of 2026-07-25.** Row 5 is the first request actually sent
  under the project identity. Rows 1–4 predate the rule, so the
  maintainer's personal name is what appears in Chicago's public FOIA logs
  for those; nothing can be done about that retroactively.
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
