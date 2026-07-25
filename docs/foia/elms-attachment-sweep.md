# eLMS attachment sweep — where bikeway mileage reaches City Council

**Run 2026-07-25.** Follows the lead the Office of the City Clerk volunteered when it
denied FOIA `F145909-071726`: eLMS search has a *"search within attachments"* filter that
returns far more than the default. This is that sweep. **No FOIA was needed.**

It settles the question request #2 was filed to answer — *where do the bikeway-mileage
figures CDOT reports to Council actually live?* — and produces two verifiable findings.

---

## The API surface (undocumented, now mapped)

`https://api.chicityclerkelms.chicago.gov/swagger.json` exists and is the authoritative
spec. The Clerk's UI filter maps to a query parameter:

```
GET /search?search=<phrase>&includeAttachments=true&top=500&skip=0
           [&filter=controllingBody eq '<body>']
```

- **`includeAttachments=true` is the whole ballgame.** `bikeway mileage` returns **0**
  results without it and **95** with it. The figures exist only inside attached documents.
- **Quoted strings are phrase matches; unquoted terms OR together.** Unquoted
  `protected bike lane` returns 3,897 rows, top hit a pothole claim for a person named
  *Lane*. Always quote.
- Facets come back empty on attachment searches, so they cannot be used to narrow.
- Attachments themselves are reachable via `/matter/recordNumber/{recordNumber}` →
  `attachments: [{fileName, path, attachmentType}]`, with direct public blob URLs.

Two surfaces exist and they behave differently:

| Surface | Full-text indexed? | Reachable how |
|---|---|---|
| **Matter** attachments | **Yes** | `/search?includeAttachments=true` |
| **Meeting** files (agendas, notices, summaries) | **No** | `/meeting?filter=body eq '…'` → `files[]` |

---

## Finding 1 — the transportation committees hold no mileage records at all

Swept both committees named in FOIA #2, across **394 meetings and 1,378 files**
(2010-12-06 → 2026-07-14):

| attachmentType | count |
|---|---|
| Notice | 401 |
| Agenda | 396 |
| Summary | 355 |
| Other | 207 |
| Monthly Rule 45 | 19 |

The `Other` bucket looked like the place a presentation deck would hide. It is not: all
207 are superseded versions of the same paperwork — *"Original Agenda"*, *"Revised
Notice"*, *"Original Summary"*. **Not one presentation, handout, or exhibit.**

Matter attachments tell the same story. Every mileage phrase returns **0** when filtered
to either committee, even where it returns hits citywide:

| phrase | citywide | P&TS | T&PW |
|---|---|---|---|
| `"protected bike lane"` | 16 | 0 | 0 |
| `"Complete Streets"` | 32 | 0 | 0 |
| `"miles of protected bike lanes"` | 1 | 0 | 0 |
| `"bike lane mileage"` | 0 | 0 | 0 |
| `"bikeway mileage"` | 0 | 0 | 0 |

**This independently corroborates the Clerk's denial.** The Clerk said it does not hold
CDOT's program records; the record system confirms nothing of the kind was ever filed
with these committees. Request #2 could not have succeeded against any office — the
records do not exist in Council's system. That is a documented dead end, not a refusal.

---

## Finding 2 — mileage reaches Council through the annual Budget Overview

Of 56 distinct matters whose attachments mention bike-facility phrases (2011–2025),
**52 sit under "City Council"** rather than any committee — which is exactly why the
committee-filtered searches came back empty.

The explicit *miles* claims live in the annual budget documents:

### `O2015-6370` — Budget Overview for Year 2016

> "The City is on track to complete the first 100 miles of protected bike lanes before the
> end of 2015 with more lanes to be completed in 2016."

> "By 2019, the City plans to add an additional 50 miles of protected bike lanes."

### `O2022-3024` — Budget Overview for Year 2023

> "Added 45 miles of new bike lanes, surpassing Mayor Lightfoot's goal of 100 new miles in
> her first term."

(`R2011-637`, the Daley retirement resolution, also matches `"miles of bike lanes"` — as
biography, not reporting.)

---

## Checking those claims against CDOT's own numbers

Now possible because FOIA `S145367-071326` produced CDOT's own year-by-year figures
(`data/cdot_bikeway_history.json`). Both sides of each comparison are the City's own data.

**1. "The first 100 miles of protected bike lanes" by end of 2015 — only by counting
buffered lanes.**

| CDOT's 2015 figures | miles |
|---|---|
| Protected bike lane | **21.35** |
| Protected + buffered | **108.35** |

The claim is reachable only if buffered lanes count as protected. They are not the same
facility, and CDOT's own dashboard lists them separately — and does not count buffered as
low-stress (see `DECISIONS.md` #37). Protected-only delivery was **21%** of the claim.

**2. "By 2019, an additional 50 miles of protected bike lanes" — missed on any reading.**

| basis | 2015 | 2019 | added |
|---|---|---|---|
| Protected only | 21.35 | 24.30 | **+2.95** |
| Protected + buffered | 108.35 | 131.80 | +23.45 |

Against a 50-mile pledge: **6%** delivered on the protected-only basis, 47% even on the
generous one.

**3. "100 new miles in her first term" — this one holds up.**

CDOT installed **121.36** on-street miles across 2019–2022. Excluding the 4.33 miles of
concrete upgrades to existing protected lanes (the counting issue in `DECISIONS.md` #36),
**117.03 miles** are genuinely new. The claim is substantiated on either basis. The
companion "added 45 miles" matches 2021 alone (44.23 mi).

Two claims do not survive contact with the city's own spreadsheet; one does. Recording all
three is the point.

---

## Coverage limits

- **eLMS committee meetings start 2010-12-06**, and the two committees' own records begin
  2018-01-11 (P&TS) and 2018-12-05 (T&PW). Anything earlier lives in the Legistar era
  (`LEGISTAR_DATA_FROZEN_AT`, 2023-06-21 boundary — see `config.py`).
- Meeting files are **not** full-text indexed. Finding 1 rests on filename and
  attachment-type metadata across all 1,378 files, not on reading each PDF. A presentation
  filed under a meaningless name (`DOC042.pdf`) would not surface by name — though the
  complete absence of any non-procedural `attachmentType` makes that unlikely.
- Phrase search only finds the phrasings tried. The list used is in this document's
  methodology above; a document saying "X centerline miles of low-stress network" without
  any tried phrase would be missed.

## Not done here

The two failed claims are **published commitments with citations and now-measurable
delivery** — the same shape as the entries in `data/commitments.json`. Adding them would
extend the promise-vs-delivered ledger backward past the 2023 Cycling Strategy. That is a
deliberate editorial decision about publishing findings on a former administration, so it
is flagged rather than taken unilaterally.
