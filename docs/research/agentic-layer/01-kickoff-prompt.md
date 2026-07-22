# Kickoff prompt — study #1: the agentic layer

Paste this to a Claude Code session at the repo root to run the agentic-layer
research study. It is self-contained. Study #0 (user-needs,
`docs/research/user-needs/`) established the method; this study reuses its
machinery where it fits and replaces personas with agent-consumer scenarios
where it doesn't.

---

Run the OYL agentic-layer research study. Work on a dedicated branch/worktree
so nothing collides with other sessions.

**Research question:** OYL now ships a static agent API (`/api/v1/`,
`llms.txt`, hand-written JSON Schemas, `_meta` envelopes with tier/provenance
/caveats). What should be built next so that AI assistants answering
Chicago-bike-safety questions find OYL, quote it correctly, keep its caveats
attached, and refuse where OYL has no data? Deliverable: a build proposal for
maintainer review — research first, implementation later.

**Prior evidence to build on (read before anything else):**
- `docs/research/user-needs/REPORT-ux-proposal.md` — theme T7 and proposals
  P1/P6: humans admire the layer's structure but demand tested caveat
  propagation, refuse-don't-hallucinate, and provenance in answers. The
  nl-network-planner memo contains an adversarial test protocol sketch.
- `docs/research/news-layer/` and `docs/research/user-needs/validation/` —
  the concept → feasibility → persona-validation → live-audit loop this
  project already trusts. Reuse it.
- `README.md` (agent API section), `site/llms.txt`, `SCHEMA.md` (v1.14+
  agent-API contract and the caveats addition, if merged).

**Model usage policy — follow this, it is deliberate.**

| Stage | Model class | Why |
|---|---|---|
| Orchestration (you, the main loop) | strongest available | Judgment, QC, final synthesis. |
| Landscape & feasibility web research | Sonnet, parallel | Search-and-summarize with citation discipline: how assistants/crawlers actually consume llms.txt and static APIs in 2026; MCP adoption; how comparable civic-data projects serve agents; discovery/SEO-for-agents reality vs. folklore. Every claim names a real org/tool/spec. |
| Live audits | Sonnet agents driving real tools | Empirical, not speculative: ask real assistants OYL-answerable questions; record discovery, correctness, caveat survival, refusal behavior. |
| Consumer-scenario interviews | Sonnet | The "personas" here are humans-behind-agents (a journalist asking ChatGPT, an aide asking Claude, a developer wiring MCP) grounded in study #0's evidence bases where they overlap. |
| Synthesis + build proposal | strongest available, ONE pass | The deliverable. Never parallelize, never downgrade. |
| Formatting/link checks | Haiku | No inference content. |

**Steps:**

1. Inventory the current layer as-built (endpoints, schemas, llms.txt
   guidance, what P1/P6 shipped) into `02-layer-inventory.md` — the stimulus.
2. Feasibility/landscape briefs (`evidence/`, parallel Sonnet agents, cited):
   (a) how major assistants discover & fetch site data today (llms.txt
   reality check); (b) MCP — what shipping a server would mean for a static,
   volunteer-run project, incl. hosting-free options; (c) how agents handle
   caveats/provenance in retrieved data — known failure modes; (d) civic-data
   precedents serving agents; (e) evaluation harnesses for answer fidelity.
3. Live audit: a written protocol (extend the nl-network-planner sketch:
   questions with known answers, questions OYL cannot answer, caveat-carriage
   checks), executed against at least two real assistant surfaces; transcripts
   into `audits/`.
4. Consumer-scenario interviews (3–5, not 9): journalist-via-assistant,
   ward-staffer-via-assistant, civic developer, accessibility-motivated
   resident. Stated vs. latent needs discipline per
   `docs/research/user-needs/01-lead-researcher.md`.
5. Synthesis → `REPORT-agentic-proposal.md`: what to build (candidates to
   evaluate honestly, not presume: MCP server, eval suite in CI, fetch
   recipes, structured-answer endpoints, refusal affordances, per-question
   deep links), what NOT to build (kill list with evidence), sequencing,
   method limits.
6. Commit everything, push, open a PR. Present the executive summary and
   stop — build decisions belong to the maintainer.

**Quality gates:** every feasibility claim names a checkable source; audit
transcripts are verbatim and dated; no proposal may assume agent behavior
that an audit could have tested but didn't; the report must state explicitly
whether the static-files-only constraint (no server, no accounts) survives
contact with each proposal; caveat-carriage (the study-#0 T7 finding) must be
empirically measured, not re-asserted.
