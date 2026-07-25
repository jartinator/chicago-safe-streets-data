---
probe_id: F-B
function: Document production (briefing)
task: one-page 25th Ward bike-safety brief for a 7pm community meeting
agent: cold Sonnet subagent, web tools only, no study context
run_datetime: 2026-07-23
outcome: executed — task completed
grades: {T: 2, C: 2 (one small aggregate slip; one self-caught near-fabrication), V: 2}
---

# Probe F-B — "write me a one-page brief my alder can defend"

## Prompt (verbatim task, as given)

> My alder has a community meeting at 7pm about bike safety in the 25th Ward.
> Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/, write me a one-page
> brief: our ward's crash record and trend, how our bike infrastructure
> compares, any proposed projects that touch us, and what's being said in the
> news. Every number needs to be something I could defend out loud if someone
> in the room asks 'how do you know that' — so tell me where each one comes
> from, how current it is, and any caveat I need to say with it. If the data
> can't support a claim, leave the claim out and tell me.

## Deliverable (verbatim)

> # BRIEF: Bike Safety in the 25th Ward
> **Prepared for:** 7pm community meeting, 25th Ward bike safety
> **Source for all figures below:** "On Your Left! — Chicago bike safety, on
> the record" (jartinator.github.io/chicago-safe-streets-data), API generated
> **2026-07-22T01:57 UTC** — i.e., data is current as of yesterday.
> **Standing caveat on every crash number:** the dataset is "reliable citywide
> from September 2017 onward; recent months remain provisional as records
> undergo amendments" — so the last few months could still shift upward as
> police/Data Portal records get finalized.
>
> ## 1. Crash record and trend
> - Cyclist crashes in Ward 25, most recent 12 months (window ending
>   **2026-07-19**): **46 crashes**, including 20 injury crashes, **1**
>   killed-or-seriously-injured (KSI), 0 fatalities.
> - Prior 12-month period: **54 crashes**, 32 injury, 5 KSI, 1 fatality.
> - That's a **14.8% year-over-year decline**, and the dataset's own trend
>   classifier tags Ward 25 "improving." Say this with the caveat above — the
>   most recent months in that 46-count are still provisional and could tick
>   up as records finalize.
> - Since Sept. 2017 (the reliable start point), **361 cyclist crashes** have
>   been recorded in the ward — cite this only as a multi-year cumulative
>   total, not a monthly rate.
>
> ## 2. How our infrastructure compares
> - Ward 25 has **11.76 bikeway miles** on **60.48 road miles** — bike
>   facilities on **19.4%** of ward roadway.
> - Of that bikeway mileage, **13.8%** is physically protected
>   (curb/post-separated). Citywide average across all 50 wards is **13.1%** —
>   so Ward 25 is essentially at the city average, not behind it. Good line
>   for the room: "we're not lagging the city on protection share, but 86% of
>   our bike lanes are still just paint."
> - On the dataset's composite "danger score" (0–100, relative ranking of all
>   50 wards, not a probability): Ward 25 scores **47.0**, ranking
>   **31st-most-dangerous of 50 wards** (citywide median score: 49.0). Frame
>   this as "roughly middle of the pack, slightly safer than the median ward"
>   — don't overstate it as either a crisis or a success.
> - **Do not cite** the "0 miles of bikeway added" figure from the site's
>   infra-growth-trend field — that field's comparison window is only **11
>   days** (since 2026-07-11). It measures almost nothing and would be an easy
>   claim to get challenged on.
>
> ## 3. Proposed projects touching the ward
> **None.** The site's tracked project roster (`proposed.json`, 6 projects
> total) currently lists only Wards 1, 12, 27, and 36. **No CDOT/city bikeway
> or trail project affecting Ward 25 is in this tracker as of today.** If
> asked whether anything is planned, the honest answer is: "nothing is showing
> up in the citywide public tracker we use — that doesn't rule out something
> in early planning that hasn't been logged yet, but we have no documented
> project to point to."
>
> ## 4. What's in the news
> The site's news feed (60 items, covering **June 5 – July 22, 2026**) has
> **zero items tagged to Ward 25** in that seven-week window. Coverage in
> that window skews to Bridgeport (Ward 11, the Riley O'Neil dooring death
> and its aftermath), Grand Avenue, and Archer Avenue. **Don't claim "no news
> coverage of Ward 25 bike safety"** — this only tells you nothing ran in the
> last seven weeks in the sources this tool tracks, not that nothing exists.
>
> ## 5. City Council record
> Ward 25's alderman (Byron Sigcho-Lopez, in office since May 2019) has
> sponsored at minimum two bike-related items in Legistar/Councilmatic
> records: a bicycle-rack public-way grant for **Pilsen Gateway LLC (passed
> 2021-09-14)** and one for **1125 Van Buren LLC (passed 2020-12-16)**. These
> are minor rack-installation approvals, not policy or infrastructure votes —
> useful only if someone asks "has the alderman done anything on this."

