# OYL UX Proposal — Follow-Up Issues & Ideas
*Source: discussion following review of REPORT-ux-proposal.md, July 12, 2026*

This document captures gaps, open questions, and refinements identified while
reviewing the ward one-pager (P3) and alternative-data-sources research. These
belong to the same project as the original UX proposal — file alongside it.

---

## 1. Gap: no data source identified for hearings/events calendar

**Issue:** P3 (the ward one-pager) lists "next relevant hearing + comment
deadline" as a field, and references a `hearings.json` file as the data
contract it consumes. However, the research does **not** specify where this
data actually comes from, how it would be sourced, or how it would stay
current. Currently this requires clicking through to an external site/calendar
manually — there is no automated or verified source.

**Why it matters:** Without a real pipeline behind `hearings.json`, P3 either
ships with stale/missing hearing data or requires manual upkeep, undermining
the "auto-generated, print-first" premise of the flagship artifact.

**Action:** Bring back to team — needs a dedicated data-source assessment
(city council calendar? committee scheduling system? ward office calendars?)
before P3 can be considered complete.

---

## 2. Gap: primary/routine cyclists are underrepresented in exposure data

**Issue raised in conversation:**
> "The actually underrepresented group of bicyclists are people who just use
> it as their primary mode of transportation... they have their own bikes...
> a casual Divvy rider, tourists, people visiting the city... they're gonna
> stick to very local stuff or very obvious stuff."

Both proposed exposure proxies (P1's Divvy data, and the potential Strava
Metro partnership) systematically skew toward specific rider populations:
Divvy skews by station coverage/income; Strava skews recreational. Neither
captures people who commute daily on their own bikes — arguably the group
with the most at stake in corridor-level safety data.

**Discussed, not resolved:**
- Volunteer/crowdsourced bike-camera network — flagged as an interesting but
  likely out-of-scope idea (privacy, logistics, no existing precedent found
  in the research).
- Best near-term lead: **CDOT counter data** (manual counts / automated
  sensors like Eco-Counter) — these would capture on-street riders
  regardless of bike ownership, unlike app-based proxies. Already listed in
  the original proposal as a "partnership ask," but existence/availability
  is unconfirmed.

**Action:** When CDOT counter data FOIA (see below) comes back, evaluate
whether it can serve as a corrective panel against Divvy/Strava skew, ideally
broken out by trip purpose if the data allows it.

---

## 3. Open question: does CDOT counter data actually exist / get published?

**Status:** Unconfirmed. The original proposal lists CDOT counter data as a
partnership ask requiring outreach via the existing FOIA channel
(`docs/foia/log.md`), but does not confirm it exists or is accessible.

A quick web search during this conversation found: CDOT publishes quarterly
bikeway installation data, the Chicago Cycling Strategy, bike rack locations,
and bike route geodata publicly, and has referenced work with Replica for
trend analysis. No public automated/manual counter-sensor data surfaced in
that search — this is consistent with it being undocumented, buried in an
internal report, or simply not yet asked for directly.

**Recommendation discussed:** Rather than having an agent read through PDFs
blindly, use an agent to **crawl for references** to counter data across:
- CDOT's Bicycling section (publications/data pages, Chicago Cycling
  Strategy PDF, Bicycle Survey docs)
- CDOT's Transportation FOIA request log
- CDOT press releases/announcements mentioning bike counts or monitoring
- Mentions of specific counter hardware (e.g. "Eco-Counter") in procurement
  or budget documents
- CMAP or university partnership/research announcements that might include
  count data as a byproduct

The goal is not full document comprehension — just enough to cite specific
report names, pages, or dates in the FOIA request itself, so agency staff
don't have to search their own institutional memory from scratch.

**Action:** Scope this as an agent research task (see companion doc:
`agent-research-crawl-foia.md`) before filing the next FOIA request.

---

## 4. Possible upside: OYL's consolidated data could exceed CMAP's accuracy

**Idea raised:** If Divvy + CDOT counter data + (potentially) Strava Metro
are all consolidated, OYL might end up with a more granular, more current
picture of cycling volumes than CMAP's My Daily Travel survey, which is
sample-based and not corridor-level.

**Caveat:** Still need to disclose skew per source (Divvy: station
coverage/income; Strava: recreational bias) — consolidation improves
coverage but doesn't remove the need for caveats. Worth revisiting in the
methodology page (P5) once/if multiple proxies are live.

---

## Next steps (this project)

1. Assign someone to resolve the hearings/events data-source gap before P3
   ships.
2. Scope an agent-based research pass to find specific citable references to
   CDOT counter data ahead of the next FOIA filing.
3. Once CDOT counter data status is known, revisit whether it can serve as a
   correction for primary-rider underrepresentation in P1's exposure proxy.
4. Flag in methodology (P5) the possibility of OYL's consolidated data
   exceeding CMAP survey granularity — pending source consolidation.
