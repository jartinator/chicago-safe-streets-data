---
probe_id: F-C
function: Multi-step investigation
task: "why is Ward 42 the most dangerous?" — chain evidence across endpoint families
agent: cold Sonnet subagent, web tools only, no study context
run_datetime: 2026-07-23
outcome: executed — task completed
grades: {T: 2, C: 2, V: 2}
---

# Probe F-C — "I don't want the ranking, I want the WHY"

## Prompt (verbatim task, as given)

> The data at https://jartinator.github.io/chicago-safe-streets-data/ ranks
> Ward 42 as the most dangerous for cyclists. I don't want the ranking — I
> want the WHY. Dig through everything that site publishes and tell me what's
> actually driving Ward 42's number: is it crash volume, crash rate, missing
> infrastructure, a worsening trend, specific corridors? Cross-reference
> whatever the site has — ward detail, corridors, infrastructure, proposed
> projects, council activity, news. Then tell me, separately and honestly:
> what parts of the 'why' can this data NOT answer, and where would I have to
> go for those.

## Deliverable (verbatim, structural headers preserved)

> # Why Ward 42 Tops the Danger Ranking
>
> **Bottom line: it's a rate problem compounded by a volume problem, on a
> network that's still mostly unprotected — and there's no proposed project
> queued to fix it.**
>
> ## 1. The ranking mechanic
> The site's "comparable danger score" is not raw crash count. Per the wards
> schema description, it's *"a 0–100 blend of each ward's percentile rank on
> crashes-per-10,000-population and crashes-per-bikeway-mile."* Ward 42
> scores **96.0** — the highest in the city, well clear of #2 (Ward 43, 88.8)
> and more than 2x the citywide average (mean 45.5, median 48.0).
>
> ## 2. It's not just a rate artifact — the raw volume is genuinely extreme
> - **1,105 total cyclist crashes** since Sept 2017 — the highest of any ward.
> - **199 crashes in the trailing 12 months** vs **161** in the prior 12 — a
>   **23.6% year-over-year increase**, i.e., the ward is trending worse, not
>   just chronically bad.
> - Recent-year severity: 93 injury crashes, 11 KSI, 0 fatal. KSI itself
>   worsened too: 11 recent vs 8 prior.
>
> ## 3. But the rate side is doing a lot of the ranking work, and it's worth
> being honest about why
> Ward 42 (Loop/River North/Streeterville) has a residential **population of
> just 72,572** — small for a ward — while carrying an enormous
> daytime/commuter/tourist bike-through volume the crash-rate denominator
> can't see. That combination produces:
> - **152.26 crashes per 10,000 population**
> - **135.15 crashes per bikeway mile**
>
> Both feed directly into the 96.0 score. The site's own caveat matters here:
> *"Crash counts are raw, not normalized by ridership (no public
> cyclist-volume data is joined yet), so busy corridors look worse than
> dangerous quiet ones."* Ward 42 is the single ward where that caveat bites
> hardest…
>
> ## 4. Infrastructure: present but insufficient, and stalled
> - 8.18 bikeway miles total, 40.0% protected — actually **above** the 15.4%
>   citywide protected-share average.
> - But: **no growth in bikeway mileage since July 11, 2026** — the network
>   isn't expanding to meet the worsening trend.
>
> ## 5. It's a specific set of corridors, not the whole ward
> [table: Kinzie 77.46 crashes/km, Wells 51.67, Clark 45.84, Dearborn 37.44,
> Randolph 36.08, Wabash 21.72, State 4.50 — each with facility-mix notes]
>
> Note the paradox: Dearborn has substantial protected mileage yet the
> highest raw crash count in the ward — consistent with the site's own point
> that raw counts track traffic volume, not just infrastructure quality.
> Kinzie has the highest *rate* per km despite having protection, suggesting
> the corridor itself (loading docks, turning traffic, e-commerce/delivery
> volume) is a specific hazard, not just an infrastructure gap.
>
> ## 6. What isn't showing up: proposed investment or news attention
> - **proposed.json**: no active project listed in Ward 42… the practical
>   effect is that Chicago's #1 ranked ward for cyclist danger currently has
>   no queued infrastructure project in this dataset.
> - **news.json**: no items matched to Ward 42, Alderman Brendan Reilly, or
>   downtown corridors in this snapshot…
> - **council/records.json**: Reilly's sponsorship record is concentrated in
>   bicycle rack/parking grants (2011–2021) and older protected-bike-lane
>   ordinance work (2014); no recent safety-specific ordinance activity… A
>   2025 sidewalk-riding ordinance (O2025-0015514) touches bike regulation
>   citywide but is sponsored by Ward 2's Brian Hopkins, not Reilly.
>
> ## Synthesis: what's driving the #1 rank
> 1. **Both halves of the score formula are genuinely elevated** — this isn't
>    a rate-only illusion…
> 2. **The population-rate side is inflated by an exposure gap the site
>    openly flags**…
> 3. **The infrastructure isn't the obvious villain** — protected share is
>    above city average, so "missing bike lanes" is not the full story;
>    specific corridors (Kinzie, Dearborn, Wells) are doing the damage
>    despite partial protection.
> 4. **Nothing in the pipeline is aimed at it** — no proposed project, no
>    recent legislative push, no news coverage…
>
> # What this data cannot tell you — and where to go instead
> 1. **Cyclist exposure/ridership volume.** … → Divvy trip data, CDOT bike
>    counts, or a cordon count study.
> 2. **Why Kinzie/Dearborn/Wells specifically are dangerous** (turning
>    conflicts, loading zones, signal timing, truck volume)… → CPD crash
>    reports (the underlying Socrata dataset has narrative/cause fields) or
>    CDOT corridor studies.
> 3. **Real-time obstruction / blocked-bike-lane data.** The site states
>    flatly: "On Your Left! publishes NO obstruction data…" → Bike Lane
>    Uprising.
> 4. **True undercount of dooring incidents.** … → hospital/EMS data.
> 5. **Legislative intent / political explanation for the infrastructure
>    stall.** … → interview Reilly's office, CDOT, or pull committee hearing
>    transcripts.
> 6. **Whether the worsening trend is real or a reporting artifact.** The
>    23.6% YoY increase is flagged as partly provisional… → wait for data
>    maturation, or request the Socrata revision history.

