# DOF FOIA F146238-072126 — Smart Streets pilot violation data

**Agency:** Chicago Department of Finance
**Sent:** 2026-07-20 (email to `DOFfoia@cityofchicago.org`, cc `cdotfoia@cityofchicago.org`)
**Received by agency:** 2026-07-21
**Acknowledged:** 2026-07-21, with a +5 extension invoked the same day
**Responded:** 2026-07-28 by April Lundberg, FOIA Officer — **seven days early**
**Disposition:** **Granted in part.** 112,318 violation records released. No fee charged.

The request is [`docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md`](../../../docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md).
Background dossier: [`docs/foia/smart-streets-enforcement.md`](../../../docs/foia/smart-streets-enforcement.md).

---

## Read this first: the spreadsheet is not in the repository

`records/FOIA_Meyer_A52294_20260721.xlsx` is **on local disk only**. It is listed in
`.gitignore` and hashed in `manifest.json`, and it must stay out of git.

DOF withheld license plates and addresses. It did **not** withhold owner names. The
release carries `Owner Last Name` and `Owner First Name` for every row, so **82,880 of
the 112,318 rows (73.8%) name a private individual next to the violation they
received**, with the address, date, and time of that violation.

The request had asked for the opposite. It said, in terms:

> I do not object to the redaction of personal identifying information of private
> individual registrants under 5 ILCS 140/7(1)(b)–(c). Business and commercial-fleet
> registrant names are not private information and have already been publicly disclosed
> in press reporting on this program.

So the project asked for business names and volunteered to give up individual ones. DOF
released both. The determination letter never mentions names — it discusses plates and
addresses, and at one point describes redacting "the address of the person who received
each delinquent ticket," language that reads as though it were carried over from a
different kind of request.

**This repository is public.** Committing the file as received would republish 82,880
people's names attached to a traffic violation, on a site none of them have any reason to
expect. The project would be doing to them exactly what its own FOIA letter said should
not be done. Nothing derived from this file gets published until the name columns are
dropped or reduced to an individual/business flag.

This is a decision for the maintainer, not a settled matter. Two things worth weighing:
whether to tell DOF what they released, and whether the local copy should be reduced to a
redacted version immediately rather than kept whole.

---

## What arrived

| File | In repo | What it is |
|---|---|---|
| `records/FOIA Enclosure Meyer 08032026.pdf` | yes | The determination letter |
| `records/FOIA_Meyer_A52294_20260721.xlsx` | **no** | The production — 1 sheet, 112,318 rows, 10 columns |

The PDF filename says `08032026` (August 3) on a letter dated and sent July 28. Treat it
as a template artifact; the letter's own date governs.

### Columns

`Ticket Number`, `Issued Date`, `Location`, `Ward`, `Violation Code`,
`Violation Description`, `Fine Level 1`, `Ticket Queue`, `Owner Last Name`,
`Owner First Name`.

### Coverage

Violations dated **2024-11-06 through 2026-07-18** — the full pilot to date, matching the
requested window.

| Violation description | Rows | Fine |
|---|---:|---:|
| ZERO FINE WARNING - SMRT ST | 80,915 | $0 |
| STND, PARK OR OTHER USE OF BUS LANE - SMRT ST | 10,406 | $90 |
| **PARK/STAND ON BICYCLE PATH - SMRT ST** | **7,856** | **$250** |
| 30 DAY INSTALLATION WARNING - SMRT ST | 4,597 | $0 |
| EXP. METER NON-CENTRAL BUS. DIST. - SMRT ST | 3,725 | $50 |
| PARK OR STAND IN BUS STOP/STAND - SMRT ST | 2,759 | $100 |
| EXP. METER CENTRAL BUS. DIST. - SMRT ST | 2,038 | $70 |
| NON PYMT/NON-COM VEH PARKD COM LDNG ZNE - SMRT ST | 16 | $140 |
| STREET CLEANING - SMRT ST | 6 | $60 |

**85,512 rows (76%) are warnings carrying no fine.** Any "violations" headline that does
not separate warnings from citations will overstate enforcement by roughly four times.

`Ticket Queue` gives disposition: 78,243 Warning, 14,088 Paid, 10,876 Notice, 4,034
Dismissed, 383 Court, 58 Hearing Req, 39 Bankruptcy, 4,597 blank.

**Ward is missing on 7,336 rows (6.5%)**, and only 20 distinct wards appear — consistent
with a geographically limited pilot, but it means ward-level rates need the missing rows
stated, not dropped silently.

---

## What this makes possible

Business and fleet names came through intact. 29,438 rows (26.2%) have a last name but no
first name — the fleet-registrant pattern. On **bicycle path violations specifically**:

| Registrant | Bike-path violations |
|---|---:|
| AMAZON LOGISTICS INC | 649 |
| TRANS ONE INCORPORATED | 192 |
| FEDERAL EXPRESS | 178 |
| UNITED PARCEL SERVICE | 163 |
| NORTHWEST EXPRESS INC | 153 |
| FEDERAL EXPRESS CORP | 142 |
| RYDER TRUCK RENTAL LT | 128 |
| CHICAGO BEVERAGE SYSTEMS | 123 |

This is the company-level attribution the request was built to get, and it is the first
obstruction-adjacent layer the project has held. Note that the same company appears under
several spellings — FEDERAL EXPRESS, FEDERAL EXPRESS CORP, FEDERAL EXPRESS CORPORATION —
so any ranking needs a name-normalization step before it means anything. Rental and
leasing companies (EAN/Enterprise, Hertz, PV Holding) rank high on the all-types list
because the registrant is the lessor, not the driver; they are not comparable to a
delivery fleet and should not sit in the same ranking without a caveat.

---

## What was not provided

- **Item 3 — the data dictionary.** Nothing was supplied. Field meanings are inferred
  from the column headers above. `Fine Level 1` in particular is unexplained: it appears
  to be the initial assessed fine, but whether a "Level 2" escalation exists is unknown.
- **Item 2 — the Tribune production.** Not delivered as a separate document. The
  violation-level data probably subsumes it, but that is an assumption, not a statement
  from DOF.

Both are small enough to be worth a short follow-up, and neither blocks using the data.

## Exemptions claimed

License plates and registrant addresses, under 5 ILCS 140/7(1)(b) (private information,
defined at 2(c-5) to include personal license plates and home addresses) and 7(1)(c)
(unwarranted invasion of personal privacy).

Both are ordinary and correctly applied. Plates are not needed here — the project wanted
company attribution, and company names arrived. **There is no denial worth appealing.**
The PAC review right stated in the letter is noted for the record only.
