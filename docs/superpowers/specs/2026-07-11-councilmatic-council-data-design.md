# Design: Fold Councilmatic into the council-data pipeline

**Date:** 2026-07-11
**Branch:** `feature/councilmatic-council-data` (off `main`)
**Status:** Approved design, pending spec review → implementation plan

## Problem

The pipeline's council-legislation data is frozen. `pull_council_records.py` /
`legistar.py` pull from `webapi.legistar.com`, whose most recent
`MatterIntroDate` is stuck at **2023-06-21** (`LEGISTAR_DATA_FROZEN_AT`) because
Chicago's City Council migrated off Legistar to a new system (eLMS). No working
eLMS JSON endpoint was found during prior research, so everything after that
date is invisible: `aggregate.py` surfaces a "data frozen" gap and
`aldermen_safety_record.json` is built from stale sponsorships.

## What we found (spike, 2026-07-11)

DataMade's **Chicago Councilmatic** (MIT-licensed) publishes official Chicago
City Council data via a public Datasette instance
(`https://puddle.datamade.us/chicago_council-464e17d`), a SQL-over-HTTP JSON
API. Verified against live data:

- **Current through 2026-07-09** — fully covers the post-2023 gap.
- Council actions: 16,158 (2024) / 18,964 (2025) / 8,519 (2026-to-date).
- **28+** bike/pedestrian/safety bills with activity after our cutoff.
- Rich schema: `bill`, `billaction`, `billsponsorship`, `person`, `personvote`,
  `voteevent`.

Data-quality findings that shaped this design:

- `bill.classification` is a JSON-encoded string (`["ordinance"]`) — must be parsed.
- The keyword net catches noise (a *committee-appointment* resolution matched
  "traffic safety"), so records must still flow through the existing
  `classify_safety_topic.py` refinement.
- **Sponsorship varies per bill** — the real accountability backbone.
- **Votes are near-unanimous:** of 12,302 recorded vote events post-2023, only
  **175 (1.4%)** had even one "No"; 0.09% of individual votes were "No". A naive
  "% voted yes" score would be a flat, misleading column. The ~175 genuinely
  contested votes ARE real signal and are surfaced individually.
- Raw `absent` counts conflate committee non-membership (an alder marked
  "absent" from a committee they don't sit on is not a no-show) — attendance is
  therefore **out of scope**.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Consumption path | Live Datasette SQL API | Only ~dozens of keyword-filtered bills per run; weekly, human-reviewed. The 3.7 GB nightly `.db.zip` dump is overkill; documented as fallback only. |
| Merge point | Two raw files + shared union helper | Each puller stays independent and independently degradable; re-running one source can't wipe the other. |
| Vote signal | Per-bill contested votes + per-alder `recorded_no_votes` count | Both are real; no synthetic scoring. |
| Attendance | Out of scope | Raw `absent` conflates committee non-membership. |
| Full DB dump | Out of scope (documented) | Live queries suffice for the volume. |
| Provenance tier | `real` (disclosed as a mirror) | Official council data, sourced via DataMade's Councilmatic mirror. |

## Architecture

Pipeline order (unchanged except the new pull inserted before classify):

```
pull_council_records.py  -> raw/council_records.json      (Legistar, <= 2023-06-21)
pull_councilmatic.py     -> raw/councilmatic_records.json  (Councilmatic, > 2023-06-21)  [NEW]
classify_safety_topic.py -> raw/safety_topic_tags.json     (reads UNION of both raw files)
aggregate.py             -> site/data/council_records.json + aldermen_safety_record.json
```

### Component 1 — `pipeline/councilmatic.py` (shared fetch helper)

Mirrors `legistar.py`. Single function:

```
query(sql) -> list[dict]
```

GET against `{COUNCILMATIC_DATASETTE_URL}.json?sql=<sql>&_shape=array` with
retry/backoff (same shape as `legistar._get`). Isolates the SQL-over-HTTP detail
so callers never build URLs.

### Component 2 — `pipeline/pull_councilmatic.py` (deterministic pull, non-fatal)

Follows the `pull_council_records.py` contract: fetch only (no analysis, no
LLM), idempotent, warns-and-skips on failure.

**Bills.** Keyword net reuses `SAFETY_TOPIC_KEYWORDS` over `bill.title`, filtered
to bills whose latest `billaction.date` is **> `LEGISTAR_DATA_FROZEN_AT`** so
this module owns only the post-2023 gap (no overlap with Legistar). Normalizes
each bill to the **existing council-record schema** so downstream is
source-agnostic:

```json
{
  "matter_id": "O2025-0015514",        // Councilmatic `identifier`; never collides with Legistar ints
  "title": "...",
  "type": "ordinance",                  // parsed from JSON-encoded bill.classification
  "status": "...",                      // latest billaction description
  "intro_date": "YYYY-MM-DD",
  "body": null,                          // Councilmatic has from_organization; optional
  "sponsors": ["Hopkins, Brian", "..."],// billsponsorship -> person
  "url": "https://chicago.councilmatic.org/legislation/O2025-0015514/",
  "source": "councilmatic",
  "recorded_votes": {                    // present ONLY when a contested vote exists
    "date": "YYYY-MM-DD",
    "yes": 33, "no": 15, "absent": 2,
    "no_voters": ["Lastname, First", "..."],
    "result": "pass"
  }
}
```

**Contested votes.** For each matched bill, if it has a `voteevent` with recorded
individual `personvote`s and any dissent (`option = 'no'`), attach
`recorded_votes`. Only ~175 events citywide qualify, so this is a small honest
layer, never synthetic.

**Output & degradation.** Writes `raw/councilmatic_records.json`
(`{source, fetched_at, covers_from, keywords, records}`). On any
`requests.RequestException`: warn to stderr, leave the file absent, return —
identical to the Legistar puller's non-fatal posture. `aggregate.py` falls back
to its stub.

### Component 3 — shared union helper

`load_all_council_records()` (small, new; placed where both `classify` and
`aggregate` can import it) returns the union of:

- `raw/council_records.json` records (Legistar), tagged `source: "legistar"`
- `raw/councilmatic_records.json` records (Councilmatic), already tagged

Deduped by `(source, matter_id)`. Either file may be absent (union still works).

- **`classify_safety_topic.py`**: its single read of `raw/council_records.json`
  switches to this helper, so Councilmatic bills get LLM-tagged through the
  existing keyword-noise filter. Its `matter_id`-keyed cache handles mixed
  id formats (int vs string) — JSON keys are strings, no collision.
- **`aggregate.build_council_records()`**: switches to the helper; carries
  `source` and `recorded_votes` onto each output record; **flips the gap note**
  — when Councilmatic records are present, the note reads "current through {max
  Councilmatic action date}" instead of the frozen-2023 message; when absent, the
  existing frozen message stands.

