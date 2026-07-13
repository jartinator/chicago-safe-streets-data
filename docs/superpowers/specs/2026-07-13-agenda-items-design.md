# Agenda-item extraction & context — design

**Date:** 2026-07-13
**Goal:** committee meeting agendas are linked as PDFs on the action page. People
deciding whether to attend need to know *what's on the agenda* — and an agenda
line like "approval of O2026-0025394" needs context (what is that ordinance,
who filed it, what ward does it touch) before it means anything.

## What we verified live (2026-07-13)

1. **Agendas exist only as PDFs.** The eLMS API's meeting rows carry an
   `agenda` field, but it is `null` in list responses and `[]` in the detail
   endpoint (`GET api.chicityclerkelms.chicago.gov/meeting/<meetingId>`) even
   for a published meeting. The PDF under `files[attachmentType=Agenda]` is the
   only machine-readable agenda source.
2. **Agenda PDFs are text-based and parseable.** The 2026-07-14 Transportation
   agenda extracts cleanly with pypdf: a cover page (committee, date, room,
   optional "AMENDED" banner), then per-page ALL-CAPS section headings
   ("MAYORAL", "ORDINANCES FOR VACATIONS, …"), items with an optional leading
   ward number in parens ("(28) HUB 32, LLC – O2026-0026797") and free-text
   descriptions. Some items (mayoral appointments) carry **no** record number.
3. **eLMS has a matter lookup.** `GET /matter?filter=recordNumber eq
   'O2026-0026797'` returns the canonical `title`, `filingSponsor`, `type`,
   `status`, `matterCategory`, `committeReferral`, and `matterId`. The public
   detail page is `https://chicityclerkelms.chicago.gov/Matter/?matterId=<GUID>`
   (confirmed 200).

## Approaches considered

- **A. Parse PDF only.** No API enrichment. Cheap, but agenda text is terse and
  ugly ("HUB 32, LLC – O2026-0026797") — exactly the "proposal #45" problem the
  goal names.
- **B. Parse PDF for record numbers + enrich each via the eLMS `/matter` API
  (chosen).** Record-number regexes are the one robust anchor in the loose PDF
  layout; the API turns each anchor into a clean plain-language title, sponsor,
  type, and status — deterministic context, no LLM. Items without record
  numbers (appointments) fall back to verbatim PDF text under their section
  heading.
- **C. LLM summarization of the PDF.** Rejected: CONTRIBUTING.md's ground rule
  is deterministic pull modules; the one LLM exception (classify_safety_topic)
  only *tags* already-fetched records. Verbatim official text + official API
  titles achieves the goal without inventing words the city didn't write.

## Architecture

New module **`pipeline/pull_agenda_items.py`**, run right after
`pull_hearings.py` (it consumes `raw/hearings.json`):

1. For every meeting with an `agenda_url`, download the PDF (timeout, size
   cap); extract text with **pypdf** (new dependency, pure-Python).
2. Parse deterministically, block-by-block (blocks = blank-line-separated):
   - cover page → `amended` flag;
   - ALL-CAPS short blocks → current *section heading*; standalone "WARD"
     column headers and page numbers dropped;
   - blocks containing a record number (`\b(?:O|Or|R|SO|SR|SA|A|F|Doc|M|CL|PO|PR)
     \d{2,4}-\d{4,}\b`-style regex) → one item per record number, with
     leading `(\d+)` captured as `ward`, remaining text kept verbatim as
     `agenda_text`;
   - ALL-CAPS-led blocks under a section with no record number (appointments)
     → item with `record_number: null`, verbatim text.
3. For each distinct record number, one `GET /matter?filter=recordNumber eq
   '<rn>'` → `title`, `type`, `status`, `sponsor`, `category`, `matter_url`.
   Lookup failure leaves the item with PDF text only — never fabricated.
4. Write `raw/agenda_items.json`: `{ fetched_at, agendas: { <agenda_url>:
   { amended, items: [...] } } }`.

**Non-fatal posture** end-to-end, matching every other third-party pull: any
failure (download, parse, lookup) degrades to fewer/plainer items and never
raises the pipeline. Idempotent: re-running overwrites cleanly.

**`aggregate.py` (`build_hearings`)** merges `raw/agenda_items.json` into each
meeting by `agenda_url`: meeting gains `agenda_items: [...]` and
`agenda_amended` when its PDF was parsed (absent otherwise, so the UI knows
extraction didn't run vs. an empty agenda). Aggregate also computes two
derived flags per item — analysis stays out of the pull module:

- `safety_keyword_match`: matter/agenda title matches `SAFETY_TOPIC_KEYWORDS`;
- `tracked`: record number appears in the published council_records set.

## Published schema (SCHEMA.md, CONTRACT_VERSION 1.9 → 1.10)

```
meetings: [{ date, status, location, agenda_url, notice_url, comment,
  agenda_amended?: bool,
  agenda_items?: [{ record_number|null, ward|null, section|null,
                    agenda_text,            // verbatim from the official PDF
                    title|null, type|null, status|null, sponsor|null,
                    category|null, matter_url|null,   // from the eLMS matter API
                    safety_keyword_match: bool, tracked: bool }] }]
```

Tier stays `real` at the dataset level — every published word is verbatim from
the official PDF or the official API; the `note` gains a sentence saying agenda
items are best-effort extracted and the PDF remains authoritative.

## UI

**action.js** — each rendered meeting (both meeting blocks) gains an "On the
agenda" list when `agenda_items` is present: ward chip when known, the
API title (falling back to `agenda_text`), type · sponsor, linked to
`matter_url` (else the agenda PDF), safety-matched items emphasized. Logic
lives in the page's testable model (existing convention), covered in
tests/ui.

**ward-model.js / ward.js** — meetings already flow into the ward page; agenda
items tagged with that ward number are surfaced there ("on the next committee
agenda for this ward"), reusing the same item shape.

## Fixtures & tests

- `make_fixtures.py` is unchanged: its fixture hearings.json is the honest
  link-out fallback with **empty** `meetings`, so there is nothing to attach
  agenda items to — under `--fixtures` the merge is a structural no-op (the
  raw agenda file is simply absent), and the merge logic is covered by unit
  tests instead.
- `pipeline/tests/test_pull_agenda_items.py`: parser unit tests on real-shaped
  agenda text (sections, `()` empty ward, `(28)` ward, record-number split,
  appointment fallback, cover-page/amended handling), matter-enrichment merge,
  and non-fatal degradation. Network mocked per existing convention.
- `tests/ui`: model tests for the new agenda-items rendering data.

## Out of scope

- OCR (scanned agendas) — if a PDF yields no text, the meeting just keeps its
  PDF link, as today.
- Historic agendas — only the already-pulled upcoming meetings are parsed.
- LLM summaries of agenda items — revisit only with the classify-style
  cached/overridable pattern if verbatim titles prove insufficient.

---
*Post-merge note (2026-07-13): main's network-tiers work claimed contract
v1.10 while this branch was open, so the published contract bump for agenda
items is **v1.11** (and the DECISIONS.md entry is #25). The design above
predates the renumber.*