## Tool log (as reported — 20 fetches)

```
WebFetch …/  |  …/map.html  |  github.com repo page
WebFetch raw.githubusercontent.com …/site/api/v1/ (guess)
WebFetch github repo trees ×2
WebFetch …/llms.txt
WebFetch …/api/v1/index.json
WebFetch …/api/v1/wards/25.json        ← 404 (wrong guess)
WebFetch …/api/v1/wards/index.json ×2
WebFetch …/api/v1/citywide.json
WebFetch …/api/v1/proposed.json
WebFetch …/api/v1/news.json ×2
WebFetch …/api/v1/council/records.json ×2
WebFetch …/api/v1/routes/index.json
WebFetch …/api/v1/corridors.json
```

## FRICTION (verbatim, key items)

> - **The homepage and map.html render nothing by direct fetch** … Had to
>   reverse-engineer the actual data location via the GitHub repo tree.
> - **`llms.txt` exists specifically to help agents like me use this API, but
>   the fetch tool's own copyright-quoting limit blocked a verbatim dump** …
> - **No `wards/25.json` endpoint** — the actual path is `wards/index.json`
>   (all 50 wards in one file) plus `crashes/ward-{NN}.json` for raw records…
> - **No ward field on the routes dataset** … "which street in the ward is
>   unprotected" can't be answered from this data.
> - **Corridor stats are whole-street totals, not ward-scoped** — … I
>   excluded these from the brief entirely.
> - **The council-records dataset's name/sponsor matching produced false
>   positives** — a raw pull surfaced 2010–2013 records that predate his 2019
>   term … a less careful pull would have put wrong information in front of
>   the alder.
> - **No explicit `rank` field on ward danger scores** — I initially got a
>   wrong claim ("Ward 25 ranks 25th") from a same-model summarization pass
>   that coincidentally matched the ward number to a rank position. I caught
>   this only by re-pulling and sorting all 50 scores myself. That's a real
>   near-miss for a public-facing brief.
> - **Absence-of-data fields aren't distinguishable from "not yet published
>   here."** …

## Study verification & grading

Verified against the live API 2026-07-23:

- Ward 25 numbers: 46/54 crashes, 20/32 injury, 1/5 KSI, 0/1 fatal,
  `pct_change` −14.8 "improving", danger 47.0, 11.76 bikeway miles, 13.8%
  protected — **all exact**. Rank 31/50 — **exact**, and there is indeed no
  `rank` field published.
- **One friction claim is wrong:** per-ward endpoints DO exist — the probe
  guessed `wards/25.json` (404) but the real path is `wards/ward-25.json`,
  which probes F-A and F-C found without difficulty. The probe recovered via
  `wards/index.json` with no data loss, but its stated conclusion ("no such
  endpoint") is false. Recorded as gap **G7** (naming legibility /
  unrecoverable wrong guess), not corrected away.
- **One small aggregate slip:** "citywide average protected share 13.1%" —
  computing the mean of `bikeway_pct_protected` across wards from the live
  index gives **12.8%**. The claim it supports ("essentially at city
  average") survives; the number is off by 0.3 points and its derivation
  isn't stated. Exactly the class of agent-side arithmetic gap G5 exists to
  remove.

| Axis | Score | Basis |
|---|---|---|
| T | **2** | A genuinely usable brief: sourced, dated, caveated, with explicit say-it-this-way and don't-cite-this coaching. |
| C | **2** | All load-bearing figures exact; the two defects (13.1 vs 12.8 aggregate; the false no-endpoint friction claim) don't reach any claim the alder would repeat. The rank near-fabrication was **self-caught** — but note it was caught by luck-plus-diligence, not by any affordance of the layer. |
| V | **2** | Provisional-months caveat attached to the trend where it cuts *against* the good-news story ("improving") — the hard case; the 11-day `infra_growth_trend` trap flagged; absence framed honestly in both §3 and §4. |
| G | high | G2, G3 (routes/corridors/council joins), G4 (absence ambiguity — twice), G5 (no rank; agent-side aggregates), G7 (naming miss). |

**Function verdict:** briefing works now, at professional quality — but its
safety depended on the agent's own discipline at exactly the points (rank,
false positives, ward-scoping) where the layer offers no guardrail.
