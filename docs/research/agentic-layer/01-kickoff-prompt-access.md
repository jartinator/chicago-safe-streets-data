# Kickoff prompt

Paste this to a Claude Code session at the repo root to run (or re-run) the
agentic-access-layer study. It is self-contained; everything it references is
checked in under `docs/research/agentic-layer/` and `docs/research/user-needs/`.

---

Run the OYL agentic-access-layer research study defined in
`docs/research/agentic-layer/`. It reuses the method from the user-needs study
(`docs/research/user-needs/`) — same lead-researcher, same personas, same
stated-vs-latent discipline — layered with an agentic dimension and an empirical
eval. Work on a dedicated branch/worktree so nothing collides with other sessions
(this repo is often open in several chats at once — see CLAUDE.md).

**The question this study answers:** what is the *smallest* thing that makes
getting OYL's data seamless for two co-equal audiences — non-technical people
using their own AI assistant, and technical re-users pulling clean data — where
the delivery mechanism (static API / a skill / an MCP server) is **open**, and
"a skill over the existing static API is enough; the MCP is overkill" is a
**valued outcome**, not a failure. Read `00-concept.md` first; it is binding.

**Model usage policy — follow this, it is deliberate.** The strongest model
(Fable/Opus class) is scarce and slow; spend it only where inference quality
compounds. Route as follows:

| Stage | Model class | Why |
|---|---|---|
| Orchestration (you, the main loop) | strongest available | Judgment, quality control, and gatekeeping the stop point live here. |
| Evidence web research (3 domain agents) | Sonnet | Search-and-verify with citation discipline; parallelize. `access-mechanisms.md` must *live-verify*, not infer from memory. |
| Persona interviews (11 agents) | Sonnet | In-character reasoning grounded in a written evidence base. Sonnet holds character and resistance well. |
| Per-interview needs-extraction memos | Sonnet, escalate to strongest if an interview is rich/contradictory | Structured extraction against the extended memo template in `04-researcher-addendum.md`. |
| Seamlessness eval (`06`) | Sonnet cold agents; **strongest** grader | Measuring agent behavior against a rubric, not interviewing. |
| Cross-interview synthesis + the REPORT | strongest available, ONE agent or the main loop itself | The deliverable. Never parallelize, never downgrade. |
| Mechanical formatting, file assembly, link checks | Haiku | No inference content. |

Two warnings, both deliberate:

- **Do NOT run persona interviews on Haiku-class models** — characters flatten
  into agreeable feature wish-lists, exactly the failure this study is designed to
  avoid.
- **AI-topic questions are maximally sycophancy-prone.** A persona that fluently
  *praises* agent tooling, out of world, is a spoiled interview — rerun it. The
  stances in `personas/_agentic-overlay.md` are the countermeasure; hold them.

**Steps:**

1. **Ground and refresh.** Read `00-concept.md`, `DECISIONS.md` #32, `site/llms.txt`,
   `site/api/v1/index.json`, `docs/superpowers/plans/2026-07-13-agent-api-layer.md`,
   and `docs/superpowers/cost-savings-orchestration.md`. Refresh the "what exists
   today" section of `02-stimulus-access-experiences.md` if the API surface changed
   (it churns weekly). Skim `docs/foia/` and open PRs only to *locate* the FOIA
   ingestion seam — reference it, never touch it.
2. **Evidence.** If the three briefs under `evidence/` are stale or stubs, fill
   them (parallel Sonnet agents; every claim names a real org/source, and
   `access-mechanisms.md` must verify each mechanism against live docs/endpoints).
3. **Baseline eval FIRST** (`06`, Parts 1–2), *before* interviews: measure how well
   a cold agent serves the goal with today's surface, and how much a mock skill
   closes the gap. Write results to `interviews/_eval-results.md`. This tells the
   orchestrator where the real gaps are — to *flag* to the interviewer, never to
   feed to personas.
4. **Interviews.** For each of the 11 personas (the 9 in
   `../user-needs/personas/` plus the 2 new ones here), run an interview: the
   persona agent gets its persona file + `../user-needs/personas/_shared-rules.md`
   + `personas/_agentic-overlay.md` + `02-stimulus-access-experiences.md`; the
   interviewer follows `../user-needs/01-lead-researcher.md` +
   `04-researcher-addendum.md` and the guide `../user-needs/03-interview-guide.md`
   + `03-interview-guide-addendum.md`. Write transcript + extended memo to
   `interviews/<persona-id>.md`.
5. **Cross-interview synthesis memo** (`interviews/_synthesis-memo.md`, strongest
   model): recurring themes with attributions, tensions between audiences, needs
   unique to one audience, a `mechanism_implication` tally, and a candid list of
   what this method cannot tell us (simulated personas can't reveal real org AI
   policies in force, real assistant capabilities, or real abuse economics).
6. **Conditional eval Part 3** (intent routing) — run only if intent-differentiated
   tool shapes survive the synthesis memo.
7. **Synthesis → `REPORT-access-architecture.md`** per `05-synthesis-access-architecture.md`.
8. **STOP (hard).** Commit and push. Present the executive summary and the
   decision menu — *harden-static-only / + skill / + MCP subset / full layered
   stack* — with a recommendation, and stop. Implementation decisions belong to the
   maintainer after review. File any human-only follow-ups (e.g. a hosting/spend
   decision) on tracker issue #33 with an `[agent-api]` prefix.
9. **Build** — only after an explicit human go — in fresh sessions per
   `07-build-orchestration.md` (skill-first almost certainly; MCP only if it
   survived the overkill test and the human accepts server ownership).

**Quality gates:**
- Every latent need has an inference basis (a workaround, misreading, or
  documented-world obligation) — never "they'd probably like…".
- Every recommended artifact (a static change, a skill, a tool) traces to named
  participants **and** to an eval measurement, or carries an explicit "no
  measurement available" flag.
- Each MCP tool that survives names, in writing, the computation that **cannot** be
  pre-baked into a static file (the overkill test).
- Both audiences appear in every REPORT section; a proposal that serves only one
  must say so.
- The REPORT contains the mechanism-adjudication table, a kill list, and a
  standalone "the case for stopping at static + skill" section — regardless of the
  verdict.
- New-data sections contain **preferences only**; no ingestion design.
- Commits carry the model co-author trailer.

**Collision guards.** This study writes only under `docs/research/agentic-layer/`.
It never edits `pipeline/`, `site/`, `docs/foia/`, or FOIA items in
`docs/outbox/`. It runs under the existing `agent-api` initiative key; a new
registry key is added to `docs/outbox/README.md` only if the human later approves a
build tranche that creates new human tasks (e.g. standing up hosting).
