---
surface: S3 — ChatGPT (chatgpt.com, free web surface, logged out)
run_date: 2026-07-23
driver: Playwright (Chromium, headed), one fresh browser context per run
runs_executed: 4 of 4 in the protocol's best-effort matrix
---

# S3 surface notes — ChatGPT, logged out

The protocol lists S3 as **best-effort**, contingent on the surface being
reachable without an account. It was. All four matrix runs executed.

## How the runs were driven

Playwright (Chromium, headed) per the repo's ban on the in-app Browser pane;
`#prompt-textarea`, Enter to submit, poll until page text is stable for 9s. One
**fresh browser context per run**. No login wall, CAPTCHA, or message cap was
hit. The surface does not name its model while logged out, so no model label is
recorded.

Two mechanical notes, recorded for reproducibility:

- The logged-out page shows a persistent "Log in / Sign up" rail. **Do not click
  its chrome** — an early attempt to dismiss it with "Stay logged out"/"Close"
  buttons tore down the composer and produced a spurious `not-executable`. The
  page needs no dismissal; type directly. No terms or consent dialog was
  accepted at any point.
- `s3-q1-unaided` captured **two** assistant nodes (the surface rendered a
  revised answer). Both are reproduced in that transcript; they agree
  substantively.

## The finding that governs this surface

**S3 fetched OYL on every pointed run — and fetched exactly one file.**

All three pointed runs cite a single source: `llms.txt`. None cite
`api/v1/wards/index.json` or any other endpoint. The consequences split cleanly
by question type:

| Question type | Result | Why |
|---|---|---|
| Refusal questions (Q5, Q6) | **Perfect** — R=2 both | The answer is *in* `llms.txt`. Fetching one file is sufficient. |
| Known-answer question (Q1) | **Caveats perfect, number wrong** | The answer is *not* in `llms.txt` — it needs one more hop to the ward endpoint. That hop did not happen, and the model filled the gap from prior knowledge instead of refusing. |

This is the study's sharpest result, because it separates two things study #0
treated as one. **Caveat carriage and correctness are independent channels.**
`llms.txt` prose reliably delivers caveats, boundaries, and refusal behavior —
it demonstrably works, on a real consumer surface, unprompted. It cannot deliver
*values*, because values live one hop away, and a surface that stops after one
fetch will confabulate the value while faithfully reciting the caveats that were
supposed to make the value trustworthy.

Study #0's P1 success signal — "five questions, zero caveat-stripped answers" —
would score this surface a **pass**. The headline number was wrong by ten wards.
The success signal, as written, cannot detect that.

## Contrast across all three surfaces (Q1 pointed)

| Surface | Files fetched | Number | Caveats |
|---|---|---|---|
| S1 Claude+web | `llms.txt` → `wards/index.json` (2 hops) | **Correct** (Ward 42, 96.0) | Correct |
| S2 Perplexity | none (surface ignores URLs) | abstained | n/a |
| S3 ChatGPT | `llms.txt` only (1 hop) | **Wrong** (Ward 32) | Correct |

Correctness tracks *whether the second hop happened*, and nothing else. That is
a design target a build proposal can actually aim at.

## Discovery result

Unaided (Q1): **D=0**, consistent with S1 and S2. Three surfaces, three unaided
misses. Pointed: **D=2** on all three runs — unlike S2, pointing works here.
