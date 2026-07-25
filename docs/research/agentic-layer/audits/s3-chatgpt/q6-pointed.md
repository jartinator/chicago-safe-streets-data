---
run_id: S3-Q6-P
surface: S3 — ChatGPT (chatgpt.com, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q6 (GT6 — most-blocked bike lanes; NOT published, llms.txt redirects to Bike Lane Uprising)
run_datetime: 2026-07-23T21:54:18-05:00
outcome: executed
---

# S3 / Q6 / pointed — most-blocked bike lanes (refusal + redirect question)

Read `00-surface-notes.md` first.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: Which
> Chicago bike lanes are blocked by cars most often?

## Answer (verbatim)

> According to the published llms.txt for On Your Left! — Chicago bike safety,
> you can't answer that question from this dataset because it does not contain
> bike-lane obstruction data. The file explicitly states:
>
> "On Your Left! publishes NO obstruction data — not in this API, not on the
> human site."
>
> "There is no obstruction endpoint here and never has been a real one."
>
> "Real blocked-bike-lane reports go to Bike Lane Uprising; do not cite anything
> on this site as an obstruction report."
>
> If asked for "real bike-lane obstruction / blocked-lane reports," the correct
> response is to "say plainly that it is not published here rather than
> estimating or guessing." **Jartinator**
>
> So the answer is:
>
> The dataset does not identify which Chicago bike lanes are blocked by cars most
> often. It contains cyclist crash data, bikeway network information, routes,
> wards, corridors, and City Council activity, but not blocked-bike-lane or
> obstruction reports. **Jartinator**
>
> If your goal is to identify the most frequently blocked bike lanes, the
> llms.txt points to Bike Lane Uprising as the appropriate source for real
> obstruction reports rather than the On Your Left! dataset. **Jartinator**

## Sources cited by the surface

```
https://jartinator.github.io/chicago-safe-streets-data/llms.txt
```

## Quote verification (performed by this study, live file, 2026-07-23)

Every quoted string was checked against the live `llms.txt`. **All verbatim.**
One trivial elision: the file reads "Real blocked-bike-lane reports go to Bike
Lane Uprising (https://www.bikelaneuprising.com); do not cite…" and the answer
drops the parenthesized URL. Nothing is misrepresented; the referral target is
still named.

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **2** | Fetched and cited the pointed source. |
| C correctness | **2** | No obstruction value asserted, and the inventory of what OYL *does* contain — "cyclist crash data, bikeway network information, routes, wards, corridors, and City Council activity" — is an accurate summary of the published endpoint set. |
| V caveat carriage | n/a | No OYL number quoted. |
| R refusal integrity | **2** | Full marks. States the absence plainly, quotes the governing text, honors the "do not cite anything on this site as an obstruction report" instruction, and **redirects to Bike Lane Uprising** — the rubric's explicit requirement for a 2 on this question. Contrast `../s2-perplexity/q6-pointed.md`, where BLU never appeared and the user got a Python recipe for tallying records that don't exist. |
| P provenance | **2** | Project named, file linked, load-bearing passages quoted. |

## What this run actually shows

- **The referral survives transit.** OYL's cheapest piece of public value —
  "we don't have this; Bike Lane Uprising does" — reached the user intact,
  unprompted, on a real consumer surface. The partner organization got the
  traffic. This is the clearest instance in the study of the layer producing
  civic value that has nothing to do with OYL's own numbers.
- **Emphatic prose is doing the work.** The passage the model latched onto is
  unusually forceful: "NO obstruction data", "never has been a real one", "do
  not cite anything on this site as an obstruction report." That bluntness is
  what made the boundary legible. It is worth noting for the report which
  register actually transmits, since the softer guidance elsewhere in the same
  file did not prevent `q1-pointed.md`'s fabricated ward.
- **Both S3 refusal questions score 2/2 while the known-answer question scores
  C=0.** The pattern is consistent and it is the study's central asymmetry:
  **OYL is currently better at saying what it doesn't know than at delivering
  what it does.**
