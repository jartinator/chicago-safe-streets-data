# CLAUDE.md

## Concurrent sessions — Marge watches this

This repo is frequently open in **several Claude chats at once**. Session
collisions are now tracked machine-wide by **Marge**, the project manager
(`/marge`, spec at `_system/marge/SPEC.md`).

If you see **`[MARGE] CONCURRENT SESSION`**, another chat is live in this
project — possibly in a different worktree, which still counts.

1. **Stop before editing.**
2. **Move to an isolated git worktree** (this repo keeps them under
   `.claude/worktrees/`), or confirm with Jared that it's safe here.
3. Run `/marge claim chicago-safe-streets-data "<what you're doing>"` so the
   next session sees your task, not just your existence.

The guard only **warns** — it never blocks. The older local guard
(`.claude/hooks/session_guard.py`) is retired and no longer wired; Marge
supersedes it.

## No in-app Browser pane in this repo

Never call `preview_start` or the `mcp__Claude_Browser__*` tools here. A browser
preview opened against this project crashes the Claude desktop GPU process
within ~3–5 seconds and takes the whole app down (reproduced 3× on 2026-07-23;
evidence in `C:\Users\jared\projects\claude-crash-evidence`). Use **Playwright**
against a local `http.server` instead — see the `verify` skill for the snippet.

## Human-task tracking & the outbox (binding for every session)

Two standing conventions; follow them **as you work**, not as cleanup:

1. **Tracker issue #33** ("Human action items — running tracker") is the
   canonical list of tasks only a human can do. Whenever your work creates,
   changes, or completes such a task — a letter that needs sending, an
   application to submit, a contact to make — update #33 in the same
   session: right section, `[initiative]` prefix, link to the artifact.
   When the human reports something sent/answered, check the box and update
   the artifact's front matter (and `docs/foia/log.md` for FOIA) in one pass.
2. **Every pre-drafted outbound message lives in `docs/outbox/`** — FOIA
   letters, partnership emails, applications, nudges. Naming, front matter
   (status/initiative/to/sent/tracking), lifecycle, and the initiative-key
   registry are defined in `docs/outbox/README.md`. Never leave send-ready
   correspondence embedded in another doc; program docs link to the outbox
   file instead.
