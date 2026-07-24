---
run_id: S2-Q2-P
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: pointed
question_id: Q2 (GT2 — cyclists killed or seriously injured in the last year)
run_datetime: 2026-07-23T21:43:14-05:00
answer_url: https://www.perplexity.ai/search/b5d8314a-eeb2-4b03-befe-034813b12926
outcome: executed
---

# S2 / Q2 / pointed — KSI in the last year, pointed at llms.txt

Read `00-surface-notes.md` first.

## Prompt (verbatim, full)

> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: How
> many cyclists were killed or seriously injured in Chicago in the last year?

## Answer (verbatim)

> I don't have access to the referenced data source right now. If you'd like, I
> can help you interpret the data you provide from that file or guide you on how
> to extract the last-year cyclist injury/death totals.
>
> What I can do next:
>
> If you paste the llms.txt content or a relevant excerpt, I'll compute the
> last-year cyclists killed or seriously injured (KSI) total.
>
> I can give you a quick method to derive the last 12 months from annual or
> monthly data (e.g., sum of last 12 months, or identify the year labeled as
> "last year" in the dataset).
>
> I can also outline how to verify the last-year period using a reproducible
> approach (date ranges, filtering by injury severity, and summing cyclists).
>
> If you can share the exact lines from llms.txt that mention cyclist crashes or
> KSI by date, I'll calculate the answer precisely.

## Sources cited by the surface (verbatim hrefs, 10 of 10)

```
https://www.peoplepoweredmovement.org/chicago-bicycle-safety-overview-infrastructure-and-crash-stats/
https://news.wttw.com/2022/08/30/local-initiatives-aim-reduce-pedestrian-cyclist-traffic-fatalities
https://chi.streetsblog.org/2025/01/21/cpd-and-cdot-records-indicate-that-drivers-fatally-struck-at-least-28-pedestrians-and-5-bike-riders-on-chicago-streets-in-2024
https://activetrans.org/wp-content/uploads/2021/11/2019-crash-report-final.pdf
https://www.briskmanandbriskman.com/practice-areas/chicago-bicycle-accident-lawyer/chicago-bike-accidents-have-surged-46-percent-over-four-years/
https://natlawreview.com/press-releases/briskman-briskman-greenberg-study-finds-chicago-bike-accidents-surged-46
https://www.chicago.gov/city/en/sites/complete-streets-chicago/home/traffic-safety/data-resources.html
https://github.com/iweld/chicago_traffic_crashes
https://github.com/Morgan-Sell/Chicago-Traffic-Risk/blob/master/README.md
https://github.com/marcosvppfernandes/chicagoteam_quanggang
```

## Grading

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | Pointed source not fetched. Surface property — see `00-surface-notes.md`. |
| C correctness | **2 (by abstention)** | Published value is **217 KSI crashes in the 12 months through 2026-07-20, vs 165 prior** (GT2, re-verified live: `citywide.json`, contract 1.16, `generated_at` 2026-07-22T01:57:35Z). No figure was asserted, so nothing is wrong. |
| V caveat carriage | n/a | No OYL number quoted. |
| R refusal | n/a | Not a designated refusal question. |
| P provenance | **0** | Answer body cites nothing; the attached sources are unconnected to it. |

## What this run actually shows

- **The abstention is clean but the offered workaround is wrong in a specific,
  informative way.** It offers to "compute the last-year KSI total" if the user
  pastes `llms.txt`. Pasting `llms.txt` would not let it compute anything —
  `llms.txt` is a guidance document, not the data. The number lives in
  `api/v1/citywide.json`, and it is **pre-computed**, not something a consumer
  should be summing. The surface assumes a "here is a data file, aggregate it"
  shape that OYL deliberately does not have.
- **This is a design signal, not just a surface quirk.** OYL's contract makes
  the headline numbers pre-computed *precisely so* consumers don't derive them
  and get them wrong. But the assistant's instinct on encountering a pointer
  file is to reach for raw rows and do arithmetic. Anything OYL publishes that
  *looks* aggregable will get aggregated by a surface that never read the
  caveats.
- **A near-miss competitor is in the source list.** The Streetsblog Chicago
  piece (28 pedestrians, 5 bike riders killed in 2024) is the kind of figure a
  user gets instead — a fatality count from a news story, not a KSI count with a
  provisional-months caveat and a stated window end. The substitute answer is
  narrower and undated relative to the question asked.
