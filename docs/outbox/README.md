# Outbox — every pre-drafted outbound message, in one place

All correspondence drafted for a human to send lives here: FOIA requests,
partnership emails, applications, follow-up nudges. If it's send-ready (or
being drafted) and leaves the project when sent, it's in this folder —
never embedded inside another doc (program docs link here instead).

## Naming convention

```
YYYY-MM-DD--<initiative>--<recipient>--<slug>.md
```

- **date** — when first drafted (never changes; status tracks the rest).
- **initiative** — one key from the registry below.
- **recipient** — the org, kebab-case (`cdot`, `city-clerk`, `strava-metro`,
  `amli-eco-counter`, `bike-lane-uprising`).
- **slug** — 2–5 words on what it is.

## Front matter (top of every file)

```
---
status: draft | ready | sent | answered | closed
initiative: <registry key>
to: <email or portal>
subject: <subject line>
drafted: YYYY-MM-DD
sent: —            # fill on send
tracking: —        # reference number, if any
tracker: #33       # the human-tasks issue
---
```

**Lifecycle:** `draft` (needs review/edits) → `ready` (verified, fill
name and fire) → `sent` (date + tracking filled; FOIA items ALSO get their
`docs/foia/log.md` row updated) → `answered`/`closed` (outcome noted at
the bottom of the file — the file is the permanent record; never delete).

## Initiative registry

Canonical keys — used here, in tracker issue #33, and anywhere else human
tasks are labeled. Add new initiatives to this table (don't invent ad-hoc
keys elsewhere).

| Key | Initiative | Home docs |
|---|---|---|
| `foia` | Open-records program (counts, mileage history, council records) | `docs/foia/` |
| `exposure-data` | Ridership/exposure sources — REPORT P1 (Divvy, Strava Metro, counters) | `docs/research/user-needs/REPORT-ux-proposal.md` |
| `blu-partnership` | Bike Lane Uprising data-sharing outreach (optional) — the mock obstruction layer was removed; the site now carries only a plain BLU referral, no partnership framing | `SCHEMA.md` normalized obstruction schema |
| `gov-agent-layer` | AI safe-use guide for public-sector staff | `docs/projects/gov-agent-layer-*.md` |
| `agent-api` | Static agent API under `site/api/v1/` | `docs/superpowers/plans/2026-07-13-agent-api-layer.md` |
| `ux-tranche2` | Second UX tranche (P7–P11) | `docs/research/user-needs/REPORT-ux-proposal.md` |
| `core-site` | Dashboard/pipeline maintenance (refresh reviews, etc.) | `README.md` |
| `oyl-agent-layer` | design-studio `oyl-agent-layer` engagement handoff (caveat co-location, agent skill) | `design-studio/product/oyl-agent-layer/00-HANDOFF.md` |

## For Claude sessions (binding — see CLAUDE.md)

1. Any new outbound draft is created **here**, named per the convention,
   with full front matter — even rough first drafts.
2. Any time work creates, changes, or completes a task only a human can do,
   update **tracker issue #33** in the same working session: correct
   section, `[initiative]` prefix, link to the outbox file or doc.
3. When the human reports something sent/answered: update the file's front
   matter, check the box on #33, and (for FOIA) the `docs/foia/log.md` row —
   all in one pass.
