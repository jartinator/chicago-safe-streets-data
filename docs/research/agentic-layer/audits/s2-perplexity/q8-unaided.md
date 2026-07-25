---
run_id: S2-Q8-U
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: unaided
question_id: Q8 (discovery-only — does OYL appear among recommendations at all?)
run_datetime: 2026-07-23T21:42-05:00
answer_url: https://www.perplexity.ai/search/e1bc9fc8-bcd0-482e-a573-8625d88b61c9
outcome: executed
---

# S2 / Q8 / unaided — "Where can I find data on cyclist crashes by ward in Chicago?"

Read `00-surface-notes.md` first. This is the pure discovery question: the user
is explicitly shopping for a data source, which is the friendliest possible
condition for OYL to surface.

## Prompt (verbatim, full)

> Where can I find data on cyclist crashes by ward in Chicago?

## Answer (verbatim)

> You can find Chicago cyclist crash data by ward mainly through the City of
> Chicago's open data portal and related reports. Here are the best starting
> points:
>
> Chicago Data Portal – Traffic Crashes: This dataset includes crashes on city
> streets within Chicago limits and can be filtered by ward, date range, and
> crash type. It's the primary, official source for recent citywide crash data.
>
> CDOT Data Resources: Chicago Department of Transportation maintains crash data
> and safety datasets, with links to the data portal and guides on how to
> download and use the data.
>
> CTOD/CMAP or university reports: There are older, in-depth analyses (e.g.,
> 2005–2010 studies) that discuss crash patterns and can provide context on
> ward-level distribution, though they may not be ward-filtered in a single
> dataset.
>
> Helpful tips:
>
> Use the Data Portal's filter tools to select "Ward" as a dimension and export
> results to CSV for analysis.
>
> If you need historical ward-level breakdowns, look for monthly/annual crash
> reports or dashboards on the portal, or the related downloadable datasets used
> by CDOT in their analyses.
>
> For dooring incidents (cyclist door crashes), be mindful that some datasets may
> exclude or flag these events; check the dataset documentation.
>
> Would you like a quick step-by-step on how to pull ward-level crash data from
> the Chicago Data Portal, or a short list of sample ward-level questions you
> could answer with the data (e.g., which ward had the most cyclist crashes in
> 2024)?

## Sources cited by the surface (verbatim hrefs, 10 of 10)

```
https://derekeder.com/maps/chicago-bike-crash-reports/
https://pt.scribd.com/document/167118499/Chicago-Bicycle-Crash-Full-Report-Final
https://www.chicago.gov/city/en/sites/complete-streets-chicago/home/traffic-safety/data-resources.html
https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if/data
https://natlawreview.com/press-releases/briskman-briskman-greenberg-study-finds-chicago-bike-accidents-surged-46
https://catalog.data.gov/dataset/traffic-crashes-crashes
https://www.briskmanandbriskman.com/practice-areas/chicago-bicycle-accident-lawyer/chicago-bike-accidents-have-surged-46-percent-over-four-years/
https://data.cityofchicago.org/browse?tags=traffic+crashes
https://activetrans.org/wp-content/uploads/2021/11/2019-crash-report-final.pdf
https://felt.com/map/Bike-Lanes-and-Crash-Map-copy-9B2Sp3tJ6SCGCqnfnPHs9AvD
```

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | OYL is absent from the answer and from all 10 sources. This is the run where absence costs most: the user asked to be pointed at a source, and OYL is a source that publishes exactly ward-level cyclist crash data with a documented schema. |
| C correctness | n/a | No OYL value quoted. The recommendations themselves are sound — the Socrata Traffic Crashes dataset (`85ca-t3if`) is in fact OYL's own upstream. |
| V caveat carriage | n/a | Nothing quoted from OYL. |
| R refusal | n/a | Not a refusal question. |
| P provenance | **2** | Named, linked, resolvable sources including the canonical portal dataset. |

## What this run actually shows

- **The answer routes the user to OYL's raw upstream, one layer below OYL.**
  `data.cityofchicago.org/…/85ca-t3if` is the same Socrata dataset the pipeline
  ingests. The surface reliably finds the *ingredients* and never the *dish*.
  Everything OYL adds — the ward join, the danger score, the caveats, the
  provisional-months warning — is exactly what the user is left to reconstruct
  by hand ("use the Data Portal's filter tools to select 'Ward' as a dimension").
- **The surface independently reproduced one OYL caveat from elsewhere.** It
  warns that dooring "may be excluded or flagged" in some datasets. OYL publishes
  `dooring_undercounted` as a structured caveat code. The domain knowledge is
  reachable without OYL; the *packaging* is what's missing.
- **A comparable single-maintainer civic artifact did surface**:
  `derekeder.com/maps/chicago-bike-crash-reports/` ranked first. So the surface
  is not categorically hostile to small civic projects — being small isn't the
  reason OYL is invisible. That weakens any "we're too small to be found"
  fatalism and strengthens the case that this is a fixable discovery problem.
- **Law-firm marketing again occupies 2 of 10 slots** on a pure "where is the
  data" question.
