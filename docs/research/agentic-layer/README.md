# OYL agentic-access-layer study

A re-runnable multi-agent study answering one question: **what is the smallest
thing that makes getting OYL's data seamless** — for two co-equal audiences
(non-technical people using their own AI assistant; technical re-users pulling
clean data) — where the delivery **mechanism is left open** (static API / a skill /
an MCP server, head-to-head) and "stop at static + skill, the MCP is overkill" is a
**valued outcome**. Mirrors `../user-needs/` (method) and `../news-layer/`
(replication pattern). Research first; implementation later, human-gated.

## Layout

| Path | What it is |
|---|---|
| `00-concept.md` | Goal, three-mechanism head-to-head, intent tools as one candidate shape, honest hazards, kill criteria, FOIA-seam fence |
| `01-kickoff-prompt.md` | Paste-to-run orchestration: model routing, 9 steps, quality gates, collision guards, hard stop before any build |
| `02-stimulus-access-experiences.md` | Stimulus: what exists today + mechanism-blind experience vignettes + (technical-only) mechanism menu + new-data question |
| `03-interview-guide-addendum.md` | Agentic dimension layered on `../user-needs/03` |
| `04-researcher-addendum.md` | Ground rules 7–9 + extended memo template (incl. `mechanism_implication`) |
| `05-synthesis-access-architecture.md` | Strongest-model synthesis → the REPORT: mechanism adjudication + specs + kill list |
| `06-seamlessness-eval.md` | Empirical protocol: cold-agent baseline, skill uplift, conditional intent routing |
| `personas/` | Agentic overlay + 4 new personas (the 9 base personas live in `../user-needs/personas/`) |
| `evidence/` | Three cited briefs (stubs until a run fills them) |
| `interviews/` | Run output: transcripts, memos, `_synthesis-memo.md`, `_eval-results.md` |
| `REPORT-access-architecture.md` | Run output: the deliverable |
| `BRIEF.md` | Run output: plain-language what-shipped-why (incl. a build-nothing outcome) |

## Roster — 13 interviews

The 9 personas in `../user-needs/personas/` (via `personas/_agentic-overlay.md`, no
edits to their files) **plus** four new here: `chi-data-journalist` (daily),
`chi-investigative-reporter` (accountability), `chi-civic-tech-dev`, `govtech-vendor`.

## Design principles

- **Goal-first, mechanism-agnostic.** The mechanism is earned by evidence, not
  assumed. DECISIONS #32 (static, no server) is a stance the research may keep or
  overturn — either is a valid result.
- **Two audiences, equal weight.** Every REPORT section addresses both.
- **Measured, not just asked.** The eval (`06`) gives the head-to-head hard data so
  an MCP must beat a *measured* static+skill baseline.
- **New data = preferences only.** Ingestion is another session's work; the only
  FOIA intersection here is the *public* request log (`u9qt-tv7d`).

## Not yet authored

`07-build-orchestration.md` (the build playbook, mirroring
`../../superpowers/cost-savings-orchestration.md`) is written **after** a run
produces `REPORT-access-architecture.md` and the maintainer picks a mechanism, so
its phase map is transcribed from the approved report rather than guessed.

## Re-running

Idempotent, like the parent study: refresh the "what exists today" section of `02`
and the `evidence/` briefs against the current product, then re-run. Diff
`REPORT-access-architecture.md` across runs to see how a shifting product surface
moves the mechanism verdict.
