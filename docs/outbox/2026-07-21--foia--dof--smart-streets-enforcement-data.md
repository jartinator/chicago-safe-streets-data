---
status: answered
initiative: foia
to: DOFfoia@cityofchicago.org (cc cdotfoia@cityofchicago.org; or GovQA portal: chicago.gov/publicrecords → Finance)
subject: FOIA request — Smart Streets pilot violation data (bike/bus lane camera enforcement)
drafted: 2026-07-21
sent: 2026-07-21
tracking: F146238-072126 (DOF); cc spawned CDOT S146292-072126, closed same day (not keeper → referred to DOF)
answered: 2026-07-28
tracker: #33
---

> **Answered 2026-07-28 — records released, not yet reviewed.**
>
> April Lundberg, DOF FOIA Officer (`April.Lundberg@cityofchicago.org`,
> 312-742-7150), replied directly to the original email rather than through
> GovQA, with two attachments:
>
> - `FOIA Enclosure Meyer 08032026.pdf` — the determination letter
> - `FOIA_Meyer_A52294_20260721.xlsx` — the data production
>
> That is **seven days ahead** of the extended 2026-08-04 deadline, which is
> unusually fast for a request this broad.
>
> **Neither file has been downloaded or opened.** Treat everything about the
> outcome as unknown until they are. The question that decides whether this
> becomes a real data layer: did **commercial registrant names** survive, or did
> DOF redact them under 7(1)(b)–(c) despite the letter pre-arguing that business
> names are not private and were already public via the Tribune? If they were
> withheld, that is the PAC-review decision point, and the 60-day window for a
> Public Access Counselor request starts from the determination letter's date.
>
> Intake goes to `data/foia/F146238-072126/records/` per the "On receipt" steps
> in `docs/foia/log.md`. Downstream plan:
> `docs/superpowers/plans/2026-07-21-smart-streets-enforcement-integration.md`.

# FOIA request: Smart Streets enforcement data (DOF, cc CDOT)

**How to submit:**
- Online portal (GovQA): https://www.chicago.gov/publicrecords → Department
  of Finance — auto-assigns a tracking number; or
- Email the body below to **DOFfoia@cityofchicago.org**, cc
  **cdotfoia@cityofchicago.org** (DOF administers Smart Streets citations;
  CDOT co-owns the program — the cc forestalls a "wrong department" bounce).

Statutory response: 5 business days, extendable +5. Chicago publishes all
FOIA requests (requester name + request text) in its public FOIA logs
(Finance log dataset: `7avf-ek45`). Log the filing in `docs/foia/log.md`
with date and tracking number.

*Verification status (2026-07-21): anchors checked — see the checklist at
the bottom. One open item: the DOF FOIA email was found via search
(chicago.gov is unreachable from this build environment); confirm it on
https://www.chicago.gov/city/en/depts/fin/supp_info/fin_foia.html before
sending, or just use the GovQA portal, which needs no email.*

**SENT 2026-07-21** via Gmail (from the draft prepared the same day).
See the Outcome log at the bottom of this file — both departments
acknowledged same-day via GovQA; DOF invoked a +5 extension, **response
due 2026-08-04**; nudge 2026-08-06 if nothing. See `docs/foia/log.md`
row 4.

---

To: FOIA Officer, Chicago Department of Finance
Cc: FOIA Officer, Chicago Department of Transportation

Re: Freedom of Information Act request — Smart Streets pilot program
violation data

Dear FOIA Officer,

Under the Illinois Freedom of Information Act, 5 ILCS 140, I request copies
of the following records of the Smart Streets pilot program (the automated
camera enforcement of bike lane, bus lane, and bus stop violations
authorized by the Smart Streets Pilots ordinance passed by City Council on
March 15, 2023, and administered by the Department of Finance with the
Department of Transportation). Each item is independent — a partial
response is welcome, and for any dataset an export of the existing database
or spreadsheet in its native structured format (CSV or Excel, not scanned
images or PDFs of records) is preferable to any newly created document.

1. Violation-level records of all warnings and citations issued under the
   Smart Streets pilot from November 1, 2024 through the date this request
   is processed, including for each record, as maintained: date and time of
   violation; location (address, block, or intersection); violation type
   (bike lane, bus lane, or bus stop); whether a warning or a citation was
   issued; fine amount assessed and disposition/payment status; the name of
   the registered owner for vehicles registered to businesses or commercial
   fleets; and ward or any other geographic identifier maintained.

2. The compiled dataset or summary of Smart Streets violations by vehicle
   owner that was produced in response to the records request underlying
   the Chicago Tribune's July 19, 2026 report on delivery-company fines
   (Amazon Logistics, FedEx, UPS). As this production has already been
   compiled and released, I request a copy of the same records.

