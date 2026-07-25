---
title: Capability-probe summary — can agents DO work with the layer?
run_date: 2026-07-23
probes: 5 (one per function; F-B split into brief + FOIA)
method: >
  Cold Sonnet agents, no study context, realistic tasks, public layer only
  (F-D additionally allowed to write/run code in an isolated scratchpad).
  Tool logs captured. Every consequential claim in a probe deliverable was
  re-verified against the live API by the study before grading; probe errors
  are recorded as findings, not silently corrected.
---

# Probe summary — the layer under working conditions

Study #1 asked whether assistants *quote* the layer correctly. These probes
asked whether they can *work* with it: monitor, produce documents, chase a
"why," build against it. Grading axes: **T** task completion, **C**
correctness of numbers used, **V** caveat/provenance carriage into the
artifact, **G** gap yield (what the probe surfaced that OYL could build).

| Probe | Function | T | C | V | Verdict in one line |
|---|---|---|---|---|---|
| [F-A monitoring](f-a-monitoring.md) | weekly ward check | 2 | 2 | 2 | Recipe + honest baseline run; found 2 real data bugs; state must live client-side |
| [F-B ward brief](f-b-ward-brief.md) | meeting one-pager | 2 | 2* | 2 | Defensible brief; caught its own near-fabrication; one false friction claim |
| [F-B2 FOIA draft](f-b2-foia-draft.md) | records request | 2 | 2 | 2 | Independently converged on the maintainer's real request; send-ready quality |
| [F-C investigation](f-c-investigation.md) | "why is 42 worst" | 2 | 2 | 2 | Real multi-endpoint synthesis incl. the Dearborn paradox; hand-joins throughout |
| [F-D watcher](f-d-developer-watcher.md) | scheduled code | 2 | 2 | n/a | Working validated watcher in one session; 6 precise API friction items |

\* one small aggregate slip (claimed citywide mean protected share 13.1%;
live computation gives 12.8%) that does not change its conclusion.

**Headline: every probe completed its task.** The layer as-built already
supports real work — with the agent supplying, by hand, a set of missing
affordances that recur across all five. Those recurrences are the build list.

## The cross-probe gap register

Ordered by how many probes independently hit each gap.

### G1 — No history, no diffs, no change feed (F-A, F-D; automation persona)
Every URL is overwritten weekly. "What changed?" — the core of monitoring —
is unanswerable from the site alone; both probes built client-side state
stores and said so explicitly. F-D: no `changelog.json`, no per-record
`updated_at`, ETags present but undocumented. F-A: "a fetch-only client
cannot recover 'what changed since last week' on its own."

### G2 — The agent front door is real but badly signposted (F-B2, F-C, F-B)
Three probes reported the homepage/map/methodology pages as empty shells to
their fetch tools and reached the API *via the GitHub repo tree*. F-C called
`llms.txt` "the actual front door… I only got it because I tried it as a
common convention on a hunch."

Study verification adds precision: the static HTML **does** contain a
`<noscript>` block whose first bullet is "AI agents & developers: start here
— llms.txt." The pointer exists; the probes' fetch pipelines did not surface
it (consistent with extraction steps that drop noscript content). The gap is
therefore *pointer placement*, not pointer absence — e.g., the pointer must
also exist where extractors actually look (visible HTML, headers, sitemap
annotations), not only inside `<noscript>`.

### G3 — No joins between the layer's own families (F-C, F-A, F-B)
No ward field on corridors or routes; no adjacency between wards; 4 of 6
proposed projects have empty `wards` (so ward filters silently miss the 606
extension — verified live); council records need a sponsor-name join with no
ward field and no term-date guard (F-B hit 2010–2013 false positives for a
2019-seated alder). Every cross-family question was answered by hand-joins
the agent had to invent, each one a place for silent error.

### G4 — Absence is ambiguous everywhere (F-B, F-C, F-A)
"No projects in Ward 25", "no news for Ward 42": the layer cannot say
whether that means *checked and none* or *not covered*. F-B had to invent
the honest phrasing itself; F-C explicitly couldn't distinguish matcher-miss
from genuine absence. A per-family "coverage" statement (what was checked,
when, empty-is-meaningful) would close it.

### G5 — Derived conveniences agents keep re-deriving (F-B, F-A, F-C)
No `rank` on ward danger scores (F-B's near-fabrication was exactly here — a
summarization pass emitted "ranks 25th" from the ward number; caught only by
re-sorting all 50 wards). No citywide roll-up aggregates for per-ward fields.
Danger-score formula documented only in an embedded `note` field (F-C found
it there by luck; methodology.html is empty to fetchers). Publishing rank,
percentile, and per-metric citywide baselines would remove a whole class of
agent arithmetic.

### G6 — Contract details that bite builders (F-D, plus one F-A find)
Schemas `$ref` a non-self-contained `envelope.schema.json` with no discovery
path; schema coverage is partial (`wards.schema.json`, `council.schema.json`
404) and nothing lists which endpoints are covered; no machine-readable
update-cadence field (`STALE_HOURS` had to be invented from prose);
`findings[].id` used as a stable key but not contracted as one;
cross-endpoint `contract_version` lockstep undocumented. Plus the F-A find,
verified live: `crash_trend` and `windows` in the same ward file disagree
(window_end 07-16 vs 07-20; 76/62 vs 74/63) — filed as a fix task.

### G7 — Naming discoverability is inconsistent (F-B vs F-A/F-C)
Two probes found `wards/ward-NN.json` effortlessly; one guessed
`wards/25.json`, got a 404, concluded per-ward endpoints don't exist, and
downgraded its own data access. The endpoint exists — the miss is a
documentation/URL-pattern legibility failure, and it shows recovery from a
wrong first guess is not reliable.

### G8 — LLM-mediated fetch is the wrong transport for numbers (F-A, F-D, F-B)
F-A recommended plain HTTP + JSON parsing for any standing automation "to
avoid paraphrase-introduced error creeping into the numbers"; F-B's
rank near-miss came from a summarization pass, not a fetch. The layer can
help by making exact values easy to re-verify (deep links per fact) and by
publishing recipes that push automations toward plain HTTP.

## What the probes did NOT find

- No probe fabricated a number that survived to its deliverable. F-B's
  near-miss was caught by the probe itself; graded C=2 with the near-miss
  recorded. Task-shaped work with the full API in hand looks *safer* than
  study #1's one-hop Q&A — consistent with the second-hop finding, since
  probes fetched many files.
- No probe hit a wall that made a function impossible. The gaps are
  friction and reliability taxes, not brick walls — except G1, which makes
  monitoring genuinely impossible without client-side state.
