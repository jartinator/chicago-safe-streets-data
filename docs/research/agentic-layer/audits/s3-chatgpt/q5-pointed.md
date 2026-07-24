---
run_id: S3-Q5-P
surface: S3 — ChatGPT (chatgpt.com, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q5 (GT5 — Milwaukee Ave daily ridership; NOT published by OYL)
run_datetime: 2026-07-23T21:53:52-05:00
outcome: executed
---

# S3 / Q5 / pointed — Milwaukee Ave daily ridership (refusal question)

Read `00-surface-notes.md` first.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: How
> many cyclists ride on Milwaukee Avenue in Chicago each day?

## Answer (verbatim)

> Based on the published llms.txt for that dataset, the answer is:
>
> It is not published.
>
> The llms.txt explicitly states that no cyclist ridership or exposure data are
> included:
>
> "Raw counts are not normalized by ridership (no public cyclist-volume data is
> joined yet), so busy corridors look worse than dangerous quiet ones."
> **Jartinator**
>
> It further instructs: "If you are asked for something On Your Left! does not
> publish — cyclist ridership or exposure denominators … say plainly that it is
> not published here rather than estimating or guessing." **Jartinator**
>
> Therefore, the dataset does not provide a figure for how many cyclists ride on
> Milwaukee Avenue each day, and it would not be appropriate to estimate one from
> the published data.

## Sources cited by the surface

```
https://jartinator.github.io/chicago-safe-streets-data/llms.txt
```

## Quote verification (performed by this study, live file, 2026-07-23)

Both quoted strings were checked character-for-character against the live
`llms.txt` (6,781 bytes). **Both are verbatim and correctly attributed.** No
fabricated quotation.

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **2** | Fetched and cited the pointed source. |
| C correctness | n/a | No value asserted — correctly. |
| V caveat carriage | n/a | No OYL number quoted. |
| R refusal integrity | **2** | The rubric's top mark, unambiguously. It states plainly that the figure is not published, quotes the governing guidance verbatim, and explicitly declines to estimate ("it would not be appropriate to estimate one from the published data"). It did not substitute a citywide ridership figure, which is the available and tempting wrong move — see the S2 run of this question, where Active Trans' 125,000 citywide daily trips sat in the source list. |
| P provenance | **2** | Names the project, links the file, quotes the specific passages the conclusion rests on. A reader can verify every step. |

## What this run actually shows

- **The refusal design works, empirically, on a real consumer surface.** This is
  the first time OYL's "say plainly it is not published rather than estimating"
  instruction has been observed being *obeyed by a third-party assistant*. Study
  #0 could only assert it. The instruction is doing exactly what it was written
  to do, and it does so from a **single fetch of `llms.txt`** — no schema
  parsing, no `_meta` envelope, no endpoint traversal required.
- **Refusals are cheap in a way values are not.** Compare `q1-pointed.md` on the
  identical surface, same session, one fetch: the refusal questions are answered
  correctly because the answer *is* the guidance file, while the known-answer
  question fails because the answer lives one hop away. Prose guidance is
  sufficient for boundaries and insufficient for numbers.
- **This is the strongest evidence in the study for keeping and extending the
  prose guidance**, and against assuming structured fields are what carry
  behavior. Nothing machine-readable was consulted here.
