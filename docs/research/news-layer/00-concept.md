# Concept: "In the news" — attaching public news coverage to OYL entities

**Date:** 2026-07-13
**Status:** fleshed-out idea, pre-feasibility. Companion files in this folder
carry the feasibility evidence, persona reactions, and the refined design.

## The idea in one paragraph

OYL already publishes the *official record* of Chicago bike safety: upcoming
committee meetings with parsed agenda items, council records with sponsors and
votes, per-alderman safety records, and 21 named main routes with report
cards. What it lacks is the *narrative*: the Streetsblog or Block Club story
that explains why an ordinance matters, what happened on a corridor last week,
or what an alderman said about a bikeway. A weekly, deterministic pipeline
module would pull public news feeds (RSS), keep only bike/street-safety items,
match each item to entities OYL already publishes — aldermen by name, routes
by street name, wards, council records, upcoming meetings — and publish a
small `news_items.json` of **headline + link + outlet + date + matches**
(never body text). The site then shows "In the news" links in context: on a
meeting whose agenda item has coverage, on a ward page, on a route report
card, on an alderman's record.

## Why this fits OYL (grounded in the prior user-needs study)

The 2026-07 user-needs study (docs/research/user-needs/) surfaced news as the
connective tissue of the civic-data world OYL serves:

- **chi-everyday-rider** receives civic data *only* through intermediaries —
  "Block Club and Streetsblog articles, the Facebook group, another parent at
  pickup" (persona evidence base). Her one civic-finance concept (menu money)
  came from a Block Club article. News coverage attached to OYL entities meets
  her where her attention already is.
- **chi-ward-office** wants to hear about his ward "before Streetsblog does"
  (interview memo) — meaning Streetsblog is already the de facto alert system
  for ward bike-safety news; OYL surfacing that coverage next to the official
  record shortens his loop.
- **chi-pro-advocate / chi-community-organizer** work in a press register
  (ADV-L in the UX report distinguishes press vs resident framing); they cite
  articles in testimony packets alongside data.
- The evidence briefs themselves lean on Streetsblog/Block Club as the
  primary public record of council bike-safety dynamics (e.g. the Dowell 18th
  St teardown, the 2026 blockage-reporting ordinance vote) — OYL's own
  research method proves the coverage exists and maps to entities OYL tracks.

The **action page's job** is helping someone decide whether to show up to a
meeting or contact an alderman. A verbatim agenda title ("HUB 32, LLC –
O2026-0026797") tells them *what*; a linked news story tells them *why it
matters*. That pairing is the core value.

## What would attach where

| OYL entity | Attachment | Example |
|---|---|---|
| Upcoming meeting / agenda item | Coverage of a matter on the agenda, or of the committee's topic | Streetsblog preview of a Transportation Committee ordinance |
| Council record (ordinance) | Coverage naming the ordinance or its subject | "Which alders voted against the blockage-reporting ordinance" |
| Alderman | Bike-safety coverage naming the alderman | "Ald. Dowell is forcing CDOT to tear out 18th St protection" |
| Main route / corridor | Coverage naming the street | "Milwaukee Avenue protected lanes installed after two deaths" |
| Ward | Via matched alderman or matched street-in-ward | Ward page "In the news" strip |

## Mechanism sketch (subject to feasibility)

- **`pipeline/pull_news.py`**, weekly, deterministic, non-fatal like every
  other pull: fetch a small allowlist of RSS feeds (candidates: Streetsblog
  Chicago, Block Club transportation category, Google News RSS query as
  fallback), keep items matching the existing safety-topic keyword approach.
- **Deterministic entity matching at aggregate time** (analysis stays out of
  pull modules, per the agenda-items precedent): alderman surnames from
  `aldermen.json`, street names from the main-routes roster, `\bward \d+\b`
  and record-number regexes, agenda-item overlap by record number or street.
  No LLM at runtime; no invented text — headline verbatim, link out.
- **Published dataset** `news_items.json` with provenance entry: headline,
  canonical URL, outlet, published date, and a `matches` object. Tier:
  headlines/links are `real` (verbatim facts of publication); the match
  fields are `derived` — exact labeling to be settled in design.
- **UI**: small "In the news" link lists/chips on action.html meetings,
  ward.html, route report cards, alderman records; a sources.html entry with
  the usual tier badge and limitations note (editorial outlets, not official
  records; coverage ≠ endorsement; matching is by name, so misses and false
  hits are possible).

## Honest hazards (to test in feasibility + persona research)

1. **Fetchability.** Prior crawls got HTTP 403 from chi.streetsblog.org and
   blockclubchicago.org article pages. RSS endpoints may or may not be
   similarly bot-blocked. If feeds need scraping tricks, that's a kill signal.
2. **Licensing.** Headline + link + date should be safe (facts of
   publication, standard RSS use), but verify outlet policies; never body
   text or images.
3. **Matching precision.** A false attachment ("this article is about your
   ward" when it isn't) damages OYL's provenance-obsessed trust posture more
   than a missed one. Matching must favor precision over recall, and the
   persona research should probe whether *unmatched* general news has any
   value (likely not — a news firehose is what Streetsblog's own homepage is
   for).
4. **Neutrality.** Streetsblog is advocacy-adjacent. OYL is an evidence
   dashboard. Framing must be "coverage exists, judge it yourself" (outlet
   name always visible), multiple outlets where possible, and no OYL-authored
   summaries of articles.
5. **Staleness.** Rules needed for how long an item stays attached (e.g.
   rolling 90-day window per entity, all-time for council records?) and what
   happens when a meeting passes.

## Kill criteria

- No outlet feed is reliably fetchable with plain HTTP + honest User-Agent.
- Deterministic matching yields mostly-empty or mostly-wrong attachments on
  a real week of feed data.
- Personas read attached coverage as OYL endorsing the outlet's position, or
  simply don't value it.
