# "In the news" — news coverage attached to wards, aldermen, and routes — design

**Date:** 2026-07-13
**Precursors:** docs/research/news-layer/00-concept.md (idea),
docs/research/news-layer/evidence-feeds.md (feasibility evidence + local probe).

## Goal

OYL publishes the official record (meetings, agenda items, council records,
alderman safety records, route report cards) but not the narrative around it.
Attach recent public news coverage — **headline + link + outlet + date only,
never body text** — to the entities OYL already tracks, so the action and ward
pages can show *why* an agenda item or a corridor matters, in the outlets'
own words, with the outlet always named.

## What feasibility research settled (evidence-feeds.md)

1. **Three viable inputs**, all verified live with a plain honest client:
   - `chi.streetsblog.org/feed/` — full-text RSS, permissive robots.txt, and
     per-item `<category>` tags that carry **ward numbers, alderman names,
     and street names**.
   - `blockclubchicago.org/category/transportation/feed/` — topic-scoped RSS
     with `Bikes`/`City Hall`/neighborhood categories. (Their robots.txt
     disallows AI-branded crawlers by name; the module must use its own
     honest User-Agent — `OnYourLeftNewsBot/...` — and back off on 403/429,
     treating a block as opt-out, per the Overpass User-Agent precedent.)
   - Google News RSS search (`"bike lane" Chicago when:30d` style) as a
     cross-outlet supplement (Tribune/Sun-Times/suburban outlets); links are
     Google redirect URLs resolved with one non-fatal HEAD each.
   - Dead ends, verified: The Daily Line (paywalled, no feed), ATA blog
     (feed live but empty), WTTW/Sun-Times general firehoses (≈0 relevant
     items per sample; Google News picks up their rare hits anyway).
2. **Licensing:** headline+link+date+source is settled-safe (facts aren't
   copyrightable — *Feist*), and is a strict subset of Block Club's own CC
   BY-ND republishing policy. No body text, no images, ever.
