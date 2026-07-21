# Agent prompt: access-architecture synthesis

> **Model:** strongest available. One agent, one pass, full context. The highest-
> leverage step — do not parallelize or delegate downward.

Turn the interviews (`interviews/`), the cross-interview memo, the eval results
(`interviews/_eval-results.md`), the evidence briefs, and the stimulus into a
**decision the maintainer can act on**: what to build, in what order, on which
mechanism — where "harden the static API + a skill, no server" is a valid winner.
Respect the product: static, read-only, volunteer-run, provenance-obsessed
(DECISIONS #32).

## Process (run in order, show your work)

1. **Affinity map.** Cluster every stated + latent need across memos into themes;
   keep participant attributions; tag each theme by audience (non-technical /
   technical) so the co-equal-audiences requirement is checkable.
2. **Jobs ledger.** Per theme: the job-to-be-done, audiences served, and current
   coverage — `served-by-site / served-by-static-API-today / partially / unserved /
   actively-harmed` — plus "agent-reachable today?" from the eval baseline.
3. **Experience requirements.** Per surviving job: which Part-B vignette(s) it
   needs, at what fidelity, for which audience.
4. **Mechanism adjudication (load-bearing).** For each required experience, name
   the **cheapest mechanism that delivers it**, weighing three evidence streams:
   interview memos, eval measurements, and `evidence/access-mechanisms.md`. Strict
   escalation — each step requires *documented failure* of the previous:
   (a) harden mechanism 1 (llms.txt copy, new pre-baked static artifacts, schema/
   doc fixes); (b) a skill (fetch recipes + mandatory caveat framing + output
   templates); (c) an MCP tool, **only** for computation provably not pre-bakeable
   (the V3 class) — and each surviving tool must name that computation in its spec.
   > A server must earn its way past DECISIONS #32 **job-by-job**; "other projects
   > have one" is not evidence. Landing on static + skill is a success outcome.
   The likely landing zone is layered (skill + hardened static for the many;
   exports/aggregate, MCP only if warranted, for the few) — but the layers must be
   *earned in this table*, not assumed.
5. **Specs for what survives.**
   - *Static-hardening spec* — concrete llms.txt / api-v1 / pre-baked-artifact
     changes, each traced to evidence.
   - *Skill spec(s)* — directory name; two-key frontmatter (`name` = dir,
     `description` = a "Use when…" trigger, per `.claude/skills/` convention);
     content outline (fetch recipes, the three caveats verbatim — dooring
     undercount, no ridership normalization, synthetic-obstruction exclusion —
     output templates per audience, the no-synthetic-data rule); the distribution
     answer (which assistants can consume it — a finding from `evidence/
     agent-usage.md`, not an assumption); evidence trace.
   - *MCP spec* (only if a tool survives) — per tool: name, audience, the
     **description string verbatim** (descriptions carry the weight; eval Part 3
     tests them), inputs, output file format, source files, caveat-propagation
     rules, the named non-pre-bakeable computation, evidence trace.
   - *New-data findings* — addressed to the FOIA session: preferences + quotes.
     Contract line: ingestion design/implementation belongs to that workstream.
6. **Kill list.** A disposition (build / defer / kill) for **every** item in the
   `00-concept.md` taxonomy — including each intent tool and `get_foia_trends` —
   so nothing dies by silence.
7. **The case for stopping at static + skill.** Mandatory regardless of verdict:
   state what static + skill already does, and what *future* evidence would justify
   a server later.

## Report format → `REPORT-access-architecture.md`

- **Executive summary** — the decision menu (harden-static-only / + skill / + MCP
  subset / full layered) and your recommendation, one page.
- **Themes & evidence** — the affinity map, stated vs latent marked, attributed.
- **Mechanism-adjudication table** — the step-4 output.
- **Specs** — step 5.
- **Sequencing** — tranche 1 = zero-runtime items (static hardening + skill),
  almost certainly first; any MCP tranche gated on the human's server-ownership
  decision.
- **New-data findings** — for the FOIA session.
- **Kill list.**
- **Method limits** — inherited verbatim from the researcher's candid list, plus
  study-specific limits (simulated personas can't reveal real org AI policies in
  force, real assistant capabilities, or real abuse economics).

Every proposal traces to named participants (stated or latent) **and** to an eval
measurement or an explicit "no measurement available" flag. No "users want."
