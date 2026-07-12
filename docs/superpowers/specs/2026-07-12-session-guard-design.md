# Session Guard — preventing concurrent-session file collisions

**Date:** 2026-07-12
**Status:** Design, awaiting approval

## Problem

Multiple Claude Code chats are opened against the **same working directory**
(`chicago-safe-streets-data`, the main worktree). Because they share one set of
files on disk, when one chat edits a file the others see their files changing
underneath them ("someone is working in it RIGHT NOW, all my files are
changing"). The chats step on each other's work.

The repo already uses git worktrees (`.claude/worktrees/*`), but nothing steers
new sessions into their own worktree or warns when two sessions land in the same
folder. There is currently no `CLAUDE.md` and no committed `.claude/settings.json`.

## Goal

Make concurrent sessions in the same folder **visible and self-correcting**:

1. Detect when another Claude session is live in the same working directory.
2. Warn loudly — in-chat, to both the user and the agent — at session start and
   before edits.
3. Tell the agent (via `CLAUDE.md`) to move to its own worktree when a collision
   is detected.

Non-goal: hard-blocking edits. The guard **warns and allows** — it must never
trap the user with a false positive.

## Approach

Two cooperating layers ("both", per the enforcement decision):

- **Hard layer** — a heartbeat script + hooks that the harness runs automatically.
- **Soft layer** — a `CLAUDE.md` rule telling the agent what to do about a warning.

### Component 1: heartbeat store

A per-session heartbeat file recording that a session is alive in a directory.

- **Location:** OS temp dir, **not** OneDrive — e.g.
  `%TEMP%/claude-session-guard/<hash(cwd)>/<session_id>.json`.
  Rationale: heartbeats written into the OneDrive-synced repo would sync across
  machines and generate exactly the kind of file churn we are trying to stop.
- **Keyed by** a hash of the absolute working directory (`cwd`), so two sessions
  in the *same* folder collide but sessions in *different* worktrees do not.
- **Contents:** `{ session_id, cwd, pid, last_seen (ISO-8601) }`.
- **Liveness:** a heartbeat is "live" if `last_seen` is within **15 minutes**.
  Active chats refresh on every prompt and stay live; closed chats go stale and
  are ignored (and cleaned up opportunistically).

### Component 2: guard script

`.claude/hooks/session_guard.py` (Python 3, cross-platform; 3.12 confirmed
available). Reads the hook event JSON from stdin (`session_id`, `cwd`, `hook_event_name`)
and dispatches on the event:

- `--event write` (SessionStart / UserPromptSubmit): write/refresh this session's
  heartbeat, then scan sibling heartbeats for the same `cwd` that are **live** and
  have a **different** `session_id`. If any found, print a warning to stdout so it
  is injected into the conversation as additional context.
  **Debounce:** SessionStart always warns if a collision exists; UserPromptSubmit
  re-warns only when the set of colliding sessions *changes* (a new chat appears),
  not on every prompt — avoids nagging. State is tracked in the session's own
  heartbeat file (`last_warned_peers`).
- `--event clear` (Stop / SessionEnd): delete this session's heartbeat file.

Design principles: standard library only, fail-open (any error → exit 0 with no
warning, never obstruct the session), fast (<50 ms typical).

### Component 3: hook wiring

Committed `.claude/settings.json` (so every chat in this repo gets it):

| Hook event         | Action                                             |
|--------------------|----------------------------------------------------|
| `SessionStart`     | `session_guard.py --event write` — register + warn |
| `UserPromptSubmit` | `session_guard.py --event write` — refresh + warn  |
| `Stop`             | `session_guard.py --event clear` — deregister      |
| `SessionEnd`       | `session_guard.py --event clear` — deregister      |

Hooks invoke Python explicitly (`python .claude/hooks/session_guard.py ...`) for
Windows compatibility.

### Component 4: CLAUDE.md rule

A new `CLAUDE.md` (or a section if one is later added) with a "Concurrent
sessions" rule, roughly:

> This repo is often open in several Claude chats at once. If the session guard
> warns that another session is live in this same folder, **stop before editing**:
> move to a fresh git worktree (e.g. via the worktree tooling under
> `.claude/worktrees/`) or confirm with the user. Prefer working in a dedicated
> worktree for any real editing rather than the shared main folder.

## Warning copy

On collision, the injected message reads approximately:

```
⚠️  CONCURRENT SESSION DETECTED
Another Claude chat is live in this exact folder RIGHT NOW:
  <cwd>
  other session: <session_id_short>, last active <N>s ago
Editing here will make your two chats fight over the same files.
→ Move this work to its own git worktree before editing.
```

## Error handling

- Any exception in the guard → exit 0, emit nothing. The guard must never break a
  session or block a legitimate edit.
- Missing/malformed heartbeat files are skipped silently.
- Stale heartbeats (> 15 min) are ignored and deleted when encountered.

## Testing

- **Unit:** liveness threshold (fresh vs stale), same-cwd vs different-cwd keying,
  self-exclusion (a session never warns about itself), malformed-file tolerance.
- **Integration:** simulate two heartbeats in one cwd dir → `--event write` prints
  a warning; one heartbeat → no warning; stale sibling → no warning.
- **Manual:** open two chats in the main folder, confirm the second warns; open a
  chat in a worktree, confirm no warning.

## Out of scope

- Blocking edits (PreToolUse gate) — explicitly rejected; warn-and-allow only.
- Auto-creating worktrees — the agent/user does that after being warned.
- Cross-machine coordination via OneDrive — deliberately avoided.