3. **Matching:** street names and alderman surnames match deterministically
   well (Streetsblog's own tag taxonomy proves it). **Council record numbers
   never appear in news text (~50-headline sample: zero)** — do not build a
   record-number matcher. Meeting-specific matching is unreliable (date
   proximity at best).
4. **Volume:** ~4–6 new relevant items/week, spikes to 10+ around events.

## Scope decisions (from the above)

- **Attach at ward / alderman / route level only.** No item↔meeting or
  item↔record claims in v1 — precision over recall; a false "this article is
  about your ward" hurts OYL's trust posture more than a miss. The action
  page shows ward-matched coverage *alongside* the meetings block without
  claiming per-meeting linkage.
- **Matching reads publisher categories first** (exact, case-insensitive
  match against known ward strings, alderman names, route street names),
  headline text second (word-boundary regex requiring street-type suffix for
  streets — "Milwaukee Ave(nue)" yes, bare "Lake" no). Analysis lives in
  aggregate, not the pull module (agenda-items precedent).
- **No LLM anywhere.** Relevance = existing `SAFETY_TOPIC_KEYWORDS` +
  publisher topic categories (`Bicycling`, `Bikes`, …); Google News items are
  pre-filtered by query. "Today's Headlines…" digest posts dropped by title
  pattern.
- **90-day window, capped items.** Published dataset keeps items from the
  last 90 days (cap 60), newest first. Weekly refresh cadence like
  everything else.
- **Tier:** dataset `real` (verbatim titles, real URLs, real dates) with the
  `matches` object explicitly `derived` (`match_tier: "derived"` field),
  mirroring council_records' `data_tier`/`topic_tag_tier` split. Sources
  card carries the neutrality note: these are editorial outlets (Streetsblog
  is advocacy-adjacent); OYL links coverage, it does not endorse it; outlet
  name is always shown.

## Architecture

**`pipeline/pull_news.py`** — new `LIVE_STAGES` entry (order-independent;
placed after `pull_agenda_items.py`). Deterministic, non-fatal:

1. For each feed in `config.NEWS_FEEDS` (url, source label, kind:
   `rss` | `google_news`): GET with `config.NEWS_USER_AGENT`, timeout 30,
   size cap. Any failure → that feed marked `ok: false`, others proceed;
   all-fail → honest empty raw file, never raises.
2. Parse RSS with `xml.etree` (stdlib; no new dependency): title, link,
   pubDate → ISO, categories, source label (Google items: `source` element;
   resolve redirect link with one HEAD, fall back to the redirect URL).
3. Dedup within/across feeds by canonical URL, then by normalized title.
4. Write `raw/news.json`: `{ fetched_at, feeds: [{url, source, ok,
   items: [{title, url, source, published, categories: []}]}] }` — verbatim
   fields only, no analysis. Fetch functions dependency-injected
   (`build_feeds(feeds, fetch_fn=...)`) for tests, per pull_agenda_items.

**`aggregate.py` — new `build_news_items()`**, using already-loaded
`aldermen.json` + `data/main_routes.json` + ward list:

- relevance gate (keywords/categories/query-sourced), digest-post drop;
- `matches.wards: ["1", …]` from "Nth Ward" categories/title, plus wards
  implied by a matched alderman;
- `matches.aldermen: ["Dowell, Pat", …]` from unique-surname or full-name
  match in categories/title (ambiguous surnames require full name);
- `matches.routes: ["milwaukee", …]` route ids from street-name/trail-token
  match in categories/title (street-type suffix required in title text);
- 90-day window, cap, sort; write `site/data/news_items.json` and append a
  `meta.json` sources entry (conditional on ≥1 item, like osm_trails).

**Published schema (SCHEMA.md, CONTRACT_VERSION 1.11 → 1.12):**

```
news_items.json — tier real (matches derived)
{ as_of, note, data_tier: "real", match_tier: "derived",
  items: [{ title, url, source, published,
            matches: { wards: [], aldermen: [], routes: [] } }] }
```

**UI (site):**

- `ward.html` / `ward-model.js`: `newsForWard(newsData, ward)` pure helper →
  "In the news" list on the ward one-pager (title → outlet · date, external
  link, `rel="noopener"`), capped at 5, only rendered when non-empty.
- `action.html` / `action.js`: same helper pattern in-file (action.js
  convention) — ward-scoped coverage section rendered near the meetings
  block, labeled "Recent coverage for this ward" (no per-meeting claim).
- `sources.html` / `sources.js`: new SOURCES card (id `news_items`, tier
  badge via the standard pattern, limitations copy: editorial sources,
  name-matching can miss or mismatch, weekly snapshot, headlines only).
- Tier badges via `BSD.badgeHTML` everywhere (hard product constraint).

**Fixtures:** `make_fixtures.py` gains `build_news()` mirroring the honest
all-feeds-failed raw shape (`feeds: []` + note), so aggregate's file-found
branch is exercised and `--fixtures` runs stay offline. Published
`news_items.json` then has `items: []` — the UI renders nothing, correctly.

**Tests:** `pipeline/tests/test_pull_news.py` (RSS parse on literal XML,
dedup, google-source extraction, degraded shapes); aggregate matching tests
(category ward/alderman/route hits, ambiguous-surname guard, suffix-required
street match, window/cap); `tests/ui/ward-model.test.js` + action model
additions; `test_run_all_order.py` gains the new stage. No new deps.

## Deliberately out (v1)

- Item↔meeting and item↔record-number attachment (evidence: unmatchable).
- Streetsblog per-tag feeds (main feed + categories suffice at this volume;
  tag-slug existence is per-corridor unreliable).
- emit_api.py registration — the agent-API session (p2) is actively editing
  that file; a `news/` endpoint goes in its `planned` list in a follow-up to
  avoid a cross-session collision.
- Body text, summaries, sentiment, or any editorial framing by OYL.

## Validation gate before implementation

Light persona research (docs/research/news-layer/interviews/) with the four
Chicago research subjects from the 2026-07 study — everyday rider, ward
office, pro advocate, community organizer — probing: value of attached
coverage, endorsement-perception risk, false-match tolerance, and where they'd
expect to see it. Kill/trim per their verdicts before code is written.