### Component 4 — accountability record

`build_aldermen_safety_record()` needs **no structural rework**: current
Councilmatic sponsorships now flow through the merged records, so the
sponsorship record refreshes automatically. One addition: a per-alderman
`recorded_no_votes` integer — the number of topic-relevant records where the
alder appears in a `no_voters` list. No "% voted yes" score.

### Component 5 — supporting changes

- **`config.py`**: add `COUNCILMATIC_DATASETTE_URL`; a comment pointing at the
  nightly `chicago_council.db.zip` dump
  (github.com/datamade/chicago-council-scrapers releases) as documented
  fallback; update the `LEGISTAR_DATA_FROZEN_AT` comment to note the gap is now
  covered by Councilmatic.
- **`run_all.py`**: run `pull_councilmatic` after `pull_council_records`, before
  `classify_safety_topic`.
- **`make_fixtures.py`**: synthetic `councilmatic_records.json` (including one
  record with `recorded_votes`) so `run_all.py --fixtures` exercises the merge
  and contested-vote paths offline.
- **`meta.json` sources entry + `SCHEMA.md`**: document Councilmatic as tier
  `real`, disclosed as sourced via DataMade's Councilmatic mirror, consistent
  with how every source is badged.
- **`DECISIONS.md`**: record the calls (live Datasette over dump; contested
  votes only; attendance dropped and why; two-file union merge).

## Out of scope (YAGNI)

- Per-alderman attendance metrics (committee-non-membership conflation).
- Committees/meetings replacement for `pull_hearings.py`.
- The 3.7 GB full-DB dump path (documented in a comment, not coded).
- `check_provenance.py` hook wiring — that file isn't on `main` yet (it was
  added on `fix/restore-real-socrata-data`); noted as a follow-up if/when that
  branch lands.

## Testing

- `run_all.py --fixtures` exercises the full merge + contested-vote path offline
  via the synthetic fixture.
- Each puller prints a sanity summary (row count, min/max action date) matching
  the style of the existing modules.
- A live `python pull_councilmatic.py` run confirms real records land and
  normalize correctly.

## Risks

- **Third-party dependency**: the Datasette endpoint is DataMade's
  infrastructure; treated as non-fatal (degrades to stub), same as Legistar,
  Mellow, and Ward Wise.
- **Unverified upstream**: how Councilmatic's scraper reaches post-2023 data
  isn't fully pinned down (their repo has a "Legistar End — July 2023" tag, yet
  the data is current). The data is fresh and correct from the outside; the
  scraper source is worth a look before long-term reliance.
