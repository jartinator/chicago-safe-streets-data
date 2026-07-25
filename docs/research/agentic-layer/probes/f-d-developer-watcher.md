---
probe_id: F-D
function: Developer integration
task: build and run a scheduled watcher — fetch, schema-validate, diff, fail-loud
agent: cold Sonnet subagent, web fetch + isolated scratchpad code execution, no study context
run_datetime: 2026-07-23 (runs executed 2026-07-24T03:39Z)
outcome: executed — working code, two verified runs
grades: {T: 2, C: 2, V: n/a}
---

# Probe F-D — "a watcher script I could run on a schedule"

## Prompt (verbatim task, as given)

> I want a small watcher script for the bike-safety API at
> https://jartinator.github.io/chicago-safe-streets-data/api/v1/ — something I
> could run on a schedule. It should: (1) pull the citywide and
> proposed-projects endpoints, (2) validate them against the schemas the site
> publishes, (3) detect and report changes since the last run — new KSI
> numbers, any project whose status changed, contract version bumps, (4) fail
> loudly if the data looks stale or the shape breaks. Write it in Python,
> actually run it twice so I can see the no-change path work, and tell me
> anything about the API that makes this harder than it should be.

## Deliverable

The agent produced `watch_api.py` (~250 lines; full source preserved in the
probe's raw return and in the scratchpad at `probe-dev/`): urllib fetch with
a proper User-Agent, `jsonschema` validation with a hand-built `referencing`
Registry for the shared envelope `$ref`, staleness trip-wire, KSI-headline +
per-project-status + contract-version diffing against `state/` snapshots,
append-only run log, meaningful exit codes.

**Both runs executed and verified:**

```
=== run 1 (fresh state) ===
[ok] citywide.json fetched + validated (contract_version=1.16,
     generated_at=2026-07-22T01:57:35+00:00, etag="6a61576b-4479")
[ok] proposed.json fetched + validated (…etag="6a61576b-28fb")
CHANGES DETECTED (4):
  - first run: headline KSI stat = '217', latest month 2026-07 ksi=18
  - first run: tracking 6 project(s)
  - citywide: first run, contract_version='1.16'
  - proposed: first run, contract_version='1.16'
EXIT=0

=== run 2 (immediately after) ===
No changes since last run.
EXIT=0
```

The headline KSI value the watcher locked onto ('217') matches the study's
pinned ground truth GT2 exactly. The agent also hit and correctly fixed a
real ecosystem bug en route (`jsonschema` 4.26 moved `$ref` resolution to the
separate `referencing` package).

## Tool log (as reported)

Discovery via WebFetch, then plain curl for all data/schema pulls — the agent
itself switched transports, echoing probe F-A's conclusion that LLM-mediated
fetch is the wrong tool for numbers. Probed the schemas directory
exhaustively: `envelope/citywide/proposed/index/corridors/news.schema.json`
exist; **`wards.schema.json` and `council.schema.json` 404**; no directory
index at `schemas/`.

## FRICTION (verbatim, abridged)

> 1. **`$ref` to a schema that isn't self-contained, with no discovery path
>    to the dependency.** `citywide.schema.json` and `proposed.schema.json`
>    both `$ref` `"envelope.schema.json"` as a bare relative path. Nothing in
>    `index.json`… tells a client "also fetch this other file first" — I only
>    found it by guessing the filename from the `$ref` string and probing. A
>    generic JSON-Schema validator will not auto-fetch remote refs over HTTP
>    by default (reasonably, for security), so every consumer has to
>    hand-roll a Registry/resolver exactly like I did here. A `$defs`-only
>    self-contained schema per endpoint, or at minimum a `bundled_schema` URL
>    in `index.json`, would remove this entirely.
> 2. **No schema for every endpoint, and no documented list of which ones
>    have one.** `wards.schema.json` and `council.schema.json` 404… A watcher
>    that wants to validate everything has to probe-and-catch 404s rather
>    than being told "these N endpoints are schema-covered, these aren't."
> 3. **No content-hash or "did anything change" signal cheaper than a full
>    diff.** There's a real `ETag`/`Last-Modified` on every file (GitHub
>    Pages gives you that for free), which is good… but there's no documented
>    change-feed, no `/api/v1/changelog.json`, and no per-record
>    `updated_at`/`version` on individual proposed.json projects.
>    `status_as_of` exists on projects, which helps a lot, but the file as a
>    whole has no way to say "only project X changed"…
> 4. **"contract_version" isn't guaranteed to move in lockstep across
>    endpoints, and nothing documents whether that's expected.** … a watcher
>    shouldn't have to guess.
> 5. **No documented staleness contract.** `_meta.generated_at` exists (good…)
>    but there's no published SLA ("rebuilt weekly," "alert if not rebuilt
>    within X days") anywhere in the machine-readable contract… a
>    `_meta.expected_update_interval_hours` field would let a watcher set
>    this threshold correctly instead of guessing.
> 6. **`findings` is an unordered array keyed by a string `id` that's not
>    documented as stable.** … nothing stops a future rebuild from silently
>    renaming `ksi-trend`… and quietly breaking every downstream watcher
>    without a validation error (schema still passes — `id` is just
>    `"type": "string"`).

## Study verification & grading

Cross-checked: the schema-coverage 404s match probe F-C's independent find;
the ETag values are consistent with GitHub Pages behavior; KSI 217 matches
GT2; the `referencing`-package API change is real (jsonschema ≥4.18
deprecation completed in 4.26). The civic-developer interview (study #1)
independently demanded the same three things this probe hit as friction items
1/3/5 — schema validation as a CI hard-stop, a changelog channel, a staleness
policy — which is persona-and-probe convergence on the same gaps.

| Axis | Score | Basis |
|---|---|---|
| T | **2** | Everything asked for: working code, real schema validation with the $ref resolved, both runs shown, change/no-change paths proven, loud-failure paths implemented. |
| C | **2** | Values locked match ground truth; every API claim it made (404s, ETags, relative $ref) verified. |
| V | n/a | Code artifact; caveat carriage not the object. Notably it still surfaced `data_tier`-adjacent thinking via the staleness contract. |
| G | high | All of G6 (the builder contract list) plus G1 (no change feed) and G8 (switched itself from WebFetch to curl for exactness). |

**Function verdict:** an agent can take a developer from zero to a validated,
diffing, fail-loud watcher in one session — the strongest "superior to the
website" showing in the probe set, since the website offers this function
nothing at all. The six friction items are the precise, cheap contract
additions that would make the same session shorter and every downstream
watcher safer.
