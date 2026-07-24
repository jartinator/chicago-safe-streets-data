# Status: Chicago Safe Streets Data

**Last updated:** 2026-07-23
**Phase:** building

## One-line summary
Data pipeline + public static site making Chicago street-safety data legible to non-experts.

## Current state
Active development, often across several concurrent Claude sessions in this repo. Recent work: reframing the home page's agent section toward plain-language access, and banning the in-app Browser pane here (it crashes the desktop GPU process — use Playwright against a local http.server instead).

## Next action
Continue the home agent-section reframe per `docs/` plan + spec.

## Blockers
None external. Internal: concurrent-session collisions — use a worktree under `.claude/worktrees/` when the session guard warns.

---
*Structure note: this project predates the standard `context/` + `product/` layout and keeps its own (`data/`, `pipeline/`, `site/`, `docs/`, `project-context/`). Do not restructure — it is a live git repo. `project-context/` fills the `context/` role; `pipeline/` + `site/` fill `product/`.*
