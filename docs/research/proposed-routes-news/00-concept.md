# Concept: proposed routes through the news — making "what's coming" legible

**Date:** 2026-07-13
**Status:** fleshed-out idea, pre-feasibility. Round 2 of the news-layer work
(round 1: docs/research/news-layer/, branch feat/news-coverage-layer).
Archetype case: **the 606/Bloomingdale Trail extension**.

## The gap this fills

OYL's `planned_routes.geojson` has been an empty stub since the project
began: "CDOT publishes planned bikeways only as PDF maps — no structured
feed yet." Meanwhile the round-1 feasibility work showed the *news* record
of proposed projects is rich: the Archer Avenue saga (install → protest →
partial rollback → community rides), the Grand Avenue fight, corridor
reconstructions — each proposal generates a months-long paper trail across
Streetsblog, Block Club, and TV outlets before and after anything gets
built. Residents' most common questions in the prior user-needs study were
about exactly this ("what's planned for my street?", the everyday rider's
"is this ever getting fixed?") and OYL currently answers with a blank layer.

## The idea in one paragraph

A small, hand-curated **roster of active bikeway proposals/projects**
(`data/proposed_projects.json`, the same editorial-roster pattern as
`data/main_routes.json`): each entry carries a name, corridor description,
ward(s), a human-curated **status** (proposed / funded / under construction /
partially built / blocked / shelved) with an as-of date, links to the
official record (CDOT project page, ordinance, budget line), and **name
tokens**. The round-1 news layer then does what it already does — its
matcher gains project tokens, so every pulled news item mentioning "606
extension" or "Archer Avenue bike lanes" is automatically attached to the
project, newest first. The site gets a "Proposed & in progress" view where
each project shows its curated status, its official links, and its living
coverage trail — the narrative of the proposal as it moves (or stalls).

## Division of labor (the honesty core)

- **Humans curate the roster and the status.** Status is a judgment call
  news text cannot settle deterministically (Archer was simultaneously
  "installed" and "being removed" depending on the week). Curated = the
  same trust basis as the main-routes roster; every status carries as-of +
  the citation that justifies it.
- **The pipeline attaches evidence automatically.** News matching (already
  built, already validated) supplies the ongoing coverage per project with
  auditable `via` strings; official links are checked-in data.
- **Geometry is optional and honest.** If no machine-readable geometry
  exists (expected), projects render as cards/list — never hand-guessed
  map lines presented as real. A hand-traced `crowdsourced`-tier sketch is
  a possible later step, following the curated-trails precedent.

## What it would look like

- A "Proposed & in progress" section (likely on the network or findings
  page, plus ward pages for projects tagged to that ward): project name,
  status chip with as-of, one-line corridor description, official links,
  then "Coverage" — the attached headlines, newest first.
- The 606 extension entry, e.g.: status + the official record + every
  story as the proposal moves through funding and construction.
- Ward page: "Proposed here: Archer Ave bike lanes (partially rolled back,
  as of 2026-05) · 12 stories".

## Why round 2 follows naturally from round 1

Round 1 built the pull, the matching machinery, the provenance framing
(real headlines / derived matches), and validated the trust rules (4/4
personas: precision over recall, auditable matches, no invented claims).
Round 2 adds one roster file, a handful of matcher tokens, and a render —
most of the risk was already retired.

## Honest hazards (to test in feasibility + persona research)

1. **Token collision.** "606" matches events-on-the-existing-trail coverage,
   not just extension coverage. Tokens must be phrase-level ("606
   extension", "Bloomingdale Trail extension") and the worked example must
   check real headlines. A project's coverage list polluted with unrelated
   trail-festival stories is round 1's "wrong match" failure wearing a
   new hat.
2. **Staleness of curated status.** A volunteer-maintained status that
   silently rots is worse than no status ("funded" two years after it was
   shelved). Mitigations: as-of date always shown; perhaps a "status last
   reviewed" nag in CI; keep the roster small (5-10 active projects).
3. **Roster selection bias.** Which proposals make the roster is editorial.
   Same posture as main routes: documented criteria, gaps stay visible.
4. **Scope creep into project tracking.** OYL said "no project/construction
   tracking" in its NOT-list. This is a deliberate, narrow revision of that
   boundary — the persona study should test whether it earns its place.

## Kill criteria

- Fewer than ~4 real, currently-live proposals with meaningful coverage
  trails (a roster of one is a page, not a layer).
- Name tokens can't separate proposal coverage from general corridor
  coverage in real headlines.
- Personas read curated status as OYL claiming insider knowledge it
  doesn't have, or don't value the coverage trail.
