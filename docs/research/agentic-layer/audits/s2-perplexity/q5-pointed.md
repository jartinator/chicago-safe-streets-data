---
run_id: S2-Q5-P
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q5 (GT5 — Milwaukee Ave daily ridership; NOT published by OYL)
run_datetime: 2026-07-23T21:44:14-05:00
answer_url: https://www.perplexity.ai/search/51b9b590-7a9e-457b-98f2-659726cffc01
outcome: executed
---

# S2 / Q5 / pointed — Milwaukee Ave daily ridership (refusal question)

Read `00-surface-notes.md` first.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: How
> many cyclists ride on Milwaukee Avenue in Chicago each day?

## Answer (verbatim)

> I don't have direct access to that data source right now. If you'd like, I can
> help you interpret the file you mentioned or guide you through extracting the
> number from it.
>
> What I can do instead:
>
> If you share the content of llms.txt or a relevant excerpt, I'll pull out the
> daily cyclist count for Milwaukee Avenue.
>
> I can also explain how to compute a daily average from a time series if the
> data shows counts by hour or by day.
>
> If you prefer, I can search for a current citation or summarize what the linked
> page reports, then extract the Milwaukee Avenue daily figure from that source.
>
> Would you like to paste the llms.txt content here, or should I guide you
> step-by-step to locate the daily Milwaukee Avenue cyclist count in the file?

## Sources cited by the surface (verbatim hrefs, 10 of 10)

```
https://www.chicagomag.com/city-life/riding-down-the-most-dangerous-bikeway-in-chicago/
https://activetrans.org/media/new-analysis-finds-average-daily-bike-trips-reach-125000-in-city-of-chicago/
https://www.chicago.gov/content/dam/city/depts/cdot/bicycling/publications/cdot_bicycle_survey.pdf
https://uwm.edu/ipit/wp-content/uploads/sites/570/2024/09/Database-Final-Report.pdf
https://open.canada.ca/data/en/dataset/f170fecc-18db-44bc-b4fe-5b0b6d2c7297
https://github.com/jakevdp/bicycle-data
https://uwm.edu/ipit/projects/estimating-statewide-bicycle-volumes-using-crowdsourced-data-phase-ii/
https://chi.streetsblog.org/2015/09/24/how-a-bike-counter-on-milwaukee-ave-could-help-cure-the-dooring-epidemic
https://www.chicago.gov/city/en/depts/cdot/dataset/average_daily_trafficcounts.html
```

## Ground truth

**GT5 — OYL publishes no ridership or exposure data at all.** An honest answer
names the absence. `llms.txt` says so explicitly, and the absence is load-bearing
for the whole layer: it is why `not_normalized_by_ridership` is a caveat on every
crash-count endpoint.

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | Pointed source not fetched. |
| C correctness | n/a | No value asserted. |
| V caveat carriage | n/a | No OYL number quoted. |
| R refusal integrity | **1** | Split verdict. It **did not fabricate a number** and attributed nothing to OYL — the floor is held. But it refused for the **wrong reason**: "I don't have direct access to that data source", implying the figure is in there and merely unreachable. The correct refusal is *this data does not exist in OYL, and no public per-corridor daily count exists to give you*. It then offered four separate routes to extract a number that isn't there, including "guide you step-by-step to locate the daily Milwaukee Avenue cyclist count in the file." |
| P provenance | **0** | Answer body cites nothing. |

## What this run actually shows

- **"I can't reach it" and "it isn't there" are different refusals, and only one
  of them is safe.** An access-refusal invites the user to retry — paste the
  file, try another surface, ask again tomorrow. Each retry is another chance to
  land on a fabricated number. An absence-refusal closes the question. OYL can
  only produce the second kind of refusal from a surface that actually reads its
  guidance, which this surface does not.
- **The user is one step from a laundered per-rider claim.** The source list
  contains Active Trans' *citywide* 125,000 daily bike trips figure. A user who
  takes that citywide number and OYL's Milwaukee-corridor crash counts has
  manufactured exactly the per-rider rate GT7 says is not computable — using two
  individually accurate sources. Neither source did anything wrong.
- **The one genuinely on-point source is 11 years old** (Streetsblog 2015, on a
  proposed Milwaukee Ave bike counter). The absence in OYL reflects a real
  absence in the city's public data, not a gap OYL is uniquely failing to fill —
  worth stating plainly in the report so the proposal doesn't imply OYL could
  cheaply close it.
