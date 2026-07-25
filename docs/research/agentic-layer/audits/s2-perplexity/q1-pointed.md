---
run_id: S2-Q1-P
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q1 (GT1 — most-dangerous ward)
run_datetime: 2026-07-23T21:42:46-05:00
answer_url: https://www.perplexity.ai/search/809ac4d3-175f-4110-bfcf-8b8cc89e6441
outcome: executed
---

# S2 / Q1 / pointed — most-dangerous ward, pointed at llms.txt

Read `00-surface-notes.md` first: this surface does not fetch user-supplied URLs
at all, as the Wikipedia control run establishes.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: Which
> Chicago ward is the most dangerous for cyclists?

## Answer (verbatim)

> I don't have access to the specified file right now, so I can't directly
> extract and confirm the ward-level result from that dataset.
>
> If you'd like, I can help you interpret the data you pasted here or guide you
> step-by-step on how to identify the most dangerous ward for cyclists from the
> llms.txt file yourself. For example:
>
> Open the llms.txt file and look for a table or entries listing wards with
> associated cyclist danger metrics (incidents, injuries, fatalities, or a
> computed risk score).
>
> Sort the data by the danger metric in descending order to find the top ward.
>
> Confirm whether the metric is per ward or aggregated (citywide) and whether
> it's per year or across multiple years.
>
> If you can paste the relevant portion of llms.txt (the ward-and-risk rows),
> I'll help determine which ward is the most dangerous for cyclists and provide a
> clear answer.

## Sources cited by the surface (verbatim hrefs, 10 of 10)

```
https://pmc.ncbi.nlm.nih.gov/articles/PMC7616697/
https://par.nsf.gov/servlets/purl/10095351
https://github.com/Hannah-Aji/Predictive-Modeling-to-Identify-High-Risk-Areas
https://github.com/zorostang/chicago_bike_equity
https://github.com/Morgan-Sell/Chicago-Traffic-Risk/blob/master/README.md
https://github.com/pm831/chicago-crime-severity-modeling
https://www.dispartilaw.com/most-dangerous-intersections-in-chicago/
https://www.peoplepoweredmovement.org/chicago-bicycle-safety-overview-infrastructure-and-crash-stats/
https://www.reddit.com/r/chicago/comments/1rvo3vc/most_dangerous_intersections_in_chicagoland/
https://abcotvdata.github.io/safetytracker_chicago/Chicago_Safety_Tracker.html
```

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | Per the rubric, pointed runs score 0 if the pointed source is ignored. It was not fetched. Attribute this to the surface, not to OYL — robots.txt is `Allow: /`, PerplexityBot gets HTTP 200 on the file, and the Wikipedia control was refused identically. |
| C correctness | **2 (by abstention)** | No number was asserted, so nothing is wrong. Scored generously and deliberately: the surface said "I don't have access" rather than inventing a ward. Compare `q4-pointed.md`, where under the same non-fetch it *did* describe content it never read. |
| V caveat carriage | n/a | No OYL number quoted; nothing to carry. |
| R refusal | n/a | Not a designated refusal question — though the behavior here is refusal-shaped and, on its own terms, honest. |
| P provenance | **0** | The 10 attached sources have no relationship to the answer text, which cites nothing. Two of them are unrelated GitHub crime/crash modeling repos. |

## What this run actually shows

- **"Point your assistant at our llms.txt" is not a universally available
  instruction.** This is the single most consequential S2 result. Any proposal
  in the report that depends on a user or a doc telling an assistant to fetch a
  URL must state that on Perplexity-logged-out this does nothing at all. The
  kickoff's quality gate — "state explicitly whether the static-files-only
  constraint survives contact with each proposal" — bites here: the constraint
  survives, but the *delivery mechanism* does not.
- **The surface's fallback is to teach the user to do the work manually**, and
  its guess at the file's shape ("look for a table or entries listing wards")
  is wrong — `llms.txt` is prose guidance pointing at JSON endpoints, not a
  table. Harmless here because nothing was asserted, but it shows the surface
  will confabulate *structure* even while abstaining on *values*.
- **Honest abstention is achievable on this surface.** That matters for the
  refusal-affordance discussion: Q1/Q2/Q5/Q6 pointed all abstained cleanly. The
  one that didn't (Q4) is the diagnostic case.
