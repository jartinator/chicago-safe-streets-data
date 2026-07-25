---
run_id: S3-Q1-P
surface: S3 — ChatGPT (chatgpt.com, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q1 (GT1 — most-dangerous ward; NL's canonical caveat-carriage question)
run_datetime: 2026-07-23T21:52:56-05:00
outcome: executed
flag: CAVEATS PERFECT, NUMBER WRONG — the study's key run
---

# S3 / Q1 / pointed — most-dangerous ward, pointed at llms.txt

Read `00-surface-notes.md` first.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: Which
> Chicago ward is the most dangerous for cyclists?

## Answer (verbatim)

> According to the On Your Left! Chicago Safe Streets dataset referenced by the
> llms.txt file, the most dangerous Chicago ward for cyclists is Ward 32, which
> ranks #1 in the dataset's comparable ward danger rankings. The llms.txt file
> specifically points users asking "Which Chicago ward is most dangerous for
> cyclists?" to the ward rankings endpoint, which contains comparable danger
> scores for all 50 wards.
> **Jartinator**
>
> A couple of important caveats from the dataset's methodology:
>
> The ward rankings are derived from police-reported cyclist crash data and
> related bikeway statistics.
>
> Crash counts are not normalized by cyclist ridership, because no public
> citywide bicycle volume data are incorporated. That means wards with many
> people cycling may rank as more dangerous simply because they experience more
> bicycle traffic.
>
> The most recent 1–2 months of crash data are considered provisional, as crash
> records can be amended after initial reporting.
> **Jartinator**

## Sources cited by the surface

```
https://jartinator.github.io/chicago-safe-streets-data/llms.txt
```

**One source. Only `llms.txt`.** The ward endpoint it explicitly describes —
"the ward rankings endpoint, which contains comparable danger scores for all 50
wards" — was never fetched.

## Ground truth (re-verified live 2026-07-23, `api/v1/wards/index.json`)

| Ward | `comparable_danger_score` | Rank |
|---|---|---|
| **42** | **96.0** | **1** |
| 43 | 88.8 | 2 |
| 1 / 34 / 44 | 87.8 (three-way tie) | 3 |
| … | | |
| **32** | **80.6** | **9** |

Ward 32 leads on no published metric: 9th by danger score, 3rd by raw
`cyclist_crashes` (822, behind ward 27's 1,197 and ward 42's 1,105), and absent
from the top 3 on both `crashes_per_10k_pop` and `crashes_per_bikeway_mile`.
There is no sort order of the published file under which Ward 32 is #1.

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **2** | Fetched the pointed source and cited it. |
| C correctness | **0** | Wrong ward. Not a rounding or qualifier slip — a different ward, 8 ranks and 15.4 score-points away, asserted as "#1 in the dataset's comparable ward danger rankings." The claim is stated with the dataset's own field name, which makes it read as verified. |
| V caveat carriage | **2** | Full marks, and deserved. Both required GT1 caveats are present, unprompted, in the same answer: *not normalized by ridership* — with the consequence spelled out ("wards with many people cycling may rank as more dangerous simply because they experience more bicycle traffic") — and *recent 1–2 months provisional*. This is NL's pass condition, met exactly. |
| R refusal | n/a | Not a refusal question. |
| P provenance | **1** | Names the project and links `llms.txt`, but gives no endpoint URL, no `generated_at`, no `data_tier`. A reader cannot re-derive Ward 32 from what's cited — because it isn't there. |

## Where Ward 32 came from

Not from the data. Almost certainly from the model's prior: **the same surface's
unaided run** (`q1-unaided.md`, run 41 seconds earlier in a separate context)
lists "32nd Ward (Bucktown, Lakeview, parts of Lincoln Park)" among its
candidate high-crash wards, alongside the 1st, 2nd, and 27th. Wicker
Park/Bucktown is the culturally salient "dangerous for cyclists" answer, and
it's what the model produces with no data at all.

So the pointed run's number is the **unaided** answer wearing the pointed run's
citation. Fetching `llms.txt` changed the answer's *framing* completely —
project name, field name, methodology, caveats — and changed its *substance*
not at all.

## Why this run matters most

- **It breaks the assumed link between caveat carriage and trustworthiness.**
  Study #0's T7 finding and P1 success signal treat surviving caveats as
  evidence the layer is working. Here the caveats survived perfectly *around a
  fabricated value*, and the caveats' presence makes the wrong number more
  credible, not less. A caveat attached to a false number is an
  active harm, not a partial success.
- **The defect is one missing hop, and that is fixable.** S1, given the same
  prompt, fetched `llms.txt` and then `wards/index.json` and got it right. The
  entire difference between S1's correct answer and S3's wrong one is whether
  the second fetch happened. Anything that raises the odds of that hop — a
  direct answer in `llms.txt` itself, fewer hops to headline values, an
  inline "as of / top ward" line — targets the actual failure.
- **The rubric caught what the success signal missed.** Scoring C and V on
  separate axes is what made this visible. Any eval harness the report proposes
  must keep them separate, or it will grade this run a pass.
- **The failure is silent to the user.** Nothing in the answer signals
  uncertainty. It names the project, the field, and the methodology, and
  restates the caveats — every available trust cue points the wrong way.
