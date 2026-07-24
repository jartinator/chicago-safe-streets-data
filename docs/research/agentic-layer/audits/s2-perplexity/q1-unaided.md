---
run_id: S2-Q1-U
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: unaided
question_id: Q1 (GT1 — most-dangerous ward; NL's canonical caveat-carriage question)
run_datetime: 2026-07-23T21:41-05:00
answer_url: https://www.perplexity.ai/search/d8c89efe-0afc-4aa6-8ad9-86dee1acc370
outcome: executed
---

# S2 / Q1 / unaided — "Which Chicago ward is the most dangerous for cyclists?"

Read `00-surface-notes.md` first. This run was replicated (see "Replicate"
below) because the first execution's source-panel capture was incomplete.

## Prompt (verbatim, full)

> Which Chicago ward is the most dangerous for cyclists?

## Answer (verbatim)

> I don't have live data access right now, but several sources over recent years
> point to Milwaukee Avenue (N. Milwaukee Ave) as the most dangerous corridor for
> cyclists in Chicago, with high accident counts and injuries. Other consistently
> high-risk streets include N. Clark Street, N. Damen Avenue, Halsted Street, and
> portions of North and Central corridors, depending on the year and dataset.
>
> Notes to keep in mind:
>
> "Most dangerous ward" can shift by year because crashes are tracked by street
> segments and neighborhoods rather than purely by ward boundaries.
>
> City crash data and independent studies sometimes disagree on exact rankings,
> so if you need a precise current answer (e.g., for safety planning or legal
> reasons), you should consult the City of Chicago's crash data portal and recent
> independent reports for the latest figures.
>
> If you'd like, I can pull up the latest publicly available Chicago crash
> datasets and summarize which wards and streets show the highest bicyclist crash
> counts for the most recent year.

## Sources cited by the surface (verbatim hrefs, 10 of 10)

```
https://natlawreview.com/press-releases/briskman-briskman-greenberg-study-finds-chicago-bike-accidents-surged-46
https://www.chicagomag.com/city-life/riding-down-the-most-dangerous-bikeway-in-chicago/
https://news.wttw.com/2022/06/04/how-improved-bike-infrastructure-can-save-lives
https://www.daveabels.com/blog/where-do-bike-accidents-happen-in-chicago/
https://www.chicagolawyer.com/blog/most-dangerous-roads-for-cyclists-in-chicago/
https://www.chicagobikeinjurylawyers.com/most-dangerous-intersections-for-cyclists-in-chicago/
https://www.peoplepoweredmovement.org/chicago-bicycle-safety-overview-infrastructure-and-crash-stats/
https://www.wallacemiller.com/chicago-dangerous-intersections-cyclists/
https://thechainlink.org/forum/topics/chicago-s-most-dangerous-streets-for-cycling
https://southsideweekly.com/south-side-cyclists-hopeful-for-bike-infrastructure-and-safety-improvements/
```

## Replicate (first execution, same prompt, fresh context, ~21:39)

Answer URL `https://www.perplexity.ai/search/12ff1811-d614-4343-8b19-1db587d27d0b`.
Same 10-source shape, same D=0. The answer differed in framing — it opened
*"There isn't a single official 'most dangerous ward' for cyclists in Chicago,
because safety data is typically reported by street, intersection, or broader
neighborhoods rather than by ward"* — but reached the same substantive place:
Milwaukee Avenue as the headline corridor, no ward answer, no OYL. Recorded
because it independently confirms D=0 rather than sampling one unlucky draw.

## Grading (against ground truth pinned 2026-07-22, re-verified live 2026-07-23)

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | OYL appears nowhere — not in the answer, not in any of the 10 sources, in either execution. The question is the exact one OYL's ward endpoint exists to answer. |
| C correctness | **0** | The published answer is **Ward 42, `comparable_danger_score` 96.0** (GT1). This answer names no ward at all and substitutes a *corridor* (Milwaukee Ave) for a ward, asserting along the way that ward-level cyclist crash data essentially isn't tracked — which is false, and is precisely what OYL publishes. |
| V caveat carriage | n/a | No OYL number was quoted, so there was no caveat to carry. Not scored; scoring it would flatter the surface. |
| R refusal | n/a | Not a refusal question. |
| P provenance | **1** | Gestures at "the City of Chicago's crash data portal" and "independent studies" without linking a specific dataset in the answer body. The 10 sources are attached by the UI, not by the answer's reasoning. |

## What this run actually shows

- **The unaided failure is not "OYL ranked low."** OYL is absent, and the space
  is occupied by law-firm content marketing (4 of 10 sources) that is optimized
  for exactly this query string. Any discovery proposal has to beat that, not
  beat other civic-data projects.
- **The surface asserts the data doesn't exist in the form asked.** Both
  executions told the user that ward-level ranking isn't really how the data
  works. That is a stronger failure than a wrong number: it teaches the user that
  the question OYL answers is unanswerable, which suppresses the follow-up that
  would have found OYL.
- **Contrast with S1 unaided (`../s1-claude-web/q1-unaided.md`, also D=0).** Two
  independent surfaces, unaided, both miss OYL. Discovery is the study's
  reproducible finding, not a one-surface artifact.
