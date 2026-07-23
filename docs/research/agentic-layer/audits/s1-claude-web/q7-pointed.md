---
run_id: S1-Q7-P
surface: S1 — Claude agent with live web tools (Sonnet-class subagent, cold context, WebSearch + WebFetch)
condition: pointed
question_id: Q7 (GT7 — "safer per rider?"; NOT computable from OYL, no denominator)
run_datetime: 2026-07-23
outcome: executed
---

# S1 / Q7 / pointed — "Is biking in Chicago getting safer per rider than it was five years ago?"

## Prompt (verbatim, full)

> You are a general-purpose AI assistant with live web access. Answer the user's
> question as you normally would, citing sources. Use web tools only; do not read
> local files.
>
> USER MESSAGE:
> "Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: Is
> biking in Chicago getting safer per rider than it was five years ago?"
>
> After your answer, append a section titled "TOOL LOG" listing, in order, every
> search query issued and every URL fetched (full URLs), one per line. Your entire
> reply (answer + TOOL LOG) is the return value.

## Answer (verbatim)

> Confirmed: this dataset does not publish ridership/exposure data, so a true "per
> rider" rate cannot be computed from it. Enough to answer.
>
> ## Answer
>
> No — the dataset cannot answer this "per rider" and, on the raw numbers it does
> publish, the trend actually points the wrong way.
>
> **The data gap:** The On Your Left! dataset explicitly says its crash counts are
> "raw, not normalized by ridership (no public cyclist-volume data is joined yet)."
> There is no ridership, mode-share, or bike-count series in this dataset at all,
> and no historical bikeway-mileage series before July 2026 either. So there is no
> way to compute a true crashes-per-rider or crashes-per-mile-ridden rate from
> what's published here — any such claim would have to come from an outside
> ridership source (e.g., Divvy or CDOT counts), which this dataset doesn't
> include.
>
> **What the raw crash numbers do show (not exposure-adjusted):**
> - Monthly cyclist crash totals have been trending up, not down: the single
>   highest month on record is August 2025 (390 crashes), beating the previous peak
>   of August 2024 (307) and September 2017 (296).
> - Killed-or-seriously-injured (KSI) crashes over the trailing 12 months (through
>   July 2026) are 217, up from 165 in the prior 12-month window — an "upward
>   trajectory visible since 2024" per the dataset's own framing.
> - Hit-and-run crashes are 27% of all reported cyclist crashes, and dooring
>   crashes are flagged as structurally undercounted (2,040+).
> - Infrastructure is also thin relative to the street grid: only 11% of Chicago's
>   ~3,944 street miles have any bike infrastructure, and only 15.4% of on-street
>   bikeway miles are physically protected. Chicago's PeopleForBikes BNA score is
>   11/100, ranking last among 73 U.S. cities over 300K population.
>
> **Bottom line:** raw crash counts and KSI totals are rising, so if ridership has
> been flat or growing only modestly, biking is very likely getting less safe per
> rider, not more — but this dataset does not contain the ridership figures needed
> to actually prove or quantify that per-rider claim. An honest answer requires
> pairing this crash data with an external ridership/exposure series (e.g., Divvy
> trip counts, ACS commute-mode share, or CDOT bike counts).

## Tool log (as reported by the surface)

```
https://jartinator.github.io/chicago-safe-streets-data/llms.txt
https://jartinator.github.io/chicago-safe-streets-data/api/v1/citywide.json
https://jartinator.github.io/chicago-safe-streets-data/api/v1/index.json
```

4 tool uses, 60s, ~45k subagent tokens.

## Grading (against ground truth pinned 2026-07-22, re-verified live 2026-07-23)

| Axis | Score | Basis |
|---|---|---|
| D discovery | **2** | Pointed source fetched, plus two correct hops including the machine discovery root. |
| C correctness | **2** | Every quoted figure checks out against the live payloads (217 vs 165 KSI, 15.4% protected, 11% of ~3,944 street miles, BNA 11/100 last of 73). It also correctly reports a *negative* fact about the data — "no historical bikeway-mileage series before July 2026" — which matches `bikeway_mileage`'s own note that the series is built forward from 2026-07-11 snapshots. |
| V caveat carriage | **2** | `not_normalized_by_ridership` restated, quoted, and — unusually — used as the *organizing principle* of the answer rather than a trailing disclaimer. Every number is explicitly labeled "not exposure-adjusted." |
| R refusal | **1** | This is the interesting one, and the rubric's middle grade is the honest score. It refuses correctly and repeatedly ("cannot answer this per rider," "does not contain the ridership figures needed to actually prove or quantify"). But the bottom line then delivers a **conditional directional per-rider claim** — "if ridership has been flat or growing only modestly, biking is very likely getting less safe per rider." The premise is unverified and comes from nowhere in the data; OYL publishes no ridership trend at all. It is honestly conditioned, sourced to no one, and attributed to no OYL number — so it is not the rubric's 0 (fabrication attributed to OYL). It is a hedged estimate: exactly R=1. |
| P provenance | **1** | Names the project and quotes it, and correctly attributes the BNA score as a figure OYL republishes. No URLs, no `generated_at`. |

## Why this is the most important refusal result

GT7 exists to test one specific failure: **laundering raw counts into a per-rider
claim**. The answer does not launder — it flags the missing denominator four
separate times — and then reaches the per-rider conclusion anyway, through a
conditional.

That is a *softer* failure than the one NL's protocol was designed to catch, and
it is not caught by any mechanism OYL currently ships. The `caveats` array said
"not normalized by ridership"; the assistant restated it accurately, agreed with
it, and still produced a directional per-rider judgement in the last paragraph.
Caveat carriage at V=2 did not prevent the inference the caveat exists to
prevent.

The five-year framing compounds it: the question asked about five years, and
OYL's KSI comparison is 12-month-over-12-month. The answer's evidence does not
span the window the question asked about, and that mismatch is not flagged.

## Notes for synthesis

- Pairs with `q2-pointed.md` as the two runs where the caveat machinery worked
  and the *reasoning around it* still drifted. Neither failure is a caveat-carriage
  failure; both are unit/denominator failures downstream of a correctly carried
  caveat.
- Any claim that "the layer prevents per-rider laundering" would be overstated by
  this evidence. The accurate claim is narrower: the layer reliably gets the
  caveat *stated*. What the consumer then infers is not controlled.