3. The data dictionary, field list, or record layout for the citation
   database as it pertains to Smart Streets violations, sufficient to
   interpret the fields in item 1.

To expedite processing: I do not object to the redaction of personal
identifying information of private individual registrants under 5 ILCS
140/7(1)(b)–(c). Business and commercial-fleet registrant names are not
private information and have already been publicly disclosed in press
reporting on this program.

I request a waiver of fees under 5 ILCS 140/6: this request is made for
noncommercial purposes in connection with an open-source, publicly
available civic project ("On Your Left!") that publishes Chicago bike-safety
data for public benefit, and disclosure serves the public interest.

Separately from this request: if Smart Streets violation data is something
the City would consider publishing on the Data Portal on an ongoing basis —
as it already does for the older Speed Camera Violations and Red-Light
Camera Violations datasets — we would enthusiastically use and publicize
it, and a recurring portal dataset would spare your office future one-off
requests like this one.

Electronic delivery to the email below is preferred.

Sincerely,
[NAME]
[EMAIL]
[optional: postal address / phone]

---

## Verification checklist — 2026-07-21

- [x] **No portal dataset** — web search for Chicago Data Portal "Smart
  Streets" / bus-bike lane camera datasets finds none (direct Socrata
  catalog queries are egress-blocked from this environment; recheck at
  data.cityofchicago.org before sending is cheap and optional). The
  existing Speed Camera (`hhkd-xvj4`) / Red-Light (`spqx-js37`) datasets
  are the older fixed-camera system, not Smart Streets.
- [x] **Ordinance** — Smart Streets Pilots ordinance passed City Council
  2023-03-15 (chicago.gov CDOT news release "City Council Passes Smart
  Streets Ordinance…", March 2023; Streetsblog Chicago 2023-03-15).
  Introduced January 2023 by Mayor Lightfoot with Ald. Hopkins, La Spata,
  Martin, Reilly, Vasquez.
- [x] **Program mechanics** — warnings began 2024-11-04; citations began
  December 2024; cameras on 8 DOF parking-enforcement vehicles, expanded
  October 2025 to 6 CTA buses (Hayden AI ABLE units on routes #66/#36);
  pilot zone Roosevelt–North Ave–Ashland–Lake Michigan; fines $90 (bus
  lane) / $250 (bike lane); pilot currently set to expire December 2026.
  Sources: chicago.gov press releases (Oct 2024, Oct 2025), CBS Chicago,
  Block Club Chicago 2024-11-04.
- [x] **Tribune report exists & figures** — July 2026 Tribune report:
  Amazon Logistics + FedEx + UPS charged a combined ~$460,000 for bus
  stop/bus lane/bike lane violations Nov 2024–early May 2026; ~$2.6M in
  fines program-wide; ~44,390 total warnings+violations. Corroborated via
  Wirepoints' summary of the Tribune/Yahoo syndication and Streetsblog
  Chicago ("Stay in your lane or pay the fine," 2026-01-28).
- [x] **Tribune got its numbers via a records request**, not an open
  dataset — which is exactly what item 2 leverages (already-compiled
  production, no burden argument).
- [x] **No prior public release found** — no MuckRock or other posted
  Smart Streets data extract surfaced in searches.
- [x] **DOF FOIA email** — `DOFfoia@cityofchicago.org` per search results;
  chicago.gov unreachable from this environment to confirm directly.
  RESOLVED 2026-07-21: the address works — DOF acknowledged with tracking
  # F146238-072126 (see Outcome log).

## Outcome log

- **2026-07-21 (send):** emailed to DOFfoia@cityofchicago.org, cc
  cdotfoia@cityofchicago.org. Both departments routed it into the GovQA
  Records Center — so the "verify the DOF email" open item resolved
  itself: the address works and email submissions get tracking numbers
  after all.
- **2026-07-21 (DOF acknowledgment):** request received, reference
  **F146238-072126**. Same day, DOF invoked the +5-business-day extension
  under 5 ILCS 140/3(e), checking the "consultation with another public
  body" reason — consistent with DOF needing to coordinate with CDOT
  and/or Hayden AI on the violation data. **Response due 2026-08-04.**
  Signed April Lundberg, Department of Finance.
- **2026-07-21 (CDOT):** the cc was opened as its own request
  (**S146292-072126**) and closed the same day: CDOT "is not the keeper
  of the requested information… the most likely keeper is the Department
  of Finance," citing Duncan Publishing v. City of Chicago (each
  department is a separate public body). Expected and harmless — the cc
  did its job (no wrong-door bounce at DOF; DOF is processing on the
  merits). Signed G. Rubenstein, CDOT FOIA Officer.
- **Next checkpoint:** if nothing arrives by **2026-08-06**, send the
  polite nudge on F146238-072126 (a session can draft it here).
