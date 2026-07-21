# Stimulus: access experiences

What participants react to. Present in order. **Parts A–B and D go to everyone;
Part C only to technical personas** (dev, journalist, investigative reporter,
govtech vendor). Never name a mechanism to a non-technical persona — mechanism
choice is invisible to them and contaminates the interview (see `04`, rule 7).

## Part A — what exists today (react first)

OYL already publishes machine-readable data any web-capable AI assistant can fetch:
- `site/llms.txt` — a plain-text catalogue with fetch recipes.
- `site/api/v1/` — versioned JSON: a machine index, citywide + per-ward + per-route
  + council files, crash slices, hand-written schemas, and a `_meta` provenance
  envelope. CORS-open. Synthetic (mock obstruction) data is excluded by rule.

Translate per audience: *non-technical* — "ask a capable assistant 'how dangerous
is Ward 40 for cycling?' and it can already pull our numbers"; *technical* —
"versioned JSON, documented schemas, stable URLs you can build on." Honest limits:
fixed pre-baked slices, no on-demand computation, weekly refresh, and **an
assistant may still drop the caveats** when it answers.

## Part B — experience vignettes (mechanism-blind; everyone)

Describe *what it would be like*. Capture the reaction **before** elaborating; per
vignette ask: would you use this, in what concrete moment, what must travel with
it, and what shape do you want it in (spoken prose / one-pager / table / raw CSV)?
The mechanism tag in brackets is a **researcher-only** note — never spoken aloud.

- **V1 — Ask and trust.** You ask your own assistant a ward/route safety question;
  the answer arrives with OYL's caveats attached and a link to check it. *[1 / 1+2 / 3]*
- **V2 — The hand-off artifact.** The assistant produces a one-page brief or
  talking points you could hand an alderman or read in a meeting, caveats printed
  on it. *[1 (ward one-pager half-exists) / 2 / 3]*
- **V3 — The custom cut.** You ask for a breakdown nobody pre-baked — "crashes by
  lighting condition on protected vs painted lanes since 2022" — and get a
  downloadable table. *[only 3, or a capable agent computing over raw static files
  — exactly what the eval tests]*
- **V4 — The citable pull** (technical). A documented dataset with source IDs,
  methodology, and caveats, fetchable in one command, stable enough to publish or
  build on. *[1 today / 2 adds guidance / 3 adds export_dataset]*
- **V5 — What's new.** When OYL adds data (e.g. from a records request), your
  assistant/tooling knows it's there and knows how much to trust it. *[feeds Part D]*
- **V6 — The gap brief** (civic worker). A where-are-the-holes read on your ward,
  framed for internal use. *[1+2 / 3 get_gap_analysis]*
- **V7 — What's everyone asking for.** A view of what the public repeatedly
  requests from the city about bikes/streets that isn't published yet. *[3
  get_foia_trends over the public FOIA log; or a pre-baked static artifact]*

## Part C — the mechanism menu (technical personas only)

These personas can compare mechanisms in-world. Present the three plainly (static
API + llms.txt / a skill with no server / an MCP server) with honest trade-offs,
and the intent-differentiated tool taxonomy from `00-concept.md` as one candidate
API shape. Their preferences — plain JSON vs an MCP client, "will this be up in two
years?", schema stability, self-hosting — are first-class data.

## Part D — the new-data research question (preferences only)

OYL is separately pursuing records-request data (another workstream owns
ingestion). Ask only: *when new data reaches OYL, how should it reach you through
this access layer, and would you trust it differently from the existing tiers?*
**Do not** design ingestion; if a participant starts spec'ing pipelines, note it
and steer back to preferences.

## What this layer deliberately would NOT be

No accounts, no auth, no memory, no real-time — nothing the human site doesn't
already refuse. Any access mechanism is a *view* over the same weekly-refreshed,
provenance-badged data, never a new source of truth.