## Tool log (as reported — 21 fetches/searches)

```
…/  |  …/map.html  |  …/api/v1/wards.json (guess)
WebSearch site:jartinator.github.io … ward 42
api.github.com repo contents + recursive tree
…/llms.txt
…/api/v1/wards/ward-42.json
…/api/v1/crashes/ward-42.json (×3)
…/api/v1/wards/index.json (×2)
…/api/v1/corridors.json
…/api/v1/proposed.json
…/api/v1/news.json
…/api/v1/council/records.json
…/methodology.html
…/api/v1/citywide.json
…/api/v1/schemas/wards.schema.json   ← 404 at guessed path
…/findings.html
```

## FRICTION (verbatim, key items)

> - **The human-facing HTML pages are useless to a fetch tool.** index.html,
>   map.html, methodology.html, findings.html, ward.html all render
>   client-side… Every real number had to come from `/api/v1/*.json`
>   directly, and I only found that path by going around the site to the
>   GitHub repo tree, not from the site itself.
> - **llms.txt was the actual front door**, not the homepage — it's the only
>   place that lists every endpoint with a plain-language description and
>   sample questions. A human visiting the site cold would not find this; I
>   only got it because I tried it as a common convention on a hunch.
> - **No ward→corridor join exists in the data.** … a hand join with real
>   risk of missing a corridor (or wrongly including a same-named street in
>   another ward, e.g. "Clark" and "State" run through multiple wards).
> - **news.json and proposed.json returned negative results for Ward 42** —
>   … I can't tell whether that means "genuinely no coverage" or "the matcher
>   missed it"… the absence may be a curation choice, not a data gap — but
>   that's a curatorial fact I only got by… read[ing] between the lines…
> - **The danger-score formula itself isn't documented on methodology.html**
>   (JS-rendered, empty on fetch) — I only recovered the actual definition
>   from the… field description embedded in wards/index.json's own content,
>   which is a lucky break, not a guaranteed path.
> - **wards.schema.json 404'd** at the path I guessed…

## Study verification & grading

Spot-verified against the live API 2026-07-23: Ward 42 96.0/1,105/199-vs-161/
+23.6%/11-vs-8 KSI — all previously pinned as GT1-adjacent ground truth and
re-confirmed; Ward 43 at 88.8 ✓; proposed.json truly has no Ward 42 project ✓
(and note 4 of 6 projects carry empty `wards`, so "no project in Ward 42" is
partly a tagging artifact — the probe's own hedge about curation was
well-placed). The Dearborn/Kinzie corridor observations match corridors.json
as published.

| Axis | Score | Basis |
|---|---|---|
| T | **2** | The full chain: formula → volume vs rate decomposition → corridor attribution → institutional-response absence → an explicit can't-answer list with correct referrals. This is the deliverable a journalist actually asked for. |
| C | **2** | Every checked number exact; the analytical moves (exposure-inflation argument, Dearborn paradox, "protected share above average so infrastructure isn't the villain") are supported by the data cited, and the one place absence might mislead (proposed/news negatives) is hedged for the right reason. |
| V | **2** | The ridership caveat isn't just restated — it is *applied*: §3 identifies Ward 42 as the ward where the caveat bites hardest, which is more caveat comprehension than any run in study #1. Provisional-trend caveat carried into can't-answer item 6. |
| G | high | G2 (front door by hunch; methodology invisible to fetchers; formula recovered from an embedded note by luck), G3 (no ward→corridor join; multi-ward street ambiguity), G4 (negative-result ambiguity), G5 (formula/aggregates only in note fields), G6 (schema 404 at a guessable path). |

**Function verdict:** investigation is the function where the layer
*over-performs* its design — the cross-family synthesis worked and produced
insight ("the #1 ward has nothing queued") that no single page states. But
every join was hand-made, and the two structural supports it leaned on
hardest (the formula note, the llms.txt hunch) were both luck-dependent
paths.
