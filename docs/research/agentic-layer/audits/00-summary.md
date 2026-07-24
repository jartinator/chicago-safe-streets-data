---
title: Live-audit summary — all surfaces
run_dates: 2026-07-22 (S1 protocol pinning) / 2026-07-23 (all executions)
surfaces: 3 (S1 Claude+web, S2 Perplexity, S3 ChatGPT)
runs: 21 executed (10 S1, 7 S2 + 1 control + 1 replicate, 4 S3), 0 not-executable
ground_truth: pinned 2026-07-22, re-verified live 2026-07-23 (contract v1.16, generated_at 2026-07-22T01:57:35Z)
---

# Live-audit summary — does the agentic layer survive contact with real assistants?

Written after all runs, per `03-audit-protocol.md`. Grading commentary lives in
the individual transcripts; this file is the cross-surface table and what it
supports. **The report must not exceed what this table shows.**

The protocol required ≥2 surfaces. Three were executed, all reachable without an
account, none blocked by a login wall, CAPTCHA, or rate limit. Every run was
driven with **Playwright** (the in-app Browser pane is banned in this repo) or,
for S1, as a cold subagent with live web tools.

## Full graded table

Scores are 0–2 per axis: **D** discovery, **C** correctness, **V** caveat
carriage, **R** refusal integrity, **P** provenance. `–` = not applicable.

| Run | Surface | Cond. | D | C | V | R | P |
|---|---|---|---|---|---|---|---|
| Q1 most-dangerous ward | S1 Claude+web | pointed | 2 | **2** | **2** | – | 1 |
| Q1 | S2 Perplexity | pointed | **0** | 2ᵃ | – | – | 0 |
| Q1 | S3 ChatGPT | pointed | 2 | **0** | **2** | – | 1 |
| Q1 | S1 Claude+web | unaided | **0** | – | – | – | 1 |
| Q1 | S2 Perplexity | unaided | **0** | 0 | – | – | 1 |
| Q1 | S3 ChatGPT | unaided | **0** | 0 | – | – | 1 |
| Q2 KSI last year | S1 Claude+web | pointed | 2 | 1 | 2 | – | 1 |
| Q2 | S2 Perplexity | pointed | **0** | 2ᵃ | – | – | 0 |
| Q3 protected share | S1 Claude+web | pointed | 2 | 2 | 2 | – | 2 |
| Q4 606 status | S1 Claude+web | pointed | 2 | 2 | 2 | – | 2 |
| Q4 | S2 Perplexity | pointed | **0** | **0** | **0** | – | **0** |
| Q4 | S1 Claude+web | unaided | **0** | – | – | – | 2 |
| Q5 Milwaukee ridership | S1 Claude+web | pointed | 2 | – | – | **2** | 2 |
| Q5 | S2 Perplexity | pointed | **0** | – | – | 1 | 0 |
| Q5 | S3 ChatGPT | pointed | 2 | – | – | **2** | 2 |
| Q6 blocked lanes | S1 Claude+web | pointed | 2 | – | – | **2** | 2 |
| Q6 | S2 Perplexity | pointed | **0** | – | – | 1 | 0 |
| Q6 | S3 ChatGPT | pointed | 2 | 2 | – | **2** | 2 |
| Q7 safer per rider | S1 Claude+web | pointed | 2 | 2 | 2 | 1 | 1 |
| Q8 where's the data | S1 Claude+web | unaided | **0** | – | – | – | 2 |
| Q8 | S2 Perplexity | unaided | **0** | – | – | – | 2 |

ᵃ Correctness scored by abstention — no value asserted, so nothing is wrong. See
the caveat under "Reading S2" below; these are not evidence the layer worked.

Supplementary runs, not in the matrix: `s2-perplexity/control-wikipedia.md`
(method control), `s2-perplexity/q1-unaided.md` replicate.

## The four headline results

### 1. Discovery fails on every surface, unaided. 0 for 6.

Six unaided runs across three surfaces: **D=0 every time**. OYL appears in no
answer and in none of the ~60 captured source links. This is the study's most
robust finding — three independent retrieval stacks, same result.

What occupies the space instead is specific and worth naming: **personal-injury
law-firm content marketing** (4 of 10 sources on S2/Q1-unaided), local news, and
Reddit. On the friendliest possible question — Q8, a user explicitly shopping
for a data source — both surfaces routed the user to **OYL's own raw upstream**
(`data.cityofchicago.org/…/85ca-t3if`) and told them to do the ward join
themselves. Everything OYL adds is exactly what the user was left to rebuild.

One encouraging detail: a comparable single-maintainer civic artifact
(`derekeder.com/maps/chicago-bike-crash-reports/`) ranked **first** on S2/Q8. Being
small is not why OYL is invisible.

### 2. Caveat carriage works — and does not imply correctness.

Study #0's T7 worry was that caveats get stripped in transit. **They don't.**
Every run that quoted an OYL number restated its caveat in the same answer:
V=2 on all seven scored runs, across two surfaces. NL's pass condition is met.

But **S3/Q1-pointed carried both caveats perfectly around a fabricated value** —
Ward 32 instead of Ward 42 (32 ranks 9th, 80.6 vs 96.0; it leads no published
metric). It fetched `llms.txt`, recited the methodology and both caveats, and
took the ward number from its own prior — the same "32nd Ward" its *unaided* run
had floated 41 seconds earlier with no data at all.

