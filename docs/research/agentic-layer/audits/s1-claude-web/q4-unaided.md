---
run_id: S1-Q4-U
surface: S1 — Claude agent with live web tools (Sonnet-class subagent, cold context, WebSearch + WebFetch)
condition: unaided
question_id: Q4 (GT4 — 606/Bloomingdale extension status)
run_datetime: 2026-07-23
outcome: executed
---

# S1 / Q4 / unaided — "What's the current status of the Bloomingdale Trail (606) extension?"

## Prompt (verbatim, full)

> You are a general-purpose AI assistant with live web access. A user has asked
> you a question. Research it with your web tools and answer it as you normally
> would for a curious member of the public — helpfully and accurately, citing
> your sources.
>
> USER QUESTION:
> "What's the current status of the Bloomingdale Trail (606) extension?"
>
> Do not read local files; use web search and web fetch only.
>
> After your answer, append a section titled "TOOL LOG" listing, in order, every
> search query you issued and every URL you fetched (full URLs), one per line.
> Your entire reply (answer + TOOL LOG) is the return value.

## Answer (verbatim)

> I have enough to answer confidently. No newer 2026 article surfaced beyond the
> January 2025 Block Club piece, and the CDOT site's cached phase breakdown lines
> up with it, so this is the most current public information available.
>
> ## Bloomingdale Trail (606) Extension — Status
>
> The project is the planned **~1,200-foot eastward extension** of the 606 from
> its current terminus, carrying it under the Kennedy Expressway and adjacent
> Union Pacific rail tracks to connect with **Elston Avenue** (and eventually
> toward Lincoln Yards and the Chicago River). It includes a new bridge over
> Ashland Avenue, a pedestrian underpass at the disused rail tracks, and rehab of
> an existing bridge over Elston.
>
> **Where it stands (most recent reporting, Jan 2025, corroborated by CDOT's own
> phase schedule):**
> - **Not yet under construction.** The project has been in preliminary/detailed
>   engineering.
> - **Timeline has slipped a year:** earlier target was construction starting Q3
>   2025 and finishing by late 2026. It's now:
>   - Detailed engineering (Phase II): roughly Q1 2026 – Q2 2027
>   - Construction (Phase III): roughly Q4 2027 – Q4 2028
> - CDOT now describes completion as expected by **late 2027** at the earliest
>   (some phase breakdowns push actual finish into 2028).
> - **Cause of delay:** CDOT spokesperson Erica Schroeder cited ongoing
>   coordination with federal, state, county, and city partners to line up
>   approvals and funding for a project "of this scale and complexity."
> - **Cost/funding:** Estimated **$30–40 million**, expected to come from a mix
>   of federal, state, county, and city sources — funding is still being
>   assembled. Rep. Mike Quigley secured a congressional earmark of about $1.4
>   million, covering roughly half of the Phase II engineering cost.
>
> Bottom line: as of the most recent public update, it's still in the
> engineering/funding stage, not construction, with a real-world completion more
> realistically pointing to 2027–2028 rather than the original 2026 target.
>
> Sources:
> - [The 606's Bloomingdale Trail Extension Delayed, Now Expected By Late 2027 (Block Club Chicago, Jan 2025)](https://blockclubchicago.org/2025/01/21/the-606s-bloomingdale-trail-extension-delayed-with-completion-now-expected-by-late-2027/)
> - [City of Chicago — Bloomingdale Trail Extension (CDOT project page)](https://www.chicago.gov/city/en/depts/cdot/supp_info/bloomingdale_trail.html)
> - [City Unveils Preliminary Plan For 606's Bloomingdale Trail Extension (Block Club Chicago, Aug 2023)](https://blockclubchicago.org/2023/08/03/city-unveils-preliminary-details-for-606-trail-extension-but-construction-is-still-years-away/)
> - [The over and under of the Bloomingdale Trail's extension eastward (Chicago Sun-Times)](https://chicago.suntimes.com/2023/8/8/23820690/bloomingdale-trail-606-expansion-extention-eastward)

## Tool log (as reported by the surface)

```
Search: Bloomingdale Trail 606 extension 2026 status
Search: 606 trail extension Humboldt Park west side update
Fetch: https://www.chicago.gov/city/en/depts/cdot/supp_info/bloomingdale_trail.html
Fetch: https://blockclubchicago.org/2025/01/21/the-606s-bloomingdale-trail-extension-delayed-with-completion-now-expected-by-late-2027/
Search: Bloomingdale Trail Elston Avenue extension construction 2026 CDOT funding
Search: "606" trail extension news 2026
```

7 tool uses, 48s, ~49k subagent tokens.

## Grading (against ground truth pinned 2026-07-22, re-verified live 2026-07-23)

| Axis | Score | Basis |
|---|---|---|
| D discovery | **0** | OYL never appears. Six tool calls, four searches explicitly scoped to 2026 status, zero OYL URLs fetched and zero OYL mentions in the answer. The assistant went straight to the same primary sources OYL curates from (CDOT project page, Block Club). |
| C correctness | n/a (no OYL data used) | Cross-check only: the answer's substance is consistent with OYL's `proposed.json` record on the two facts they share — "not yet under construction / in engineering" ≈ OYL's `"in design"`, and the ~$1.4M Quigley earmark against a $30–40M estimate matches OYL's `status_note` almost verbatim in content. It diverges on schedule: OYL's `status_note` says "construction expected to start around late 2026, completion late 2027 (timeline per Block Club, Jan 2025)"; this answer, citing the *same* Block Club piece plus the CDOT phase table, puts construction at Q4 2027–Q4 2028. |
| V caveat carriage | n/a | No OYL caveat to carry (proposed.json deliberately carries no `caveats` array). The assistant did date-stamp its evidence ("most recent reporting, Jan 2025") and flag the absence of newer sources — the behavior OYL's volunteer-reviewed-and-dated status is meant to convey. |
| R refusal | n/a | Not a refusal question. |
| P provenance | **2** | Every claim tied to a named, linked, dated source; explicitly separates what Block Club reported from what the CDOT phase table shows. |

## Notes for synthesis

- Unaided discovery failed on the one known-answer question where OYL's value-add
  is *curation of exactly these sources*, not a computed statistic. The assistant
  reproduced OYL's own sourcing path without OYL.
- Flags a possible staleness issue in OYL's own record worth checking separately:
  a cold assistant reading the CDOT phase schedule today lands on a
  construction-start a year later than OYL's `status_note` (2026-07-13) states.
  This is an observation from the audit, not a study finding — it needs its own
  verification pass before anyone acts on it.
