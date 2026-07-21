# Concept: The access layer — making it seamless for people to get OYL's data

**Date:** 2026-07-21
**Status:** goal defined, mechanism open — this study's job is to close that
question. Companion files in this folder carry the stimulus, the persona
reactions, an empirical eval, and the design that comes out the far side.

## The goal in one paragraph

On Your Left! (OYL) already publishes the *official record* of Chicago bike
safety and — since the agent-API layer (`site/api/v1/`, DECISIONS #32) — a
machine-readable mirror of it. What we want to know is whether getting that
data is actually **seamless**, and for whom. Two audiences, weighted **equally**:

1. **The many — non-technical people using their own AI assistant.** A resident,
   an advocate, an alderman's staffer opens ChatGPT or Claude and asks "how
   dangerous is my ward for cycling?" and should get a trustworthy answer — with
   OYL's numbers *and* OYL's caveats — or a one-page brief they could hand to an
   alderman, without ever knowing what a JSON file is.
2. **The few — technical re-users.** A data journalist on deadline, a researcher,
   a civic-tech developer who wants to pull a clean, documented dataset and build
   their own analysis or tool on top of it.

Neither audience outranks the other. **The mechanism is explicitly not decided.**
This study exists to find the smallest thing that makes access seamless for both
— and "the smallest thing" might already be mostly built.

## Three candidate mechanisms, compared head-to-head

We evaluate three ways to deliver the goal. They are **not** mutually exclusive —
the likely answer is layered — but each must earn its place on evidence, not
enthusiasm.

| # | Mechanism | What it uniquely delivers | What it costs | Status today |
|---|---|---|---|---|
| 1 | **Static JSON API + `llms.txt`** | Any web-capable agent can already fetch OYL's numbers at stable URLs; zero moving parts | Pre-baked slices only — no on-demand computation; an agent may still drop caveats | **Exists.** `site/api/v1/` (P1–P5 complete), `site/llms.txt`, hand-written schemas. DECISIONS #32. |
| 2 | **A skill over the static API** | Teaches *any* capable agent how to fetch OYL data **and** frame it with the mandatory caveats, in the user's own assistant — no server | Reaches only assistants that can load a skill; must be authored and kept in sync | **Not built.** Rides entirely on mechanism 1. |
| 3 | **An MCP server** (Cloudflare Workers + D1 free tier) | Live, parameterized computation the static files can't pre-bake — e.g. `aggregate(metric, group_by, filters)`, generated exports/joins | Net-new infra to build, deploy, keep in sync, and *own* (uptime, spend, abuse on an unauthenticated endpoint) — reverses DECISIONS #32 | **Not built.** Explicit overkill test attached. |

**The maintainer's own note, recorded honestly:** we only recently learned that a
skill works *independently of MCP* — it can ride on the static files with no
server at all. Mechanism 2 is therefore the hypothesized "seamless for the many"
unlock, and this study's job is to **test that hypothesis**, not assume it.

## One candidate *shape*: intent-differentiated tools

The idea that kicked this off was to group access by **who's asking and what
they're trying to do** — same data, different framing and output shape:

- **Advocate / resident** — `get_talking_points(ward | corridor)`,
  `get_similar_cases(corridor)`
- **Journalist / researcher** — `get_citable_summary(query)` (source dataset IDs,
  caveats, methodology), `export_dataset(filters, format)`
- **Civic worker / CDOT / alderman staff** — `get_gap_analysis(ward)`,
  `get_publish_candidates()`
- **Developer / civic-tech builder** — `get_schema(dataset)`,
  `get_data_quality(layer)`
- **Flexible backbone** — `aggregate(metric, group_by, filters)` returning a
  downloadable, versioned file; plus metadata tools (`get_data_dictionary`,
  `get_processing_notes`, `get_available_metrics`), raw exports (`export_crashes`,
  `export_infrastructure`, `export_obstruction_data`), and pre-baked joins
  (`get_crash_infrastructure_joins`, `get_obstruction_by_infrastructure_type`).
- Design principle: **stateless server, smart client** — no accounts/auth; the
  tool *descriptions* carry the weight so a calling agent self-selects or asks a
  clarifying question. Every tool returns a **file**, not a UI view.
- Flagged for its own pass: `get_foia_trends()` over Chicago's **public** FOIA log
  (dataset `u9qt-tv7d`) — see the FOIA-seam note below.

**The observation that makes this study tractable:** intent differentiation is
**orthogonal to mechanism.** "Talking points with the caveats attached" could be an
MCP tool, *or* a skill's output template over the static files, *or* a new
pre-baked static artifact (the ward one-pager already half-exists). So we test the
intent *framing* and the delivery *mechanism* as separate questions. A finding that
"residents love packaged talking points" does **not** by itself justify a server.

## Honest hazards (to test in the eval + persona research)

The overkill hazard leads, deliberately:

1. **The MCP is overkill.** A skill plus the existing static API may fully serve
   both audiences. If so, that is a **success** — zero new runtime for a
   volunteer-run project, DECISIONS #32 left intact — not a consolation prize. This
   study is built so this outcome can win on the evidence.
2. **Skills distribution reality.** Do the non-technical audiences even use
   assistants that can *consume* a skill? If a skill only reaches Claude Code
   users, "seamless for the many" needs a different vehicle (e.g. hardening
   `llms.txt` so *any* assistant self-serves). This is an empirical question for
   the `agent-usage` evidence brief, not a guess.
3. **Caveat fidelity.** The entire game for audience (1) is whether an agent's
   answer carries OYL's three load-bearing caveats — dooring undercount, no
   ridership normalization, and the synthetic-obstructions exclusion. If agents
   summarize those away, we've made it *easier* to be confidently wrong.
4. **Trust laundering via packaged outputs.** `get_talking_points`-style packaging
   may be simultaneously the most-wanted and the most-dangerous shape: it strips
   provenance for readability. Probe whether recipients would re-verify anyway.
5. **Audience differentiation may be fiction.** Everyone may want the same two or
   three outputs, and the intent taxonomy may be scaffolding no one needs.
6. **Server ownership.** Uptime, spend, and abuse exposure on an unauthenticated
   endpoint — a real, recurring cost to a volunteer maintainer that the free tier
   reduces but does not erase.
7. **Synthetic-data leakage.** Any flexible compute surface (`aggregate`, exports)
   risks exposing the mock obstructions layer as if it were real. It must not.
8. **`get_foia_trends` value unproven.** The public FOIA log may or may not contain
   enough bike-relevant signal to be worth surfacing.

## Kill criteria (per mechanism)

- **Mechanism 3 (MCP) is killed** if no prioritized job requires computation the
  eval and synthesis show can't be pre-baked or skill-served; **or** if the
  maintainer declines server ownership; **or** if the intent-routing test shows
  agents can't self-select tools from their descriptions.
- **Mechanism 2 (skill) is killed** — or demoted to an `llms.txt` copy change — if
  the eval shows today's static surface *already* delivers caveat-faithful answers,
  or if no assistant the target audience actually uses can consume a skill.
- **Mechanism 1 hardening is the floor.** It can be *sized* but not killed: making
  the data findable and correctly-caveated for a cold agent is table stakes.

## Relationship to the parallel FOIA work

A separate session is planning how OYL will **ingest** data received from
records requests. This study does **not** design or touch ingestion. It asks only
a *preference* question: when new data arrives, how do these audiences want it to
reach them through the access layer, and would they trust it differently? Those
findings are handed to the FOIA session; the pipeline work is theirs. The one
FOIA intersection in scope here is the **public** Chicago FOIA *request log*
(`u9qt-tv7d`) behind the `get_foia_trends` idea — that's FOIA *activity* data, a
public dataset like any other, not response ingestion.
