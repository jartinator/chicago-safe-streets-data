<!-- Keep PRs focused. One logical change per PR where possible. -->

## What & why

<!-- What does this change, and what problem does it solve? -->

Closes #

## Area / initiative

- Area: <!-- pipeline | site | api | foia | news | bna | data | infra -->
- Initiative: <!-- core-site | foia | exposure-data | blu-partnership | gov-agent-layer | agent-api | ux-tranche2 | none -->

## Checklist

- [ ] Data tiers are labeled honestly (`measured` / `proxy` / `mock`) and stay visible in the UI
- [ ] Schemas in `SCHEMA.md` updated if any published file changed
- [ ] `pipeline/config.py` used for new knobs (no hardcoded ids/paths in modules)
- [ ] Ran the relevant pipeline/site check (`python pipeline/run_all.py --fixtures` and/or opened the affected page)
- [ ] Updated tracker issue #33 if this created/changed/closed a human-only task
- [ ] Outbound correspondence lives in `docs/outbox/` (not embedded in another doc)
