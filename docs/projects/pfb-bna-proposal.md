# Proposal: PeopleForBikes BNA data in OYL

Builds on the source evaluation in
`docs/research/followups/peopleforbikes-bna-evaluation.md` (access verified
2026-07-13: unauthenticated JSON APIs + public GeoJSON file store). This
document says what we would *build*. Status: **draft, under user-testing
validation** — see `docs/research/user-needs/validation/pfb-bna/`.

## What the source gives us, in one breath

An annual, third-party, published-methodology measure of Chicago's bike
network: a citywide City Ratings score with history (9 → 11 → 11.08 /100,
2024–2026, vs a 36 national average), a bike-access score for every 2020
census block, and a Level of Traffic Stress (LTS) classification for every
street segment — all OSM-derived, so **crowdsourced/derived tier, never
"real"**. It is a *network quality* measure. It is not ridership: it does
nothing for the exposure gap (that remains P1/Divvy + Strava Metro work).

## Proposed elements

### B1 — Citywide BNA scorecard (small; no license question; do first)

New pipeline pull of three JSON endpoints (cities-index, city-ratings
history, ratings detail) → `site/data/bna_scores.json` → one findings card
and a sources-page entry.

- The card: "PeopleForBikes rates Chicago's bike network **11 out of 100**
  (2026). The average rated U.S. city scores 36. Chicago has **6,267 miles
  of high-stress streets** and 1,834 low-stress." Trend line 2023→2026.
  Caveat string baked in (P4 traveling-provenance style): *third-party
  score, computed from OpenStreetMap — measures the network, not riders;
  only as current as OSM mapping.*
- Facts-with-attribution scale; no geometry redistributed.

### B2 — Ward-level access scores (medium; gated on license answer)

Annual snapshot of `neighborhood_census_blocks.geojson`; spatial-join
blocks → wards (pipeline already joins crashes → wards); publish per-ward
aggregates.

- Framing rule learned from the prior study (WARD: ranking-as-liability;
  US: indices must show their math): present as **access, not danger** —
  "in Ward 35, X% of residents live on blocks with low-stress bike access
  to a grocery store" — never as a 0–100 ward re-ranking. Link the BNA
  methodology page from every surface that shows it.
- Equity surface (ORG's world): block scores make access deserts visible
  citywide; pair with the anti-disinvestment copy rule from P1 (a low
  score is an investment case, never "low demand").
- Candidate surfaces: ward one-pager line, ward table column (nullable),
  ward page section.

### B3 — Segment stress cross-check (medium-large; gated on license answer)

Annual snapshot of `neighborhood_ways.geojson` (per-direction segment +
intersection stress, speed limits, OSM ids). Buffer-match onto our
existing network geometry (same 25 m technique as the Mellow dedup,
DECISIONS.md #24) — import **attributes, not a third line layer**.

- Cross-check our facility grades: where OYL says "protected" but BNA says
  high-stress (speed/lanes/intersections), flag it — as a data-quality
  signal for us and possibly a finding ("N miles of bikeways sit on
  streets BNA still rates high-stress").
- Gives *every* street a stress attribute, not just bikeways — a future
  upgrade path for the network map's comfort floor.

### B4 — Peer-city strip (small; rides on B1)

Same cities-index API covers ~3,000 cities: one findings-page comparison
of Chicago against self-selected peers (e.g. NYC, LA, Philadelphia,
Minneapolis, Seattle) with scores from the same run. No extra pulls.

## Constraints and gates

| Gate | Detail |
|---|---|
| License | Result files carry no stated license. B1/B4 (facts, attributed) proceed; B2/B3 (redistributing derived geometry/scores) wait for an answer from PFB. Draft the ask alongside this proposal. |
| Snapshots | Only the current analysis version stays hosted (older 404). Pipeline snapshots annually into `data/snapshots/`, like the CDOT layer. |
| Egress | `files.storage.bna.peopleforbikes.org` untested from pipeline environment; may need the local-pull runbook. |
| Tier | Everything badges crowdsourced/derived. OSM-currency caveat on every surface (PFB runs mapathons precisely because unmapped infra lowers scores). |
| Cadence | Annual (spring). `meta.json` provenance records the BNA version string (e.g. 26.05). |

## What this proposal deliberately does not do

- No ridership/exposure claims — BNA measures the network, not use.
- No 0–100 ward danger index — the prior study's US/WARD interviews killed
  that shape; access framing only.
- No third overlapping geometry layer on the maps.

## Validation

Persona re-run (6 of the 9 agents from the user-needs study: US, ADV,
WARD, CDOT, RIDER, ORG) reacting to this proposal element by element.
Verdicts land in `docs/research/user-needs/validation/pfb-bna/VERDICT.md`
and gate which elements advance to implementation.
