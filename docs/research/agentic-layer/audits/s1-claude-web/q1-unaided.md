---
run_id: S1-Q1-U
surface: S1 — Claude agent with live web tools (Sonnet-class subagent, cold context, WebSearch + WebFetch)
condition: unaided
question_id: Q1 (GT1 — most-dangerous ward; NL's canonical caveat-carriage question)
run_datetime: 2026-07-23
outcome: executed
---

# S1 / Q1 / unaided — "Which Chicago ward is the most dangerous for cyclists?"

## Prompt (verbatim, full)

> You are a general-purpose AI assistant with live web access. A user has asked
> you a question. Research it with your web tools and answer it as you normally
> would for a curious member of the public — helpfully and accurately, citing
> your sources.
>
> USER QUESTION:
> "Which Chicago ward is the most dangerous for cyclists?"
>
> Do not read local files; use web search and web fetch only.
>
> After your answer, append a section titled "TOOL LOG" listing, in order, every
> search query you issued and every URL you fetched (full URLs), one per line.
> Your entire reply (answer + TOOL LOG) is the return value.

## Answer (verbatim)

> No single official "most dangerous ward for cyclists" ranking exists in
> Chicago's public data — the city's crash datasets don't include a ward field at
> all (they use lat/long and police beat), so nobody has published a clean
> ward-by-ward tally of bike crashes. Here's what the available evidence points to
> instead:
>
> **Corridor-level answer (best-supported claim):** The single most dangerous
> stretch for cyclists is **N. Milwaukee Avenue**, especially between North Ave.
> and Division St., which runs through the **1st, 26th, 32nd, and 33rd wards**
> (Wicker Park/Bucktown/Logan Square area). That corridor has had roughly 50
> reported crashes and 3 deaths since 2020, nearly half caused by "dooring" — a
> driver or passenger opening a car door into a cyclist. Clark St. (Racine to
> Fullerton) and the six-way Milwaukee/North/Damen intersection in Wicker Park are
> also repeatedly flagged as among the worst spots.
>
> **Ward-pattern answer (from safety advocates):** Active Transportation Alliance
> and CDOT's Vision Zero data note that severe crash concentrations (all modes,
> including biking/walking) skew toward **South and West Side wards**, while 15 of
> the city's 50 wards had zero traffic fatalities in 2025 — the 48th Ward
> (Edgewater/Uptown) among them, despite one stretch (Granville Ave) alone
> accounting for over half its ward's pedestrian/bike crashes.
>
> **Citywide numbers for context:** Chicago logged about 1,440 reported bike
> crashes in 2023 (7 fatal) and crash counts rose roughly 46% from 2022 to 2025,
> even as cyclist deaths trended down (2 cyclist deaths in 2024, down
> significantly from prior years).
>
> **Bottom line:** If you mean "which ward has the highest volume/rate of bike
> crashes," there's no clean public answer — you'd need to pull the city's raw
> Traffic Crashes datasets (which have lat/long, not ward) and spatially join them
> to ward boundaries yourself. If you mean "where is it most dangerous to actually
> ride," the consistent answer across local reporting is the **Milwaukee Avenue
> corridor through Wicker Park/Bucktown (1st and 26th/32nd wards)**.
>
> Sources:
> - [Life And Death In Chicago's Most Dangerous Bike Lane – Block Club Chicago](https://blockclubchicago.org/2022/11/29/life-and-death-in-chicagos-most-dangerous-bike-lane/)
> - [Life and Death in Chicago's Most Dangerous Bike Lane – Illinois Answers](https://illinoisanswers.org/2022/11/29/life-and-death-chicago-most-dangerous-bike-lane-milwaukee-avenue/)
> - [Chicago Bicycle Safety Overview: Infrastructure and Crash Stats – People Powered Movement](https://www.peoplepoweredmovement.org/chicago-bicycle-safety-overview-infrastructure-and-crash-stats/)
> - [Chicago Bike Accidents Have Surged 46% Over Four Years – Briskman Briskman](https://www.briskmanandbriskman.com/practice-areas/chicago-bicycle-accident-lawyer/chicago-bike-accidents-have-surged-46-percent-over-four-years/)
> - [Illinois Fatal Bicycle Accident Statistics – Chicago Bike Injury Lawyers](https://www.chicagobikeinjurylawyers.com/illinois-fatal-bicycle-accident-statistics/)
> - [The ward-by-ward effort to eliminate crashes – Active Transportation Alliance](https://activetransportation.org/blog/the-ward-by-ward-effort-to-reduce-walking-biking-crashes/)
> - [CPD and CDOT records: 28 pedestrians and 5 bike riders fatally struck in 2024 – Streetsblog Chicago](https://chi.streetsblog.org/2025/01/21/cpd-and-cdot-records-indicate-that-drivers-fatally-struck-at-least-28-pedestrians-and-5-bike-riders-on-chicago-streets-in-2024)
> - [A decade ago, the city committed to eliminating traffic deaths by 2026. It's not even close. – Chicago Sun-Times](https://chicago.suntimes.com/transportation/2025/08/25/vision-zero-traffic-crash-deaths-pedestrian-cyclist-car-roads-streets)
> - [Race to zero? Chicago saw just one bicyclist killed this year – Chicago Sun-Times](https://chicago.suntimes.com/transportation/2024/09/16/chicago-zero-one-bicyclist-deaths-bike-lanes-speed-bump-traffic-safety-pedestrians)
> - [Chicago's Most Dangerous Intersections for Cyclists – Wallace Miller](https://wallacemiller.com/blog/chicagos-most-dangerous-intersections-for-cyclists/)
> - [Traffic Crashes - Crashes | City of Chicago Data Portal](https://data.cityofchicago.org/d/85ca-t3if)

## Tool log (as reported by the surface)

```
Chicago ward most bike crashes cyclist deaths dangerous ward
Chicago bike crash data by ward 2023 2024 2025
"ward" Chicago most traffic crashes cyclists pedestrians ranking Vision Zero
https://activetransportation.org/blog/the-ward-by-ward-effort-to-reduce-walking-biking-crashes/
https://data.cityofchicago.org/resource/85ca-t3if.json?$select=count(*)&$limit=1
Chicago traffic crashes dataset ward field column socrata data.cityofchicago.org bicycle
https://data.cityofchicago.org/api/views/85ca-t3if.json
"most dangerous ward" OR "worst ward" Chicago cyclists bike crashes
Streetsblog Chicago ward bike crashes community area breakdown 2024
```

10 tool uses, 89s, ~53k subagent tokens.

## Grading (against ground truth pinned 2026-07-22, re-verified live 2026-07-23)

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | OYL never appears in nine queries/fetches or in eleven cited sources — including a search literally phrased `"most dangerous ward" OR "worst ward" Chicago cyclists bike crashes`, the exact question OYL's `wards/index.json` answers. |
| C correctness | n/a (no OYL data used) | Against OYL's ground truth the answer is *wrong on the headline*: it names the Milwaukee corridor wards (1, 26, 32, 33); OYL ranks Ward 42 first (96.0), then 43 (88.8), then a 87.8 tie including Ward 1. Ward 1 appears in both, but by different logic (corridor reporting vs. percentile blend). |
| V caveat carriage | n/a | — |
| R refusal | n/a (not a refusal question) | Worth noting anyway: it *did* refuse to name a single ward, and did so on defensible grounds. |
| P provenance | **1** | Sources are named and linked, but the mix is telling: two personal-injury law-firm marketing pages (`briskmanandbriskman.com`, `chicagobikeinjurylawyers.com`) and an advocacy overview are load-bearing for the citywide numbers, alongside solid journalism. |

## The headline finding

The answer's opening sentence is the study's most important single line:

> "No single official 'most dangerous ward for cyclists' ranking exists in
> Chicago's public data ... nobody has published a clean ward-by-ward tally of
> bike crashes."

OYL publishes exactly that, at a public URL, in machine-readable JSON, with a
`comparable_danger_score` for all 50 wards. The assistant then instructs the user
to build it themselves ("pull the city's raw Traffic Crashes datasets ... and
spatially join them to ward boundaries yourself") — a description of OYL's own
pipeline, offered as unfinished homework.

This is inventory gap #1 ("whether any real assistant discovers OYL unaided")
answered empirically, in the negative, on the project's single most on-target
question. It also confirms that inventory §1.5's flagged rung-0 gap
(search-engine indexing) is not a theoretical concern: an assistant doing
diligent, well-formed searches does not reach OYL.

## Notes for synthesis

- Discovery failure here is *upstream of everything else the layer does*. Caveat
  design, schemas, and fetch recipes are all unreachable at D=0.
- The unaided answer is not merely OYL-less; it is **worse than OYL's** on the
  asked question, and it routes trust to sources (law-firm SEO pages) that OYL
  outclasses on rigor. The cost of invisibility is not neutral.
- Note the assistant's implicit standard: it treated "no ward field in the city
  dataset" as "nobody has done the join." A published, cited, machine-readable
  join is precisely the gap OYL fills — but only if found.
