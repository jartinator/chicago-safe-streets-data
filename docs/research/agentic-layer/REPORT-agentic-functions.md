---
title: "Study #1b — the agentic layer as the primary experience: functions, gaps, and the build plan"
status: research complete; maintainer answers to 5 questions pending (§8); build decisions are the maintainer's
date: 2026-07-23
supersedes: REPORT-agentic-proposal.md §Sequencing (its findings stand; its ordering is replaced here)
evidence:
  - probes/ (5 live capability probes + 00-probe-summary.md gap register)
  - interviews/ (3 new: advocate, FOIA filer, automation researcher; + 4 from study #1; + maintainer-real-user.md)
  - audits/ (study #1's 21 runs — the Q&A baseline)
  - live verification of every consequential probe claim, 2026-07-23
---

# The agentic layer as the product

**Premise, set by the maintainer:** the website meets people where they are;
the agentic layer is being built to meet their needs *better* — a superior
experience, not a defensive compatibility layer. AI adoption is assumed. The
question is no longer "do assistants quote us right" (study #1 answered it)
but **"what work does the layer let people do, and what must be built so
that work succeeds?"**

The maintainer is the existence proof: OYL's FOIA program runs through an
agent — gap identified from the data, letter drafted with verified anchors,
human sends, agent books acknowledgments and computes statutory deadlines.
The Smart Streets request went from news signal to sent-and-acknowledged,
with the statutory extension recognized and a follow-up scheduled, in under
48 hours.

## Executive summary

Five cold agents were given real jobs against the live public layer —
monitor a ward, brief an alder, draft a FOIA, explain a ranking, build a
watcher. **All five completed their tasks**, at quality a professional could
use, with zero fabrications surviving to a deliverable. The layer as-built
already supports real work. That is the headline, and it was not a foregone
conclusion.

The second headline is what the probes had to do *by hand*. The same missing
affordances recurred across independent probes — no history/diffs, a
badly-signposted front door, no joins between the layer's own families,
ambiguous absence, re-derived conveniences, an under-specified builder
contract. Those recurrences, cross-confirmed by seven interview personas,
are the build list. Almost everything on it is a build-time emission —
**nothing on the build list requires a server, an account, or a byte of
runtime compute.**

The third headline is a discovery made while verifying probe claims: **the
history problem is already solved in git.** Weekly refresh PRs land each
build as a commit on main — verified: the 2026-07-21 and 2026-07-22 builds
are both retrievable today at commit-pinned raw URLs. The layer's single
hardest missing function (monitoring: "what changed?") and the researcher
persona's citation-grade archival need are both *surfacing* problems — emit
an index and a diff at build time — not infrastructure problems.

Also: the probes found two real data bugs (a ward file that disagrees with
itself; 4 of 6 proposed projects with empty ward tags), both verified live
and filed as fix tasks. A method that finds publisher bugs on first contact
is worth institutionalizing — which is what study #1's B2 (standing audits)
already proposed.

---

## 1. Function verdicts — can an agent do the job today?

Full transcripts and grading in `probes/`; gap codes (G1–G8) defined in
`probes/00-probe-summary.md`.

| Function | Verdict today | What held it back | Website comparison |
|---|---|---|---|
| **F-A Monitoring** | Designable, not runnable — state must live client-side; the layer's own inconsistencies would false-alarm week one | G1 (no history/diffs), G3, G4, G6 | The website cannot do this at all — but neither, yet, can the layer without client-side state |
| **F-B Briefing** | Works now at professional quality — but safety depended on agent discipline exactly where the layer has no guardrail (rank derivation, council false positives, ward-scoping) | G5, G3, G4, G7 | Superior to website: the brief assembled in minutes what would take an evening of tab-hopping, with caveats attached — *if* the number risks are closed |
| **F-B2 FOIA drafting** | The strongest result: a cold agent independently reconverged on the maintainer's real CDOT request — same gap, same agency, overlapping records language — from public files alone | G2 (found gaps via the repo, not the site), agency-contact 403s | No website equivalent exists anywhere; this is a function only the agentic layer provides |
| **F-C Investigation** | Over-performs: real cross-family synthesis, incl. an insight no single page states ("the #1 ward has nothing queued") and *applied* caveat comprehension | G3 (all joins hand-made), G2, G5 (formula found by luck) | Superior to website: the website can show each fact; it cannot chain them |
| **F-D Developer watcher** | Zero to validated, diffing, fail-loud watcher in one session — then 6 precise contract complaints | G6, G1 | The website offers this function nothing; the API + schemas carried it |

**The asymmetry with study #1 matters.** One-hop Q&A produced a fabricated
ward number with perfect caveats (S3/Q1). Task-shaped work, which fetches
many files, produced zero surviving fabrications across five probes. Depth
of engagement is itself a safety mechanism — another argument for making
the layer the primary experience rather than a citation target.

## 2. What the humans-behind-agents need (7 personas + 1 real user)

Convergences, each independently reached:

1. **Caveat-correct-but-fact-wrong is the universal deal-breaker** — now
   named unprompted by *six* personas across both studies (journalist,
   staffer, resident, developer, filer, researcher). The filer's version is
   the sharpest: one fabricated number beside correctly-caveated real ones
   is "worse than uniform unreliability because it defeats spot-checking."
2. **FOIA is capacity, not convenience.** The advocate's strongest reaction
   in her whole interview: assistant-run FOIA is "a door that's closed to
   us" — her group has never filed one. Probe F-B2 proves the door can be
   opened from public files. The filer's caution bounds it: the maintainer's
   workflow covers "the easy 40%" — mechanics, not the adversarial half
   (narrowing fights, denials, PAC appeals) — and must not be oversold.
3. **Monitoring is the first function two personas would adopt** (advocate:
   comment-window discovery has *no* existing workaround; researcher: weekly
   diff + contract-version watch). Both, plus the maintainer's own prose
   cron rule ("+7 business days if no acknowledgment"), are G1 by another
   name.
4. **The citation must be fetchable, dated, and independent of the
   assistant.** The researcher will delegate monitoring but "never the
   citation itself"; her archival root of trust cannot be an
   assistant-maintained local store. Commit-pinned URLs (§3) answer this
   exactly.
5. **Numbers and their provenance must be structurally inseparable in
   artifacts** (staffer, advocate, resident — study #1; reconfirmed by the
   advocate's drafted-one-pager review habit). OYL cannot control assistant
   rendering, but it can publish per-fact deep links that make inseparability
   cheap (G5/G8).

## 3. The unlock: history already exists

Verified 2026-07-23 on origin/main: successive weekly builds are distinct
commits; `git show <sha>:site/api/v1/citywide.json` retrieves the 07-21 and
07-22 builds today, and raw.githubusercontent.com serves any file at any
commit SHA over plain HTTPS, no auth.

What's missing is only that nothing *tells* an agent this. Three build-time
emissions close G1, the researcher's archival need, and most of the
staleness contract at once — all static files:

- **`api/v1/builds.json`** — an index: build date → commit SHA →
  commit-pinned base URL, appended each refresh.
- **`api/v1/changes.json`** — the diff the pipeline computes between this
  build and the last (numbers that moved, statuses that flipped, contract
  bumps, fields added/removed). This converts every "watch it for me" ask —
  advocate, researcher, staffer, the maintainer's own FOIA nudges — from
  "agent must keep state" to "agent fetches one file." It is also the
  artifact the journalist asked for as corrections insurance ("what changed
  / what's still shaky").
- **`_meta.expected_update_interval_hours`** + a pinned-snapshot URL in
  every envelope — the staleness contract and the citation-grade permalink,
  per build, for free.

## 4. The build plan

Ordered. Items from study #1 that survive are folded in at their new rank.
Every item names its evidence and states the static-files verdict (all pass
unless noted).

**Tier 1 — the function unlocks (new, from the probes):**

1. **History surfaced: `builds.json` + `changes.json` + snapshot URLs**
   (§3). Evidence: G1 hit by both automation probes; 3 personas + the
   maintainer's own workflow. Unlocks F-A outright.
2. **Front-door placement fix** (G2). The `<noscript>` pointer exists —
   verified — but 3 of 5 probes never saw it and reached the API via the
   GitHub repo. Put the agent pointer where extractors actually look:
   visible HTML text on every page, an HTTP `Link` header if Pages allows,
   sitemap entries for `llms.txt` and `api/v1/index.json`. Cheap, and it
   compounds study #1's B4 (indexability).
3. **The FOIA seed-bank** (probe F-B2 + advocate + filer + maintainer Q1,
   answer pending). Publish, as data: the known-gaps list, why each gap
   matters, the records language that would fill it, the custodian agency
   and intake route (compensating chicago.gov's 403s to fetchers). The
   probe proves an agent can then do the rest. Scope honestly per the
   filer: this seeds *requests*, it does not "handle FOIA."

**Tier 2 — the number-safety closers (probes + study #1 continuity):**

4. **Publish the derived conveniences agents keep re-deriving** (G5):
   `rank` and percentile on ward scores (F-B's near-fabrication was
   precisely here), citywide baselines for per-ward metrics, the
   danger-score formula in a fetchable static doc — plus study #1's **B1**
   (headline answers inlined into `llms.txt`, same pipeline pass), which
   remains the single cheapest correctness fix for one-hop surfaces.
5. **Coverage semantics** (G4): per family, a machine-readable statement of
   what was checked and when, so "no projects in Ward 25" stops being
   ambiguous between *none* and *not covered*.
6. **Join keys** (G3): ward tags on proposed projects (fix task filed),
   ward lists on corridors/routes where derivable, term dates on council
   sponsor matching. Each hand-join a probe invented is a silent-error site.
7. **Builder contract hardening** (G6, F-D's list + developer persona):
   self-contained or bundled schemas, a schema-coverage list, full schema
   coverage for wards/council, stable-id contract on `findings`,
   cross-endpoint version semantics documented. Plus the two filed data-bug
   fixes (intra-file window disagreement; empty ward tags).

**Tier 3 — reach (carried from study #1 and the home-page thread):**

8. **B3 referral-with-refusal generalized; B4 rung-0 indexability;** the
   four job-shaped paste-in prompts on the home page (one per audience
   block, replacing the single generic prompt in the 2026-07-16 spec), and
   a packaged skill once the prompts are A/B-tested. The `llms.txt` stale
   map link (still open) rides along.
9. **B2 standing audits, now extended with capability probes.** This
   study's probes found two publisher bugs and one false friction claim on
   first contact; study #1's audits caught the Ward-32 fabrication. Re-run
   both suites after Tier 1–2 ship; the predictions are specific (S3-class
   surfaces produce Ward 42; F-A-class watchers need no client state).

**Still killed, evidence unchanged or strengthened:** MCP server (every
item above is a static emission; the probes did professional work over
plain HTTPS — the transport was never the problem); LLM-judged CI evals
(the deterministic contract checks in Tier 2 are the CI-able part);
per-question endpoints (subsumed by B1 + G5); more JSON-LD. **Newly
killed:** OYL-hosted alerts/notifications (requires accounts/push —
`changes.json` + the user's own agent achieves the function statically);
DOI/institutional archival tier (the researcher memo itself flagged it as
disproportionate; commit-pinned URLs cover the need she actually
demonstrated).

## 5. The "superior experience" claim, tested

The claim survives, with one honest boundary. Where the work is *assembly*
— brief-building, investigation chains, watcher construction, records
drafting — the agent+layer combination did in minutes what the website
cannot do at all or only via an evening of manual synthesis, and did it
with caveats attached. Where the work is *a single number*, study #1 stands:
a shallow one-hop agent is still the most dangerous consumer the layer has,
and Tier-2 items exist precisely to protect that case. The website remains
the trust anchor the personas verify against; the layer is where the work
happens. That division — website as record, layer as workbench — is the
architecture the evidence supports.

## 6. Method limits

Single execution per probe; Sonnet-class agents only (stronger or weaker
agents will shift results); simulated personas (now 7, still 0 real
external humans — the advocate and filer findings especially warrant
real-world validation before major investment); probe tasks were
OYL-pointed (discovery was study #1's question, not re-tested here); the
maintainer's five answers (§8 of `interviews/maintainer-real-user.md`)
were pending at time of writing — Q1 (publish the FOIA seed-bank or keep
the workflow internal?) gates build item 3's scope, and the report should
be amended when answers land.

## 7. One-sentence version

The agents can already do the work — every job we handed them, they
finished; what they cannot do is see yesterday, find the front door, or
trust a join — and all three are build-time emissions away from fixed,
because the history is already sitting in git.
