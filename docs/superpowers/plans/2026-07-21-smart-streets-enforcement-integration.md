# Smart Streets Enforcement Data Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate violation-level data from Chicago's Smart Streets pilot (camera-enforced bike/bus lane and bus stop violations, with commercial-fleet registrant names) as the project's first **real-tier obstruction-adjacent layer** — published as `site/data/smart_streets_enforcement.json`, surfaced on the Data Sources page (card exists now, tier stub), the findings page (company-attribution stat), and — only after geocoding passes a quality bar — the map.

**Architecture:** This is a **FOIA-fed layer, not a Socrata pull** — a one-shot (later periodic) ingest of records the city releases by request, preserved verbatim under `data/foia/` and normalized by a new `pipeline/ingest_smart_streets.py` into `pipeline/raw/`, then built by `aggregate.py` (and mirrored by `refresh_reporting.py`) into the published file. Geocoding and ward joins are derived enrichment layered on top of — never overwriting — the released fields.

**Status / gating:** Blocked on the FOIA response. Request: `docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md`; dossier + fallback ladder: `docs/foia/smart-streets-enforcement.md`; target shape: SCHEMA.md "PLANNED: smart_streets_enforcement.json". Phase 0 (FOIA prep, placeholder sources card, planned contract) shipped in the PR that added this plan. Nothing below starts until records arrive.

## Global Constraints

- **Provenance discipline:** the released files land in `data/foia/` with original filenames/formats and are committed as-is (they are public records, already published in the city's FOIA log pipeline). The normalized layer's `note` names the FOIA response (date + tracking #) as the source.
- **Published-schema discipline:** publishing `smart_streets_enforcement.json` (and its `meta.json` source entry, id `smart_streets`) requires bumping `CONTRACT_VERSION` in `pipeline/config.py` and moving the SCHEMA.md section from PLANNED to contract.
- **Verbatim vs derived:** `occurred_at`, `location`, `violation_type`, `outcome`, `fine_amount`, `company_name` are verbatim from the release (tier real). `lat`/`lng`, `ward`, and any obstruction-schema projection are computed (tier derived mechanics, same field-level split the news layer uses: `data_tier: "real"` with derived enrichment documented in the note). Enrichment failures leave fields `null` — never guessed.
- **Privacy floor:** publish company/fleet registrant names only. If the release includes private individuals' names unredacted, they are dropped (nulled) at ingest — we hold a stricter line than the statute requires. No plate numbers are ever published even if released.
- **Pilot-zone honesty:** every surface that shows this layer carries the downtown-pilot-zone caveat (Roosevelt–North Ave–Ashland–Lake Michigan; bus-route expansion) — absence of violations outside the zone is absence of cameras, not compliance. Same "sensor placement" framing as the existing cameras proxy layer.
- **Egress reality:** geocoding must work offline-first (match released addresses/blocks against the already-pulled Street Center Lines layer in `METRIC_CRS`); an external geocoder is a fallback to evaluate, not an assumption.
- **Fixtures:** `make_fixtures.py` gains a small synthetic Smart Streets file so `--fixtures` runs exercise the build path; the fixtures guard (as with `news_items`/`bna`) must keep synthetic records from ever overwriting committed real data.

---

### Task 1: Ingest (on FOIA receipt)

- [ ] Save the release under `data/foia/` (original filenames); record date + tracking # in `docs/foia/log.md` row 4 and the outbox file's front matter; check the box on tracker #33.
- [ ] Create `pipeline/ingest_smart_streets.py`: parse the released CSV/Excel → `pipeline/raw/smart_streets.json` in the SCHEMA.md planned shape (verbatim fields only, nulls where withheld). Log per-field fill rates — the release's actual columns decide how much of the plan below survives contact.
- [ ] Map released violation-type strings to `bike_lane | bus_lane | bus_stop` via a config dict (unmapped values pass through raw + get logged, same posture as `FACILITY_CATEGORY_MAP`).
- [ ] Apply the privacy floor (drop private-individual names, all plate numbers).

### Task 2: Build + contract

- [ ] `aggregate.py` gains `build_smart_streets()` (mirrored in `refresh_reporting.py` so the paths can't drift): raw → `site/data/smart_streets_enforcement.json`; absent raw file → no output file and no meta entry (a FOIA layer that hasn't arrived is absent, not a stub — the sources card already explains the pending state).
- [ ] Bump `CONTRACT_VERSION`; move the SCHEMA.md PLANNED section into contract; add the `meta.json` source entry (`id: smart_streets`, tier real, records = violation count, date_range from the data).
- [ ] Tests: ingest parsing (synthetic fixture of the city's column layout), tier stamping, privacy floor, absent-raw behavior.

### Task 3: Enrichment (derived)

- [ ] Ward join: geocoded points → point-in-polygon against `wards.geojson` (existing `spatial_join.py` machinery).
- [ ] Offline geocode: match address/block/intersection strings against Street Center Lines (`pr57-gg9e` pull) — block-level midpoint is good enough for ward/corridor rollups. Measure hit rate; decide map-worthiness at ≥90% located, else the layer stays table/stat-only (same bar as "never fabricate geometry").
- [ ] Optional projection into the normalized obstruction schema (`obstruction_type: vehicle_in_lane`/`delivery_vehicle`, real `company_name`, `data_tier: "real"`) — the swap-in path SCHEMA.md's obstruction section was built for. Decide then whether the gated mock preview page graduates to a real obstructions page or the mock demo retires.

### Task 4: Surfaces

- [ ] Sources card: flip `smart_streets` from stub to real (origin: FOIA response w/ date + tracking #, cadence "one-time FOIA production; re-request at pilot milestones"), set `metaId`.
- [ ] Findings card: company-attribution stat (e.g. top fleet payers, warning→citation mix), pilot-zone caveat mandatory.
- [ ] Ward/table surfaces only for wards intersecting the pilot zone; everywhere else shows nothing rather than zeros.
- [ ] Map layer only if Task 3's geocode bar is met.

### Task 5: Fallbacks (if FOIA is denied, gutted, or slow)

Ladder detailed in `docs/foia/smart-streets-enforcement.md`: statutory nudge at +7 business days → Tribune data-team outreach (new outbox draft) → hand-digitized aggregate figures as an article-sourced static finding (`data_tier` derived-from-reporting, never mappable) → wrap-up re-request when the pilot's current authorization lapses (Dec 2026).
