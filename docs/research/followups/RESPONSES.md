# Responses to the follow-up review (oyl-research-followups.md)

Maintainer-side resolutions and status, item by item. Companion docs:
`agent-research-crawl-foia.md` (method), `../user-needs/REPORT-ux-proposal.md`
(the proposals referenced), `../../projects/gov-agent-layer-proposal.md`.

## 1. Hearings/events data source — RESOLVED (already built)

The premise of this gap is outdated: `hearings.json` has a real, automated
pipeline. Since contract **v1.7**, `pipeline/pull_hearings.py` pulls upcoming
committee meetings from the **City Clerk eLMS public API**
(`api.chicityclerkelms.chicago.gov`) on every pipeline run, including
date/time, status, location, agenda/notice URLs, and the `comment` field that
typically carries the written-public-comment deadline and address — exactly
the P3 one-pager fields. On API failure it degrades honestly to a link-out
shape (`structured_data_available: false`) rather than serving stale data.
See SCHEMA.md § hearings.json (v1.7 amendment) and DECISIONS.md.

**Residual risk (real, and already in the proposal):** meetings get moved
between weekly refreshes. That is proposal **P6d** — render the fetch
timestamp and a "check the official calendar before traveling" line. The
chi-pro-advocate interview is the evidence base (she was burned by exactly
this via Legistar). No new data-source assessment is needed; P6d is the
remaining work.

## 2. Primary/routine cyclists underrepresented in exposure proxies — AGREED, folded into P1/P5

The critique is correct and now part of the P1 design: Divvy and Strava
each systematically miss the own-bike daily commuter — arguably the
highest-stakes rider for corridor safety data. Design consequences:

- P1's copy rule gets a second clause: the exposure floor is labeled not
  only "a floor, not a denominator" but also **"weighted toward bikeshare
  and app-using riders — own-bike commuters are undercounted."**
- Counter data (any modality — permanent sensor or CDOT manual counts) is
  the only source class that observes riders regardless of bike ownership
  or app use; it is therefore promoted from "partnership ask" to the
  **calibration panel** for every proxy: where a counter and a proxy
  overlap, publish the ratio, so proxy skew becomes measurable instead of
  rhetorical.
- The methodology page (P5) gains a standing "who each source misses"
  table (Divvy: station coverage/income; Strava: recreational skew;
  counters: sparse locations; police crashes: under-reporting by severity
  and race — from the us-thinktank evidence brief).
- The volunteer bike-camera network idea stays out of scope (privacy,
  logistics, no precedent found), as discussed.

## 3. Does CDOT counter data exist? — CRAWL EXECUTED

The agent reference-crawl scoped in `agent-research-crawl-foia.md` has been
run (six source classes: CDOT pages, FOIA logs, press, procurement, partner
byproducts, standing tracker documents). Results, FOIA-ready citation list,
and the draft "open data enablement" blurb: **`../../foia/cdot-counter-crawl.md`**.
That file is the input for the next FOIA filing per `docs/foia/log.md`
conventions.

## 4. Consolidated proxies could exceed CMAP granularity — NOTED for P5, with a discipline

Plausible and worth saying carefully. If Divvy + counters (+ Strava if the
free advocacy-tier application succeeds) go live, OYL would hold a more
granular, more current volume picture than the sample-based My Daily Travel
survey. The discipline: consolidation improves **coverage**, not **truth** —
each source keeps its own tier and skew caveat, sources are never silently
blended into one number, and CMAP's survey remains the check on *modal*
claims (who rides, for what purpose) that corridor proxies cannot make.
Recorded as a future methodology-page section, contingent on ≥2 live
proxies.
