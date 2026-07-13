# Proposed & in progress — what shipped, why, and how (plain language)

**Date:** 2026-07-13 · **Branch:** feat/proposed-routes-news (builds on the
"In the news" layer, PR #37) · Companion to the
[design doc](../../superpowers/specs/2026-07-13-proposed-projects-design.md)
and [decision #30](../../../DECISIONS.md).

## What shipped

The site can now answer **"is anything actually coming to this street?"** —
the question the planned-routes layer was supposed to answer and never
could (it's been an empty file since day one, because the city publishes no
usable data about planned routes):

- A **"Proposed & in progress (citywide)"** card on the Take Action page:
  six real, verified projects — the 606/Bloomingdale Trail extension,
  the Archer Avenue safety project, the Grand Avenue bike lanes (phase 2),
  the DuSable Lake Shore Drive redesign, the Englewood Nature Trail, and
  the Weber Spur trail.
- Each project shows: a **plain-English status** ("in design", "funded in
  part", "installed, being modified") with **the date it was last reviewed
  and the citation backing it right next to it**, one sentence of
  what/where, the official project page, and recent news headlines about
  the project — the round-1 news feature doing new work.
- Wards with a project get a **"Proposed & in progress here"** line on
  their ward report (Ward 12 shows Archer; Wards 1/27/36 show Grand).
- **No map lines.** We checked every candidate source — CDOT's tracker is
  a spreadsheet someone would have to hand-geocode, and the regional
  planning agency's "bikeway inventory" turned out to be an archive of
  municipal plans from 2012. Honest map geometry for proposals doesn't
  exist, so we don't draw any.

## Why

The user asked the motivating question directly: can news sources help us
understand proposed routes, like the 606 extension? The research answer was
yes — with a strict division of labor:

- **News can't tell you a project's status.** During the Archer Avenue
  fight, outlets described the same week's events as "installed" and
  "ripped out"; one outlet published a piece disputing another's
  characterization of the same project. So statuses are **written by
  humans, reviewed against citations, and dated** — never inferred by
  software.
- **News is excellent at telling the story around a project** — the
  protests, the funding wins, the delays. That part is automated: the
  news layer matches stories to projects and attaches them, newest first,
  each match carrying a visible record of exactly which rule matched it.

We validated the concept with the same four simulated Chicago research
subjects as before (4/4 would use it, conditionally). Their conditions are
built in: the citation sits **with** the status, not in a footnote ("a
volunteer-written status with a vague or missing link is just a rumor with
better formatting"); the roster's selection criteria are published, and
news-coverage volume is explicitly **not** one of them (so the list can't
drift toward glamour projects); and an empty coverage list says what it
means: "no recent news coverage found — that measures press attention, not
project activity."

## How it works

1. `data/proposed_projects.json` is a small, hand-maintained roster —
   every status traced to the July 2026 evidence review, every project
   verified to exist (we dropped one candidate, "312 RiverRun phase 2,"
   because it turned out not to be a real project).
2. The weekly news pull adds one extra Google News query built from each
   project's curated phrases, so coverage of projects the big bike outlets
   have stopped tagging (Englewood, Weber Spur) still arrives.
3. Matching is deliberately strict, and we tightened it after a live test
   caught real mistakes: a bare "Grand Avenue" phrase matched stories from
   Phoenix and Long Island, and "DuSable Lake Shore Drive" matched routine
   crash reports. Now project-specific phrases ("Bloomingdale Trail
   extension") match on their own, while corridor names only count when
   the headline also contains a bike/street-safety word. The result on
   real data: every attached story is genuinely about its project.
4. Missing a story is acceptable; attaching a wrong one is not — the same
   precision-over-recall rule the round-1 study demanded, because one
   wrong match costs more trust than ten misses.

## What to know / limits

- Statuses can lag reality between volunteer reviews. The last-reviewed
  date is always shown, and the official page is always the authority.
- Coverage lists will often be short or empty — most of these projects
  make news a few times a year, at milestones. That's honest, not broken.
- The roster is editorial. The criteria are published on the Sources page,
  and additions/corrections are invited via GitHub.
