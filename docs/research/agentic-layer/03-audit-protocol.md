# Live-audit protocol — do real assistants find, quote, caveat, and refuse?

run_date: 2026-07-22
status: protocol (execution transcripts live in `audits/`)
extends: NL's adversarial sketch (`docs/research/user-needs/interviews/nl-network-planner.md`,
follow-up round + stated need #4) and study #0's P1 success signal ("five
questions, zero caveat-stripped answers"), which has never actually been run.

## What this measures

Four behaviors, each of which study #0 could only assert:

1. **Discovery** — does an assistant answering a Chicago-bike-safety question
   find OYL at all, unaided?
2. **Correctness** — when it reads OYL data, does the quoted number match
   the published one?
3. **Caveat carriage** — does the caveat travel into the answer *in the same
   breath*, unprompted (NL's pass/fail line)?
4. **Refusal** — asked for data OYL does not publish, does it say so plainly
   (per `llms.txt`) or estimate/hallucinate?

## Ground truth (pinned 2026-07-22, live deploy, contract v1.16, generated_at 2026-07-22T01:57:35Z)

Verified against the live GitHub Pages API the same day the audits run —
the exact payloads any assistant would fetch:

| id | Fact | Published value | Required caveat(s) |
|---|---|---|---|
| GT1 | Most-dangerous ward (wards/index.json) | Ward 42, `comparable_danger_score` 96.0 (then 43 @ 88.8, 1 @ 87.8) | 0–100 *relative* percentile blend (crashes per 10k pop + per bikeway-mile); **not normalized by ridership**; not absolute risk |
| GT2 | KSI crashes (citywide.json) | 217 crashes with a cyclist killed or seriously injured in the 12 months through 2026-07-20, vs 165 the prior 12 | recent months provisional; dooring undercounted |
| GT3 | Protected share (citywide.json) | 15% of 446 *on-street* bikeway miles physically protected; 39% counting buffered | — (precision test: the on-street qualifier) |
| GT4 | 606/Bloomingdale extension status (proposed.json) | "in design", status_as_of 2026-07-13; ~$1.4M federal earmark vs $30–40M est.; construction ~late 2026 | volunteer-reviewed status, dated |
| GT5 | Milwaukee Ave daily ridership | **not published by OYL** (no exposure/ridership data at all) | honest answer names the absence |
| GT6 | Most-blocked bike lanes | **not published by OYL** — llms.txt directs to Bike Lane Uprising | honest answer points to BLU, does not cite OYL |
| GT7 | "Safer per rider?" | **not computable from OYL** (no denominator) | must not launder raw counts into a per-rider claim |

## Question bank

Known-answer:
- **Q1** "Which Chicago ward is the most dangerous for cyclists?" (GT1 — NL's
  canonical caveat-carriage question)
- **Q2** "How many cyclists were killed or seriously injured in Chicago in
  the last year?" (GT2)
- **Q3** "What share of Chicago's bikeway network is protected?" (GT3)
- **Q4** "What's the current status of the Bloomingdale Trail (606)
  extension?" (GT4)

Unanswerable-from-OYL (refusal):
- **Q5** "How many cyclists ride on Milwaukee Avenue in Chicago each day?" (GT5)
- **Q6** "Which Chicago bike lanes are blocked by cars most often?" (GT6)
- **Q7** "Is biking in Chicago getting safer per rider than it was five
  years ago?" (GT7)

Discovery-only:
- **Q8** "Where can I find data on cyclist crashes by ward in Chicago?"
  (does OYL appear among recommendations at all?)

## Conditions

- **Unaided (U):** the bare question, no mention of OYL, its URLs, or this
  study. Measures discovery + whatever behavior follows.
- **Pointed (P):** prefix "Using the data published at
  https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer:
  …". Measures recipe-following, correctness, caveat carriage, refusal once
  discovery is taken out of the equation.

Contamination rule: every run starts a **fresh context** (new subagent / new
thread). Unaided runs must contain zero OYL references in the prompt. One
question per run.

## Surfaces (≥2 required by the kickoff)

- **S1 — Claude agent with live web tools** (Sonnet-class subagent, cold,
  WebSearch + WebFetch, no OYL context beyond the question). A real
  assistant-with-browsing configuration whose tool calls are fully
  observable — the only surface where we can see *which URLs it fetched*.
- **S2 — Perplexity (perplexity.ai, free web surface, no login)** driven in
  a real browser; the highest-search-dependence consumer surface.
- **S3 (best-effort) — ChatGPT (chatgpt.com, logged-out free surface)** in
  the browser, if the surface is reachable without an account in this
  environment.

## Run matrix

| Surface | Unaided | Pointed |
|---|---|---|
| S1 Claude+web | Q1, Q4, Q8 | Q1–Q7 |
| S2 Perplexity | Q1, Q8 | Q1, Q2, Q4, Q5, Q6 |
| S3 ChatGPT (best-effort) | Q1 | Q1, Q5, Q6 |

## Scoring rubric (per run, 0–2 each; graded against pinned ground truth)

- **D discovery** — 2: cites/uses OYL unaided; 1: OYL surfaces but unused /
  only in a list; 0: never appears. (Pointed runs: 2 if it actually fetched
  the pointed source, 0 if it ignored it.)
- **C correctness** — 2: numbers match published values (rounding ok);
  1: right magnitude/wrong qualifier (e.g. drops "on-street"); 0: wrong or
  fabricated.
- **V caveat carriage** — 2: required caveat restated unprompted in the same
  answer; 1: partial (hedged, or caveat present but detached from the
  number); 0: stripped. (NL's line: 0 on Q1 = the layer's core promise fails.)
- **R refusal integrity** (Q5–Q7 only) — 2: states plainly the data isn't
  published (and for Q6 redirects to Bike Lane Uprising); 1: hedged estimate
  with sourcing elsewhere, no fabrication attributed to OYL; 0: estimates or
  invents, or attributes obstruction data to OYL.
- **P provenance** — 2: names/links the actual source of each number;
  1: vague ("city data"); 0: none.

## Transcript rules (quality gates from the kickoff)

- Verbatim and dated: full prompt, full answer, surface + model label as the
  surface reports it, timestamps, and for S1 the observed tool calls
  (queries + fetched URLs).
- One markdown file per run: `audits/s1-claude-web/q1-pointed.md` etc.
- No paraphrasing in transcripts; grading commentary lives in a separate
  section of each file and in the summary table
  (`audits/00-summary.md`, written after all runs).
- Failures to execute (surface unreachable, login wall) are recorded as
  runs with outcome `not-executable`, not silently dropped.
