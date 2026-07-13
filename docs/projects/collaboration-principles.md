# Collaboration principles — working *with* government, not at it

Interaction and design principles distilled from the post-report discussion
(July 2026) and the user-needs study. These govern how OYL-adjacent work
approaches agencies, FOIA, and any tooling offered to public staff. They sit
alongside the product's existing provenance ethos (badges, caveats, read-only).

## The stance

1. **It's not them, it's the system.** Default assumption: public servants
   want the system to work and are constrained by under-resourced
   institutions, not personal unwillingness. Design every interaction so a
   willing insider can say yes cheaply. (Corroborated by the chi-cdot-planner
   interview: an independent evidence layer is *useful cover* for staff who
   already want to act.)
2. **No goose chases.** Never send an agency searching its own institutional
   memory from scratch. Before any request, do the reference work ourselves:
   name the document, the date, the page, the publicly named author. A FOIA
   that says "the dataset behind Table 3 of report X (2023, p. 14)" is a
   favor; "any bike counter data" is a burden.
3. **Asks arrive with an off-ramp toward openness.** Where appropriate,
   attach a short, optional "open data enablement" note: how the requested
   data could be published sustainably (portal dataset vs. one-off export),
   framed as a resource, never as instruction. The goal of a good FOIA is to
   make the *next* FOIA unnecessary.
4. **Advisory, not directive; bounded, not sneaky.** Anything offered to
   government staff (guides, prompts, a future agent layer) states its own
   limits up front: what it can help with (public-facing practice), what it
   must not receive (non-public information), and why — respecting agency
   policy is a feature of the tool, not an obstacle to it. No tool we ship
   should function as a workaround of an institution's rules.
5. **Relationships before launches.** New offerings go first to known
   contacts inside agencies (the "open data allies" list), not to a public
   launch. Trust is built person-to-person; tools follow the relationship.
6. **Volume is a last resort, not a strategy.** Repeated requests can
   legitimately nudge an agency toward publish-by-default — but the primary
   mode is making each single request maximally easy to fulfill. We escalate
   frequency only when specificity has demonstrably failed.
7. **Symmetric honesty.** The same provenance discipline OYL applies to data
   (tiers, as-of dates, caveats that travel) applies to our claims *about*
   agencies: if we assert a dataset exists, we cite where we saw it; if a
   crawl came up empty, we record the dead end so no one re-litigates it.

## Where these are operationalized

- `docs/research/followups/agent-research-crawl-foia.md` — the reference-
  crawl method (principle 2), first executed for CDOT counter data
  (`docs/foia/cdot-counter-crawl.md`).
- `docs/foia/log.md` — request tracking; add an "allies" note per contact
  where a relationship exists (principle 5). Keep names out of the public
  repo unless already public.
- `docs/projects/gov-agent-layer-proposal.md` — the standing-tool extension
  of principles 1 & 4; scoping gated on the policy research in
  `gov-agent-layer-scoping.md`.
- The FOIA enablement blurb template (principle 3) lives with the crawl
  output and is reusable per request.
