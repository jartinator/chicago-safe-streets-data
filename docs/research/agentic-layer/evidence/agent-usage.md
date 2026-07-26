# Evidence brief: how these audiences actually use AI

> **STATUS: STUB.** States the research question + method. The kickoff
> (`../01-kickoff-prompt-access.md`, step 2) fills it before the study runs, on a Sonnet
> evidence agent, live-verified, in the citation style of
> `../../user-needs/evidence/*.md`.

## Why this brief exists

The interviews probe whether each persona would use their own AI to get OYL's data
and trust the result. Their `agent_stance` (memo template, `04`) must be grounded in
how these worlds *actually* use AI today — not in the model's guesses. This brief
also resolves honest-hazard #2 in `00-concept.md` (skills-distribution reality).

## Questions to answer (with citations)

- **Newsroom AI policy & data-journalism practice** — what Chicago-area and
  national newsrooms permit (AI-assisted research vs AI-generated published facts),
  verification norms. Grounds `chi-data-journalist` and `chi-investigative-reporter`.
- **Government-worker AI restrictions** — public-sector policies on putting data
  into / consuming outputs from external AI; anchor to
  `docs/projects/gov-agent-layer-proposal.md` and `-scoping.md`. Grounds
  `chi-cdot-planner` and `govtech-vendor`.
- **Advocacy / organizer adoption** — how campaigners and community groups use (or
  distrust) AI for civic data work; volunteer-time economics.
- **Everyday consumer assistant use for civic questions** — how ordinary residents
  ask assistants factual local questions, and documented cases of confident wrong
  answers (the harm mode behind `chi-everyday-rider`).
- **Skills-distribution reality (decisive)** — which assistants/surfaces can load a
  skill at all (Claude Code / Claude.ai / API / others), and whether a non-technical
  person on a consumer assistant can consume one. If skills are niche, "seamless for
  the many" needs `llms.txt` hardening instead. Coordinate with
  `access-mechanisms.md`.
- **Developer / MCP ecosystem** — how civic-tech builders evaluate APIs and MCP;
  maintenance/bus-factor concerns. Grounds `chi-civic-tech-dev`.

## Feeds

The 13-row stance table in `../personas/_agentic-overlay.md`; the four new personas;
honest-hazard #2. **Scope fence:** describes AI *usage*, touches no OYL pipeline/site
and no FOIA-response ingestion.
