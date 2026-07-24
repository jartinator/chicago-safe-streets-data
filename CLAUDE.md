# CLAUDE.md

## Concurrent sessions — don't work in the same tree

This repo is frequently open in **several Claude chats at once**, all pointed at
the same folder. When two chats edit files in the same working directory they
step on each other ("someone is working in it RIGHT NOW, all my files are
changing").

A session guard runs automatically (see `.claude/hooks/session_guard.py`, wired
in `.claude/settings.json`). If it reports **`⚠️ CONCURRENT SESSION DETECTED`**,
another chat is already live in this exact folder. When you see that warning:

1. **Stop before editing.** Do not start Writing/Editing files in the shared
   folder.
2. **Move to an isolated git worktree** for your work (this repo already keeps
   worktrees under `.claude/worktrees/`), or explicitly confirm with the user
   that it's safe to proceed here.
3. Prefer working in a dedicated worktree for any real editing anyway, rather
   than the shared main checkout.

The guard only **warns** — it never blocks you. It's on you (and the user) to
move. A warning that names a *different* folder than the one you're editing is
not a collision; only same-folder warnings matter.

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
