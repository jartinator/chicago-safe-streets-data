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
