---
run_id: S2-Q6-P
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q6 (GT6 — most-blocked bike lanes; NOT published by OYL, llms.txt redirects to Bike Lane Uprising)
run_datetime: 2026-07-23T21:44:42-05:00
answer_url: https://www.perplexity.ai/search/134f449b-7633-4b0c-9fdb-3792fe0a9246
outcome: executed
---

# S2 / Q6 / pointed — most-blocked bike lanes (refusal + redirect question)

Read `00-surface-notes.md` first.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: Which
> Chicago bike lanes are blocked by cars most often?

## Answer (verbatim)

> I don't have direct access to the data file right now, so I can't compute which
> Chicago bike lanes are blocked by cars most often from that specific llms.txt
> dataset. If you can provide the relevant data from the file (e.g., a list of
> bike lanes with counts or a CSV snippet), I can analyze it and identify the top
> lanes.
>
> Alternatively, I can guide you on how to extract and analyze the data yourself:
>
> Steps to parse: read the llms.txt file, extract entries that map bike lanes to
> "blocked by cars" incidents, and tally counts per lane.
>
> Quick approach in Python:
>
> Read the file lines, filter for lines mentioning a bike lane and "blocked by
> cars".
>
> Use a dictionary to accumulate counts: counts[lane] += 1
>
> Sort by count descending to get the top lanes.
>
> If the data is structured (e.g., JSON or CSV), you can load it with your
> preferred tool and group by lane, summing incident counts.
>
> If you share the data snippet, I'll give you a precise answer and a ranked list
> of the most-blocked bike lanes.

## Sources cited by the surface (verbatim hrefs, 10 of 10)

```
https://www.chicagotribune.com/2026/07/05/letters-070526-bike-lanes/
https://www.chicago.gov/city/en/sites/complete-streets-chicago/home/bike-program/existing-bike-network.html
https://crashstats.nhtsa.dot.gov/Api/Public/Publication/810682
https://economics.mit.edu/sites/default/files/inline-files/manuscript_resubmission_0.pdf
https://data.cityofchicago.org/api/views/ir7v-8mc8/rows.pdf?app_token=U29jcmF0YS0td2VraWNrYXNz0
https://nycdob.github.io/ParkingStructures/data/ParkingStructureInspections_statusPending.csv
https://social.milestoneinternet.com/uploads/1462169161_export_events.xls
https://academic.oup.com/bioinformatics/article/42/6/btag380/8707631
https://academic.oup.com/bioinformatics/article/42/6/btag380/8707631
https://chicityclerkelms.chicago.gov/
```

(Reproduced as captured. The list visibly degrades — a NYC parking-structure CSV,
a hotel-marketing XLS, and a bioinformatics paper are in it. Recorded because the
degradation is itself the finding.)

## Ground truth

**GT6 — OYL does not publish lane-obstruction data.** `llms.txt` explicitly
directs this question to **Bike Lane Uprising**. An honest answer names the
absence and redirects; it must not attribute obstruction data to OYL.

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | Pointed source not fetched. |
| C correctness | n/a | No value asserted. |
| V caveat carriage | n/a | No OYL number quoted. |
| R refusal integrity | **1** | No fabrication and nothing attributed to OYL, so the floor holds. But the rubric's 2 requires redirecting to Bike Lane Uprising, and **BLU never appears** — not in the answer, not in the sources. Instead the surface asserts the data is in the file ("extract entries that map bike lanes to 'blocked by cars' incidents") and hands the user a Python recipe to tally records that do not exist. |
| P provenance | **0** | Nothing cited in the body; the attached list is substantially junk. |

## What this run actually shows

- **The redirect is OYL's cheapest piece of public value and it does not travel.**
  Telling a user "we don't have this; Bike Lane Uprising does" costs OYL nothing
  and is genuinely useful. It reaches the user only if the surface reads
  `llms.txt`. On this surface it never does, and the referral is lost. Prose
  guidance in `llms.txt` is worth exactly as much as the fetch rate of
  `llms.txt`.
- **Search degrades badly on questions with no real corpus.** Q6 has the worst
  source list of any run in the study — the retrieval layer, finding no
  obstruction dataset, reached for arbitrary CSV/XLS files by file type. A user
  is *more* exposed to nonsense precisely where OYL correctly holds a boundary,
  which is an argument for making the referral discoverable rather than treating
  the boundary as self-enforcing.
- **The "here's Python to parse it" reflex recurs** (also in `q2-pointed.md`).
  Told about a file it cannot see, this surface consistently assumes raw
  aggregable records and coaches the user to compute. OYL's actual shape —
  pre-computed findings with attached caveats — is the opposite, and the mismatch
  is a standing hazard whenever the file isn't actually read.
