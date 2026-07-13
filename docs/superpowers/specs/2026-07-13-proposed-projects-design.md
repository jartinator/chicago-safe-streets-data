# Proposed & in-progress routes — curated roster + news coverage — design

**Date:** 2026-07-13
**Precursors:** docs/research/proposed-routes-news/00-concept.md (idea),
docs/research/proposed-routes-news/evidence-proposals.md (feasibility),
round-1 news layer (docs/superpowers/specs/2026-07-13-news-coverage-design.md,
PR #37) whose pull/matching machinery this extends.

## Goal

`planned_routes.geojson` has been an empty stub since day one. Make "what's
proposed here, what's its status, and what's being written about it" legible
— the 606/Bloomingdale Trail extension as the archetype — without inventing
geometry, status, or words the city and the outlets didn't publish.

## What feasibility research settled (evidence-proposals.md + live probes)

1. **A real roster exists.** Six active projects verified with citable
   coverage: Bloomingdale Trail (606) extension (funded in part, in design),
   Archer Ave (installed, partially modified after protests), Grand Ave
   phase 2 (contested), DuSable LSD "Redefine the Drive" (pre-design),
   Englewood Nature Trail (funded in part, construction 2027), Weber Spur
   (partial funding, target 2029). "312 RiverRun phase 2" is not a real
   project — dropped.
2. **Status cannot be auto-derived from news** (Archer was "installed" and
   "being removed" in the same month, outlets disagreeing on the same
   facts). Status is **hand-curated**, with an as-of date and citations.
3. **Bare corridor tokens fail.** Streetsblog's `the-606` tag feed is ~1/12
   on-topic for the extension (trail events, closures, crime dominate).
   Matching must use **per-project curated phrase lists** ("Bloomingdale
   Trail extension", "606 extension"), multi-word, roster-maintained.
   Sparse-but-correct coverage is the accepted outcome (round-1 rule:
   precision over recall).
4. **No machine-readable planned-bikeway geometry exists** (2026 re-check):
   CDOT's tracker is a spreadsheet; CMAP's "Bikeway Inventory System"
   ArcGIS service was probed directly this session — it's an amalgam of
   2012-era municipal plan-document layers (Chicago's = the 2012 Streets
   for Cycling Plan), not a live tracker. **Projects render as cards, not
   map lines.** Geometry stays out of v1 entirely.
5. **Feed-source gap:** Englewood/Weber coverage lives partly on outlets
   outside the round-1 allowlist (Chicago YIMBY, Hoodline). Fix: one
   additional Google News RSS query built from the roster's phrases, so
   coverage follows the roster automatically.

## Architecture

**`data/proposed_projects.json`** — checked-in editorial roster (the
`main_routes.json` pattern), ~6 entries:

```
{ note, projects: [{
    id, name,
    status,            // small controlled vocab: proposed | in design |
                       // funded in part | funded | under construction |
                       // installed, being modified | complete | blocked
    status_as_of,      // date the status was last reviewed (always shown)
    status_note,       // one curated sentence
    description,       // one neutral sentence: what and where
    wards: [],         // only where confidently known; empty is honest
    official_links: [{text, url}],   // CDOT page, ordinance, budget line
    news_phrases: [],  // multi-word match phrases, curated per project
    citations: [{title, url, source, published}]  // status evidence
}] }
```

**Pull (`pull_news.py`)**: `news_feed_configs()` returns `NEWS_FEEDS` plus,
when the roster exists, one extra `google_news` feed whose query is the
OR-join of every project's quoted phrases (`when:90d`). Non-fatal: roster
unreadable → base feeds only. Nothing else changes — items flow through the
same verbatim/dedup path.

**Aggregate**: `_project_matchers(roster)` compiles each project's phrases
(word-boundary, case-insensitive, categories-then-headline via
`_search_tagged`, `via` recorded — identical mechanics to route matchers).
`match_news_item` gains `matches.projects: [{id, name, via}]`.
New `build_proposed_projects(news_items_out)`: roster passed through
verbatim + per-project `coverage`: the matched published items
(title/url/source/published/via), newest first, capped 8. Written to
`site/data/proposed_projects.json`; `data_tier: "derived"` (curated roster,
like main_routes) with `coverage` headlines `real` and matching `derived` —
the note spells out all three. meta.json entry appended after `news_items`.

**Published schema (SCHEMA.md, CONTRACT_VERSION 1.12 → 1.13):** new file as
above; `news_items.json` items' `matches` gains the `projects` key
(additive).

**UI:**
- `action.html`: citywide "Proposed & in progress" card (beside the
  citywide hearings card): per project — name, status chip + as-of,
  description, official link(s), up to 3 coverage headlines (outlet named,
  round-1 conventions). Projects with zero coverage render with their
  official links and an honest "no recent coverage found" line.
- Ward report (`action.js`): when a project's `wards` includes the selected
  ward, a "Proposed here" line appears in the ward report (name + status +
  as-of, linking to the citywide card).
- `sources.html`: card documenting the roster (editorial, criteria,
  staleness caveat: statuses are volunteer-reviewed, `status_as_of` always
  shown, the linked official page is authoritative).
- Tier badges via `BSD.badgeHTML` (derived for the card; per round-1
  precedent).

**Fixtures**: roster is checked-in real config (like main_routes) — no
fixture variant needed; fixture news contains no project phrases, so
fixture builds publish the roster with empty coverage (exercises the
zero-coverage render path in CI).

**Tests**: pipeline — phrase matcher (multi-word, word-boundary, no bare
"606" match), roster→coverage join (cap, order, zero-coverage), pull feed-
config builder (roster-driven query, missing-roster degradation);
UI — model tests for the new card data and ward filter.

## Deliberately out (v1)

- Any map geometry for proposals (nothing machine-readable exists).
- Auto-derived status, status-change detection, or notifications.
- Story↔ordinance/meeting linkage (permanently killed in round 1).
- Suburban projects; roster criteria: Chicago bikeway/trail proposals with
  an official record and active coverage.

## Validation gate before implementation

Same four persona subjects as rounds past. Probes: value of curated status
+ coverage trail; whether curated status reads as OYL claiming insider
knowledge; staleness tolerance (status_as_of visible); roster-selection
fairness (whose projects make the list); where they'd expect it. Kill/trim
per verdicts.
