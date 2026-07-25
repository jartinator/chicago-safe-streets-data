# City Clerk FOIA F145909-071726 — Council records reporting bikeway mileage

**Agency:** Chicago Office of the City Clerk
**Sent:** 2026-07-12 (email to `clerkfoia@cityofchicago.org`)
**Received by agency:** 2026-07-13
**Acknowledged:** 2026-07-17 (GovQA)
**Responded:** 2026-07-20 by Lori Probasco
**Disposition:** **Denied — no responsive records.** The Clerk is not the record keeper.

This was the fallback/corroboration request behind
[`docs/foia/cdot-bikeway-mileage-history.md`](../../../docs/foia/cdot-bikeway-mileage-history.md):
it existed to backstop CDOT request `S145367-071326` if CDOT claimed it did not retain
historical tracker versions. **CDOT granted that request in full on 2026-07-24**, so this
denial costs the project nothing.

No records were released. The response letter is itself the result, and is kept at
`records/Base_Template_7202026.pdf`.

## What the Clerk said

Three points, paraphrased:

1. **Not the keeper.** The Office has no responsive documents because it is not the office
   that maintains them. Each City department is a separate "public body" under
   [5 ILCS 140/2(a)], citing *Duncan Publishing, Inc. v. City of Chicago*, 304 Ill. App. 3d
   778, 784 (1st Dist. 1999). A request must go to the department holding the records —
   i.e. CDOT, which is where the parallel request already went.
2. **Complete Streets reports are in eLMS.** `https://chicityclerkelms.chicago.gov/` —
   and the letter volunteers a search tip: open the filter panel and enable
   **"search within attachments"** for a more complete result. Searching "bike lanes" and
   similar terms is suggested.
3. **The Clerk does not maintain committee minutes.** Journals of Proceedings live at
   `https://www.chicityclerk.com/legislation-records/journals-and-reports/journals-proceedings`
   and are text-searchable.

The letter closes by asserting that the online availability of these records satisfies
FOIA's public-disclosure requirement, and gives the standard Public Access Counselor
review notice.

## Worth following up on

The **"search within attachments"** filter is a genuine lead, not boilerplate. This repo
already pulls eLMS (`config.ELMS_API_URL`, `pipeline/pull_agenda_items.py`) but works from
matter records and agenda PDFs. A full-text search *inside* meeting attachments is a
different surface, and it is where CDOT's committee presentations — the exact documents
this request asked for — would surface if they exist anywhere public.

**Followed 2026-07-25 — see [`docs/foia/elms-attachment-sweep.md`](../../../docs/foia/elms-attachment-sweep.md).**
The tip maps to `includeAttachments=true` on the eLMS `/search` API and is decisive
(`bikeway mileage`: 0 results without it, 95 with it). The sweep **corroborates this
denial independently**: across 394 committee meetings and 1,378 files there is not one
presentation or exhibit, and every mileage phrase returns 0 when filtered to either
committee. The records were never filed with Council. It also found where the figures
*do* surface — the annual Budget Overview, filed under "City Council" — and two claims
there that CDOT's own FOIA'd numbers do not support.

## Note on the denial

The denial looks correct on the law rather than evasive: the Clerk genuinely does not hold
CDOT's program records, and the response arrived inside the statutory window (received
07-13, answered 07-20) with a concrete redirect rather than a bare refusal. No PAC review
is warranted.
