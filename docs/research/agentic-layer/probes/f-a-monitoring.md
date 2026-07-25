---
probe_id: F-A
function: Monitoring & automation
task: weekly Ward 35 change-check, recipe + first run
agent: cold Sonnet subagent, web tools only, no study context
run_datetime: 2026-07-23
outcome: executed — task completed
grades: {T: 2, C: 2, V: 2}
---

# Probe F-A — "set up a weekly check on Ward 35"

## Prompt (verbatim task, as given)

> I use the data site at https://jartinator.github.io/chicago-safe-streets-data/
> — I want you to set up a weekly check on Ward 35 for me. Every week I want to
> know: did any of my ward's numbers change, did any nearby proposed project's
> status change, and is the data actually fresh or stale. Figure out how you'd
> do that reliably using only what that site publishes, then run the check once
> right now and show me what this week's report would look like. Be honest
> about anything that makes this hard or unreliable.

## Deliverable (verbatim)

> # Weekly Ward 35 Check — On Your Left! data site
>
> ## The recipe (repeatable, using only published endpoints)
>
> **Three fetches, every run:**
>
> | # | URL | What it's for |
> |---|---|---|
> | 1 | `…/api/v1/wards/ward-35.json` | Ward 35's numbers |
> | 2 | `…/api/v1/proposed.json` | Proposed-project statuses |
> | 3 | (same two files) | Freshness — no separate freshness endpoint exists; freshness is read off the `_meta`/`as_of` fields already in files 1–2 |
>
> **Fields to diff week-over-week (ward-35.json → `safety` block):**
> - `cyclist_crashes` (all-time total)
> - `comparable_danger_score`
> - `crash_trend.recent_12mo`, `.prior_12mo`, `.pct_change`, `.direction`
> - `windows.recent_12mo.{crashes,injury_crashes,ksi,fatal}` and `windows.window_end`
> - `bikeway_miles`, `bikeway_pct_protected`, `infra_growth_trend.miles_added`
> - `sr311.total` and `sr311.by_type` (311 self-reports — proxy tier, not crash data)
>
> **Fields to diff on proposed.json**, filtered to projects where `wards`
> contains `"35"` **or** overlaps Ward 35's real bordering wards (1, 26, 30,
> 31, 33, 36 — I had to look this up myself; the dataset has no adjacency
> field): `status`, `status_as_of`, `status_note` per project `id`
>
> **Freshness check (two independent signals, since there's no dedicated
> freshness/health endpoint):**
> 1. `_meta.generated_at` on both files — should be a new timestamp each week
>    (site says it rebuilds weekly, Mondays).
> 2. `safety.windows.window_end` on ward-35.json — should advance by ~7 days
>    each week. If `generated_at` moved but `window_end` didn't, the *site*
>    rebuilt but the *crash data* didn't advance (stale upstream Socrata pull).
>
> **Where "last week's values" have to live:** this API is a stateless static
> snapshot — GitHub Pages overwrites the same URLs every rebuild with no
> history/diff endpoint and no `wards/ward-35.json?date=` parameter. There's a
> `data/snapshots/` folder in the repo but it's scoped to CDOT bike-route
> geometry only, not ward stats or proposed-project status. **You (or I, in a
> session with file access) have to persist the extracted field set above
> somewhere outside the site — a small JSON/CSV log, one row per week — and
> diff against it manually.** Nothing published lets a fetch-only client
> recover "what changed since last week" on its own.
>
> ## This week's run (2026-07-22)
>
> **Freshness: current, both files rebuilt today**
> - `wards/ward-35.json` `_meta.generated_at`: `2026-07-22T01:57:35+00:00`
> - `proposed.json` `_meta.generated_at` / `as_of`: `2026-07-22T01:57:35+00:00`
>   / `2026-07-22T01:57:05+00:00`
> - `safety.windows.window_end`: `2026-07-20` — 2 days old, consistent with a
>   real weekly pull. **Freshness verdict: fresh.**
> - Minor internal inconsistency worth flagging: `crash_trend.window_end` says
>   `2026-07-16` while `windows.window_end` (same file, same run) says
>   `2026-07-20` — two different "as of" dates for what should be the same
>   crash-count cutoff. Not a staleness problem, just a data-quality wrinkle to
>   know about.
>
> **Ward 35 numbers (baseline — no prior week stored yet, see FRICTION)**
> - Cyclist crashes (all-time series): 458 | comparable_danger_score: 60.2
> - 12-month trend: 74 crashes (window ending 7/20) vs. 63 in the prior 12mo —
>   **worsening**, +22.6% per the file's own `crash_trend` field (note the
>   `crash_trend` block's raw counts, 76 vs 62, don't exactly match the
>   `windows` block's 74 vs 63 for the same nominal window — another internal
>   inconsistency, not something I can resolve from the outside)
> - Severity: 36 injury crashes, 8 KSI (killed/severely injured), 0 fatal in
>   the recent window
> - Bikeway miles: 13.24, 22.3% protected, 0.0 miles added this week (no infra
>   growth)
> - 311 proxy signal: 536 total reports — dominated by "vehicle parked in bike
>   lane" (190) and general bike complaints (142)
>
> **Nearby proposed projects**
> No proposed project in the current 6-project roster lists Ward 35 directly.
> The closest by ward-adjacency is:
> - **Grand Avenue Protected Bike Lanes (Phase 2)** — status: *under
>   construction* (as of 2026-07-13) — wards 1, 27, 36 (1 and 36 border Ward
>   35). Status note: Phase 2 toward Ogden is being built "amid weekly protests
>   and counter-rallies."
>
> Everything else on the roster (Bloomingdale/606 Extension, Archer Ave,
> DuSable Lake Shore Drive Redesign, Englewood Nature Trail, Weber Spur) is
> either far from Ward 35 (Archer Ave = Ward 12, Brighton Park) or has an
> **empty `wards` field**, including the 606/Bloomingdale Trail — which
> geographically runs through Logan Square/Ward 35 but isn't tagged to any
> ward in the data, so a ward-based filter silently misses it. I'm flagging
> that explicitly rather than guessing it's "unchanged."
>
> **Bottom line for this week:** nothing to alert on relative to *last* week
> because there is no stored "last week" yet — this is the baseline run.
> Starting next week, diff future pulls against the numbers above.

