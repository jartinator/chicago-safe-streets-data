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

**Both open questions were settled 2026-07-29.**

1. **DOF will be told.** A courtesy notice is drafted and ready to send at
   [`docs/outbox/2026-07-29--foia--dof--individual-names-over-release-notice.md`](../../../docs/outbox/2026-07-29--foia--dof--individual-names-over-release-notice.md).
   It reports the fact, states that the project is not publishing the names, and asks for
   nothing.
2. **A redacted derivative exists.** `pipeline/foia_smart_streets.py` reads the workbook
   and writes [`data/smart_streets_violations.csv`](../../smart_streets_violations.csv) —
   112,318 rows, no individual names. **That CSV is the only form anything downstream may
   read.** The original stays local and whole, as the provenance record: it is what proves
   what DOF actually sent, and re-requesting it would restart the clock.

### How the redaction decides

Names survive only for confirmed organizations, and the default is redaction:

| Class | Rows | Name kept |
|---|---:|:--:|
| `business` — no first name, and an explicit token (`INC`, `LLC`, `TRUST`, `RENTAL`, …) | 27,549 | yes |
| `individual` — any row with a first name | 82,880 | no |
| `unknown` — no first name, no recognizable token | 1,889 | no |

`unknown` is redacted deliberately. Getting it wrong in that direction costs one data
point; getting it wrong the other way publishes somebody's name. The script asserts that
no non-business row carries a name and refuses to write the file if that ever fails.

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

Counted on `registrant_normalized`, which folds legal suffixes and fleet numbers so that
FEDERAL EXPRESS, FEDERAL EXPRESS CORP, and FEDERAL EXPRESS 225877 are one fleet:

| Registrant | Bike-path violations |
|---|---:|
| AMAZON LOGISTICS | 661 |
| FEDERAL EXPRESS | 517 |
| UNITED PARCEL SERVICE | 278 |
| TRANS ONE | 193 |
| CHICAGO BEVERAGE SYSTEMS | 190 |
| RYDER TRUCK RENTAL | 164 |
| NORTHWEST EXPRESS | 153 |
| CITY BEVERAGE ILLINOIS | 103 |

This is the company-level attribution the request was built to get, and the first
obstruction-adjacent layer the project has held.

**Rank on `registrant_normalized`, never on `registrant`.** The raw field splits one fleet
across dozens of strings, and any ranking built on it understates the largest operators
most — which is the opposite of the error you want.

**Leasing companies are not fleets.** Ryder, Penske, Enterprise, Hertz, and PV Holding
rank high because the registered owner is the *lessor*, not whoever was driving. They rank
even higher on the all-types list. Publishing them beside Amazon and FedEx without saying
so would assert something the data does not support.

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
