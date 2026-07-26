# Evidence brief: access mechanisms (feasibility, head-to-head)

> **STATUS: STUB.** This file states the research question and method. The
> kickoff (`../01-kickoff-prompt-access.md`, step 2) fills it with a live-verified brief
> before the study runs. Fill it on a Sonnet evidence agent; **verify every claim
> against live docs/endpoints — do not infer from memory.** Match the depth and
> citation style of `../../user-needs/evidence/*.md`.

## Why this brief exists

The study compares three mechanisms for delivering seamless data access
(`../00-concept.md`): (1) the static JSON API + `llms.txt` that already exists,
(2) a skill riding on top of it with no server, (3) an MCP server on Cloudflare
Workers + D1. The mechanism adjudication in `../05-synthesis-access-architecture.md`
weighs interview preferences and eval results **against real feasibility** — this
brief supplies the feasibility leg, treating all three symmetrically so no
mechanism wins or loses on assumption.

## Questions to answer (with citations)

**Mechanism 1 — static API + llms.txt (what a cold agent can do TODAY):**
- Walk the actual live surface: `site/llms.txt`, `site/api/v1/index.json`, the
  ward/crash/routes/council files, the hand-written schemas, the `_meta`
  provenance envelope. What can a web-capable assistant fetch and correctly
  interpret *right now*? (Pairs with the eval baseline in `../06`.)
- Where does it structurally stop — on-demand computation, cross-file joins, the
  "custom cut" (V3) an agent would have to compute itself from raw files?
- Is it CORS-open / fetchable by the assistants the audiences actually use?

**Mechanism 2 — skills with zero server:**
- What can a Claude Code / agent skill actually do? Confirm concretely that a
  skill can bundle fetch recipes + mandatory caveat framing + output templates and
  ride entirely on mechanism 1 with **no server** (the maintainer's key new fact).
- **Distribution reality (decisive for the "many"):** which assistants/surfaces
  can load a skill at all? Claude Code, Claude.ai, the API, others? Can a
  non-technical person on a consumer assistant consume one, or does a skill only
  reach technical users — in which case "seamless for the many" needs `llms.txt`
  hardening instead. Cite current capability docs.

**Mechanism 3 — MCP on Cloudflare Workers + D1:**
- The Anthropic MCP-server-on-Workers template: current state, what cloning it
  involves, `wrangler deploy` reality.
- D1 fit: ~17k crashes + infra + 311 + council is trivial for SQLite/D1 — confirm
  free-tier limits (request/day, storage, row caps) against live Cloudflare docs.
- **Unauthenticated-endpoint reality:** abuse/cost exposure with no auth (the
  project's "stateless server, smart client" stance means no accounts) — what a
  volunteer maintainer is signing up to own.
- **Remote-MCP client support:** which of the assistants the audiences use can
  actually connect to a remote MCP server today? (Possibly decisive: if audience
  (1)'s assistants can't reach an MCP, the server only serves the technical few.)

## How this feeds the study

- Grounds the `mechanism_preferences` probing for technical personas (Part C of the
  stimulus) in what's real.
- Supplies the feasibility column of the mechanism-adjudication table in `../05`.
- The skills-distribution finding directly resolves honest-hazard #2 in
  `../00-concept.md`.

## Scope fence

Feasibility of *access mechanisms* only. Nothing here touches OYL's pipeline, the
human site, or FOIA-response ingestion (another session owns that).
