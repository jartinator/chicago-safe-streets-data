# Home page — design spec

**Date:** 2026-07-14
**Status:** Approved (design shape + audience decisions confirmed with user)

## Problem

The site drops every visitor straight into a full-screen Leaflet map
(`index.html`). There is no landing page that explains what "On Your Left!" is,
shows headline data, states the purpose, gives different audiences a clear next
action, or promotes the machine-readable **agent layer** (`llms.txt` +
`api/v1/`). New human visitors and AI agents both arrive with no orientation.

## Goals

1. A real landing page at `index.html` that explains the key functions, shows
   live headline data, states the purpose, and routes each audience to a
   concrete action.
2. Promote the agent layer with copy-paste access instructions.
3. Ship it live to GitHub Pages via a clean merge to `main`.

## Non-goals

- No redesign of existing pages, nav, or the design system.
- No changes to `site/data/**` or `site/api/**` (would trip the data-guard CI
  and risk the "never commit fixtures output" rule). The home page *reads*
  existing data at runtime; it never regenerates it.
- No new JS framework or build step — the site is hand-authored static
  HTML/CSS/JS deployed as-is.

## Approach

Follow the existing page pattern exactly: an HTML shell that loads
`assets/js/common.js` + a per-page script, which renders into a `<main>` and
calls `BSD.initPage(activeHref)` to inherit the shared dark header (brand +
nav), footer, provenance banner, tier-badge behaviour, and "data last
refreshed" line.

### Routing change

- The current map `index.html` moves to **`map.html`** (its script tags and
  `<div id="map">` markup unchanged).
- A new **`index.html`** becomes the landing page (shell + `assets/js/home.js`).
- `common.js` `NAV`: the `["index.html", "Map"]` entry becomes
  `["map.html", "Map"]`; add `["index.html", "Home"]` as the first item. The
  brand link (already `index.html`) now correctly points at the landing page.
- Update every other reference to the map living at `index.html`:
  - `site/llms.txt` "Human pages" block (map URL → `map.html`; add the home
    page).
  - `site/sitemap.xml` (add `map.html`; keep `index.html`).
  - Any in-page links that point to `index.html` meaning "the map" (audit with
    grep; repoint to `map.html`).

### Home page sections (rendered by `home.js`)

1. **Hero** — brand name, tagline "Chicago bike safety, on the record", a
   one-sentence purpose, and primary CTAs: *Explore the map* (`map.html`) and
   *Find your ward* (`ward.html`). A secondary line serves residents/cyclists:
   report a hazard via 311 / Bike Lane Uprising (uses `BSD.LINKS`).
2. **Headline data strip** — 4 live stat tiles fetched from
   `api/v1/citywide.json` at load (never hardcoded):
   - Cyclists killed or seriously injured, last 12 mo (`findings` id
     `ksi-trend`, stat `216`, worsening arrow).
   - Protected network share (`protected-share`, `15%`).
   - National low-stress score (`bna-score`, `11/100`).
   - Hit-and-run share (`hit-and-run`, `27%`).
   Each tile shows the finding's `data_tier` badge (via `BSD.badge`) and links
   to `findings.html`. If the fetch fails, the strip renders a graceful
   "see the findings page" fallback rather than broken tiles.
3. **Key functions** — 3 cards describing what the project does: the
   interactive map & network view, the ward-by-ward accountability record
   (crashes + council votes), and the weekly-rebuilt open dataset with labeled
   provenance.
4. **Audience actions** — 4 cards, each a heading + one-line value prop + a
   concrete link:
   - **Journalists & researchers** → findings, methodology, downloadable CSVs.
   - **Advocates & community orgs** → ward one-pagers, council records,
     upcoming hearings, proposed-project tracker.
   - **Developers & AI agents** → the API + `llms.txt` (front-door card;
     detail lives in the agent section below).
   - **Elected officials & staff** → their ward's record and upcoming
     bike/traffic-safety hearings.
5. **Agent layer** — a prominent, visually distinct section that promotes the
   machine-readable layer and tells people how to use it:
   - What it is: every number on the site is also a documented JSON endpoint;
     `llms.txt` is a plain-language index written for LLMs.
   - How to access: copy-paste-able URLs for `llms.txt` and
     `api/v1/index.json`, one `curl` example, and a one-liner to paste into an
     AI assistant ("Read <llms.txt URL> and answer questions about Chicago bike
     safety").
   - Links to `contributing.html` (Downloads & Docs) for the full contract.
6. Shared footer (from `initPage`) — unchanged.

### Styling

Add a scoped block to `assets/css/style.css` under a `.home` root class using
existing tokens (`--accent`, `--ink`, `--ink-soft`, `--card`, `--line`, tier
colors). Responsive with flexbox/grid; stat tiles and audience cards wrap on
narrow screens. No new colors invented; matches the restrained civic
data-journalism look.

## Data flow

`home.js` → `BSD.loadJSON("api/v1/citywide.json")` → pick the four findings by
`id` → render tiles with `BSD.esc` / `BSD.badge`. Hero and card content are
static copy in `home.js`. Purpose text and stat *labels* are authored; the
stat *values* come from the fetched JSON so they stay correct as data
refreshes.

## Testing / verification

- Load the page in the in-app browser against a local static server; confirm:
  header/nav/footer render, the four stat tiles populate from live JSON, every
  link resolves (map, ward, findings, methodology, contributing, llms.txt,
  api/v1/index.json), and the agent section's copy-paste URLs are correct.
- Check `map.html` still renders the map and its nav highlights "Map".
- Run the repo's JS/Python tests (`npm test` / `pytest` as present) — in
  particular any test asserting `NAV` contents in `common.js`; update the test
  if it enumerates nav items.
- No `site/data/**` or `site/api/**` edits, so the data-guard job is not
  triggered; provenance stays `socrata`.

## Delivery

Feature branch off `main` in the (clean, non-OneDrive) checkout at
`C:/Users/jared/projects/chicago-safe-streets-data`. Commit, push, PR, ensure
CI green, merge to `main`. The Deploy-to-Pages workflow publishes `site/` on
merge; confirm the live URL shows the new home page.