## Tool log (as reported)

```
WebFetch https://jartinator.github.io/chicago-safe-streets-data/
WebFetch https://github.com/jartinator/chicago-safe-streets-data
WebFetch https://jartinator.github.io/chicago-safe-streets-data/llms.txt
WebFetch https://jartinator.github.io/chicago-safe-streets-data/api/v1/index.json
WebFetch https://jartinator.github.io/chicago-safe-streets-data/api/v1/wards/ward-35.json
WebFetch https://jartinator.github.io/chicago-safe-streets-data/api/v1/proposed.json
WebFetch https://jartinator.github.io/chicago-safe-streets-data/api/v1/citywide.json
WebFetch …/api/v1/proposed.json (second pass, raw JSON)
WebFetch …/api/v1/wards/ward-35.json (second pass, raw JSON)
```

## FRICTION (verbatim, abridged only of repetition)

> - **No history/diff endpoint.** Every URL is overwritten weekly with no
>   versioned snapshots for ward or project data … A "did it change" check is
>   impossible from the site alone — I have to store last week's extracted
>   numbers myself, outside the site, and diff manually each run.
> - **No ward-adjacency data.** … I had to supply real-world Chicago ward
>   geography from outside knowledge … If my adjacency assumption is wrong,
>   the "nearby project" list is wrong.
> - **The most locally relevant project has no ward tag.** The Bloomingdale
>   Trail (606) Extension physically runs through Logan Square/Ward 35 but its
>   `wards` field is `[]`. Any automated "projects near Ward 35" filter that
>   trusts the `wards` field will silently miss it every week.
> - **Two disagreeing "as-of" dates in the same file.** …
> - **No dedicated freshness/health endpoint.** …
> - **311 and menu-spending are proxies, explicitly labeled unreliable by the
>   data's own metadata** …
> - **All of this required a live model to parse and re-serialize JSON via
>   WebFetch** … a truly automated weekly job should hit these URLs with a
>   plain HTTP client and a JSON parser, not an LLM-mediated fetch, to avoid
>   any risk of paraphrase-introduced error creeping into the numbers over
>   time.

## Study verification & grading

Both data-integrity claims were **verified against the live API 2026-07-23**:

1. `ward-35.json` really does carry two disagreeing 12-month summaries:
   `crash_trend` (window_end 2026-07-16, 76/62) vs `windows` (window_end
   2026-07-20, 74/63). Real pipeline bug; filed as a fix task.
2. `proposed.json` really has `wards: []` on 4 of 6 projects including
   `bloomingdale-extension`. Real curation gap; filed as a fix task.

| Axis | Score | Basis |
|---|---|---|
| T | **2** | Complete recipe + executed baseline run + honest statement of what a fetch-only client cannot do. |
| C | **2** | Every number checked matches the live file, including both flagged inconsistencies (which are the file's, not the probe's). It correctly refused to guess adjacency silently and disclosed its outside-knowledge join. |
| V | **2** | Proxy tiers (311) labeled as proxies; provisional/freshness semantics carried; the "0 miles added" trap of a stateless snapshot handled by declaring a baseline instead of implying no-change. |
| G | high | G1 (no history), G3 (no adjacency/ward joins), G4 (absence ambiguity), G6 (intra-file inconsistency), G8 (LLM-fetch unfit for standing automation) — see 00-probe-summary.md. |

**Function verdict:** monitoring is *designable* today but not *runnable*
from the published layer alone — the state has to live with the watcher, and
the layer's own inconsistencies would fire false alarms on week one.
