# Cost-savings orchestration playbook — agent-api-layer phases 3+

*Living process doc, not a point-in-time plan — update it in place as the approach
changes. Companion to `docs/superpowers/plans/2026-07-13-agent-api-layer.md` (the
feature plan itself; this doc is how phases 3 onward get built cheaply).*

You are the controller, running on **Sonnet** (cost mode — standing default; the user
is on limited premium credits). You never write implementation code yourself except
mechanical generate/verify/commit steps. Sequential phases, EACH IN ITS OWN FRESH CHAT
SESSION. Each phase ends at a merge-ready PR; merge only if the user asks (they've been
asking each time so far — offer it, don't assume).

## Invariants
- Work ONLY in the worktree `C:\Users\jared\OneDrive\chicago-safe-streets-data\.claude\worktrees\agent-api-layer-p1`.
  ALWAYS pass explicit paths (`git -C $wt`, `cd` in Bash) — a session resume resets the
  shell cwd to the main checkout where another live session works. (This bit us once.)
- One phase = one branch `claude/agent-api-layer-pN` cut from fresh `origin/main`.
- Ledger: `<worktree>\.superpowers\sdd\progress.md` — update after every task; trust it
  + `git log` over memory after compaction. (This file is gitignored scratch, local to
  the worktree — it does NOT travel via git. This playbook does, via this repo file.)
- Briefs/reports for any given phase: scratchpad, not committed — see the ledger for
  the live path each session uses.

## Cost mode (standing default, not special-case)
- Controller = Sonnet, always. Fable/Opus only if the user explicitly asks for that phase.
- ONE phase = ONE fresh chat session. Never continue Phase N+1 in the session that did
  Phase N — the point is a cold context that reads only the ledger + this file, not the
  accumulated transcript (context size is the dominant per-turn cost). See "Phase end"
  below for how the handoff works.
- ONE implementer task per phase where the scope is well-specified (fold multi-area
  phases like P3's routes+council into a single brief) + ONE final whole-branch review.
  Drop per-task review loops unless a task is genuinely risky/ambiguous — the final
  review is the real gate; per-task review was Phase-1/2 thoroughness we can no longer
  afford by default.
- Final whole-branch review: Sonnet by default; escalate to Opus only for a phase with
  subtle logic (e.g. schema/validation correctness in P4) or if a Sonnet review comes
  back uncertain.
- Implementer model: sonnet for multi-file/prose-spec work; haiku for pure single-file
  transcription tasks (rare at this phase's granularity).
- Controller-run directly (no agent): generating output files, verify runs, commits, PR,
  merges, the merge-origin/main-and-regenerate dance.
- Keep summaries to the user terse — findings and decisions, not process narration.

## Loop per task (when per-task review IS warranted — see cost mode above)
1. Write brief (exact values, binding constraints, report contract). Record base SHA.
2. Dispatch implementer — Agent(general-purpose, model per Cost mode), synchronous.
   Prompt = implementer template (see skill `subagent-driven-development`): brief path,
   scene-setting, TDD required, full-suite green, commit w/ trailer
   `Co-Authored-By: Claude <model-name> <noreply@anthropic.com>`, report file, <15-line
   reply.
3. Review package: `bash <skill-dir>/scripts/review-package BASE HEAD` (skill dir =
   `C:\Users\jared\.claude\plugins\cache\superpowers-marketplace\superpowers\6.1.1\skills\subagent-driven-development`,
   version number may drift — glob for the current one if this path 404s).
4. Dispatch task reviewer (same-skill template; brief+report+diff paths, global
   constraints verbatim; never pre-judge findings).
5. Critical/Important findings → SendMessage back to the SAME implementer agent id with
   the findings; then regenerate package and SendMessage the SAME reviewer for re-review.
   (SendMessage resumes run in background — collect via TaskOutput block=true.)
   Minors → park in ledger for final-review triage.
6. Mark task complete in ledger + TaskUpdate.

## Phase end (every phase ends this way — this IS the deliverable, not optional)
1. Final review clean (or one fixer dispatched with ALL findings, then re-review).
2. `git merge origin/main` (expect it — many parallel sessions land PRs constantly);
   generated site/api conflicts resolve by regenerating (see Standing decisions), never
   hand-merging JSON; run full test suite + check_provenance after.
3. Push → `gh pr create` (body: what shipped/decisions made/verification; footer
   "🤖 Generated with [Claude Code](https://claude.com/claude-code)").
4. Update the ledger: mark phase DONE, PR number, and write the "NEXT: Phase N+1" block
   the next cold session reads first.
5. Ask the user whether to merge now; if yes, watch CI (`gh pr checks --watch`) then
   `gh pr merge --merge`, re-verify (tests + check_provenance) after merge lands.
6. **Write the next phase's kickoff prompt** (see template below) and give it to the
   user verbatim, framed as "paste this into a new chat to start Phase N+1." Do this
   EVERY phase from now on without being asked again.
7. If this phase's work revealed a process change worth keeping (a new standing
   decision, a fixed bug in the loop, a cost-mode tweak) — edit THIS FILE in place and
   commit it (small standalone doc PR, or bundled with the phase PR if trivial) so the
   next fresh session inherits it. This file is the persistence mechanism; the
   scratchpad ledger is not (it's gitignored, worktree-local, and vanishes if the
   worktree is ever recreated).

### Kickoff-prompt template (fill in and hand to the user at every phase end)
```
Continue the agent-first API layer build: Phase <N> (<one-line scope>).

Read the orchestration playbook and ledger first, in this order:
1. docs/superpowers/cost-savings-orchestration.md (in the repo — read it from
   origin/main or the worktree, whichever is available first)
2. C:\Users\jared\OneDrive\chicago-safe-streets-data\.claude\worktrees\agent-api-layer-p1\.superpowers\sdd\progress.md

Then follow the playbook exactly: fresh branch claude/agent-api-layer-p<N> off
origin/main, cost-mode loop (one implementer task + one final review), merge
origin/main before the PR, hand me a merge-ready PR, and write Phase <N+1>'s
kickoff prompt at the end the same way this one was written for you.

I'm running this chat on Sonnet to keep cost down — stay on Sonnet unless a
step in the playbook calls for a different model.
```

## Standing decisions (apply to all phases)
- Envelope omits `schema`/`docs` keys until Phases 4/5 publish their targets. index.json
  lists only endpoints that exist; `planned` shrinks as phases land.
- CONTRACT_VERSION: do NOT hardcode assumptions — unrelated PRs bump it (main hit 1.13
  via the news layer #37/#39 during Phase 2). The API just tracks meta.json's value via
  config; regenerating always reconciles it. There is no "stays at X until phase Y" rule.
- Mid-phase main advances are normal (many parallel sessions). At each phase boundary and
  before every PR: `git merge origin/main`; generated site/api conflicts resolve by
  RE-RUNNING `python pipeline/emit_api.py` then `git add site/api` — never hand-merge JSON.
  git prune "Permission denied" lines on other sessions' worktrees are harmless noise —
  they're just git failing to delete a directory another live session's worktree still
  has locked; the actual git operation you ran still succeeds.
- Synthetic data (obstructions) NEVER in the API namespace except the index disclaimer.
- `_meta.generated_at`/`provenance` copied verbatim from site/data/meta.json.
- emit_api reads only committed site/data (no network, no raw/, no geometry ops).
- comparable_danger_score described as "relative concern rank among wards, higher =
  worse — not absolute risk" wherever mentioned.
- Phase 2 deviation (documented): ward files omit "top corridors" — corridors.json has
  no ward linkage/geometry, an honest per-ward mapping needs aggregate.py support first.

## Phase map (plan §6 of the agent-api-layer plan) — COMPLETE as of Phase 5
- P1: DONE, merged PR #32 — index/citywide/corridors skeleton + pipeline wiring.
- P2: DONE, merged PR #36 — wards/index.json, wards/ward-NN.json, crashes/ward-NN.json,
  size tests, pruning.
- P3: DONE, merged PR #43 — routes/index.json + routes/line-<id>.json;
  council/{index,records,aldermen}.json.
- P4: DONE, merged PR #44 — schemas/*.schema.json (hand-written, normative), check_api.py,
  jsonschema dev dep, data-guard step. tests.yml (separate pytest CI) intentionally
  skipped as optional (repo has no pytest CI) — still available as a standalone PR later.
- P5: DONE, PR #45 (open) — llms.txt, sitemap.xml, robots.txt, HTML head links + JSON-LD,
  README/CONTRIBUTING/SCHEMA.md section, DECISIONS entry, CONTRACT_VERSION note.

This was the last phase in the plan (`docs/superpowers/plans/2026-07-13-agent-api-layer.md`
§6). There is no Phase 6. If new work surfaces (parked minors, newly-discovered bugs), scope
it as its own plan/brief — don't assume the phase-N loop above continues automatically.

## Gotcha: this site is a GitHub Pages *project* page — no root-relative hrefs
`SITE_BASE_URL` is `https://jartinator.github.io/chicago-safe-streets-data` (no `CNAME`,
so it's served under a path, not at the domain root). Any HTML written into `site/*.html`
must use **relative** hrefs (`api/v1/index.json`, not `/api/v1/index.json`) for anything
meant to resolve under the site's own path — a root-relative href resolves to
`jartinator.github.io/...` and silently 404s in production while looking correct in a
local file-server preview that happens to serve from the repo root. Bit Phase 5's
`<link rel="alternate">` tags (caught in final review, fixed before merge — see P5 ledger
entry). Absolute URLs (built from `SITE_BASE_URL` itself, e.g. JSON-LD `url`/`contentUrl`,
or any URL embedded inside a JSON/text payload like llms.txt) are correct as-is and don't
need this treatment — only literal `href="/..."` attributes in committed HTML.