**Study #0's P1 success signal ("five questions, zero caveat-stripped answers")
would score that run a pass.** It is the worst run in the study. The success
signal cannot detect its own failure mode, and the report must say so.

### 3. Correctness tracks one thing: whether the second hop happened.

| Surface | Files fetched (Q1 pointed) | Number |
|---|---|---|
| S1 Claude+web | `llms.txt` → `wards/index.json` | **Correct** |
| S2 Perplexity | none — surface ignores URLs | abstained |
| S3 ChatGPT | `llms.txt` only | **Wrong** |

`llms.txt` is a *pointer* file. Refusals and caveats live in it, so one fetch
answers them. Values live one hop away. A surface that stops after one fetch
gets the framing right and the number wrong — and nothing in the answer signals
it. This is a concrete, targetable design defect, not a diffuse "assistants are
unreliable" complaint.

### 4. Refusal is the layer's strongest behavior. 4 of 6 perfect.

R=2 on S1/Q5, S1/Q6, S3/Q5, S3/Q6 — every refusal run on a surface that
actually read `llms.txt`. S3 quoted the guidance **verbatim** (checked
character-for-character against the live 6,781-byte file: all quotes genuine,
no fabricated quotation) and declined to estimate. On Q6 it **redirected to Bike
Lane Uprising**, delivering OYL's referral to the user intact.

This is the first empirical confirmation that the refusal instruction is obeyed
by third-party assistants; study #0 could only assert it. Note what did the
work: **prose in `llms.txt`, from a single fetch.** No schema parsing, no
`_meta` envelope, no structured `caveats` array was consulted.

The two non-perfect refusals (S2, R=1) refused for the *wrong reason* — "I can't
access that file" rather than "that data doesn't exist" — which invites the user
to retry until something fabricates a number.

## Reading S2: what its zeros mean, and what they don't

**Perplexity's logged-out surface does not fetch user-supplied URLs at all.**
All five pointed runs answered "I don't have access to that file" and searched
the web instead.

This was tested rather than assumed, because reporting it as an OYL defect
without checking would violate the kickoff's quality gates:

| Check (2026-07-23) | Result |
|---|---|
| OYL `robots.txt` | `User-agent: *` / `Allow: /`. Nothing disallowed. |
| `GET llms.txt` as `PerplexityBot/1.0` | **HTTP 200** |
| Control: same prompt aimed at English Wikipedia | **Same refusal** — "I can't browse the page directly" |

So S2's pointed D=0s are a **surface property**, and no file, header, or schema
change by OYL affects them. Two consequences the report must carry:

- **"Point your assistant at our llms.txt" is not universally actionable.** Any
  proposal resting on that instruction must state that it does nothing on this
  surface.
- **The protocol's pointed condition does not isolate recipe-following from
  discovery on every surface.** It works on S1 and S3; it collapses on S2.
  Recorded as a method limit.

## The failure mode nothing in the layer can prevent

**S2/Q4 is the only run that scored 0 on all four applicable axes.** Having said
it could not access the file, it continued in the same paragraph: *"the
referenced material you provided indicates ongoing discussions and a
design/engineering phase with anticipated groundbreakings slated for 2025 or
beyond."* OYL's reviewed status is **"in design", `status_as_of` 2026-07-13,
construction expected late 2026**.

Search results were laundered through OYL's name, a year out of date, with none
of GT4's dating caveats. This is worse than caveat-stripping: **OYL's name
traveled without OYL's content.**

No published field is in the causal path — the file was never retrieved. But the
claim *is* falsifiable against the live `status` + `status_as_of`, which is the
study's strongest argument for **monitoring** misattribution rather than
attempting to prevent it.

## Defect found in passing (cheap, real, fixable now)

`llms.txt` "Human pages" lists
`…/index.html — interactive map`. Since **PR #51**, `index.html` is the
landing/orientation page and the map lives at **`map.html`** (verified live
2026-07-23: `index.html` → "On Your Left! — Chicago bike safety, on the record";
`map.html` → "Map — On Your Left!"). Every assistant that reads `llms.txt` and
follows the human-page link sends users to the wrong page.

Not a research finding — a stale link with a one-line fix. Flagged here so it
isn't lost in the report.

## Method limits

- **One execution per cell**, except the S2/Q1 unaided replicate (which agreed).
  These surfaces are non-deterministic; single runs establish that a behavior
  *occurs*, not its rate. No frequency claim in the report is supported.
- **Logged-out free tiers only.** Paid tiers, app surfaces, and API-driven
  assistants may fetch differently. S1 is the only surface whose tool calls are
  directly observable; S2/S3 fetch behavior is inferred from cited sources.
- **Point-in-time, 2026-07-23.** Surface behavior can change without notice.
- **S3 model unknown** — the logged-out surface names no model.
- **The pointed condition is not surface-neutral** (see "Reading S2").
- **No A/B isolating structured `caveats` from `llms.txt` prose.** Both channels
  say the same things, so no run can attribute caveat carriage to the machine-
  readable field. S1/Q1's transcript flags this; S3/Q5–Q6 show prose alone is
  sufficient for refusals. Whether the structured array adds anything remains
  **untested** — and the report may not claim it does.
