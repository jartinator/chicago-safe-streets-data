#!/usr/bin/env python3
"""Session guard: warn (never block) when another Claude chat is live in this folder.

Each session writes a heartbeat file keyed by working directory. On SessionStart
and UserPromptSubmit we refresh our heartbeat and scan for *other* live sessions
in the same directory; if any exist we print a warning that the harness injects
into the conversation. On Stop/SessionEnd we remove our heartbeat.

Design rules:
- Heartbeats live in the OS temp dir, never inside the (OneDrive-synced) repo.
- Keyed by a hash of the absolute cwd, so different worktrees never collide.
- Fail-open: any error exits 0 with no output. The guard must never obstruct a
  session or block an edit.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

LIVE_WINDOW_SEC = 15 * 60  # a heartbeat older than this is considered dead


def store_root(base=None):
    base = Path(base) if base else Path(tempfile.gettempdir())
    return base / "claude-session-guard"


def cwd_key(cwd):
    resolved = str(Path(cwd).resolve()).lower()  # lower(): Windows paths are case-insensitive
    return hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:16]


def session_dir(cwd, base=None):
    return store_root(base) / cwd_key(cwd)


def _now():
    return time.time()


def scan_peers(session_id, cwd, base=None):
    """Return session_ids of *other* live sessions in this cwd. Prunes stale files."""
    d = session_dir(cwd, base)
    peers = []
    if not d.exists():
        return peers
    for f in d.glob("*.json"):
        if f.stem == session_id:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue  # skip malformed / half-written files
        if _now() - float(data.get("last_seen", 0)) > LIVE_WINDOW_SEC:
            try:
                f.unlink()
            except OSError:
                pass
            continue
        peers.append(str(data.get("session_id", f.stem)))
    return peers


def format_warning(cwd, peers):
    lines = [
        "⚠️  CONCURRENT SESSION DETECTED",
        "Another Claude chat is live in THIS EXACT folder right now:",
        f"  {cwd}",
    ]
    for p in peers:
        lines.append(f"  other session: {p[:8]}")
    lines += [
        "Editing here will make your two chats fight over the same files",
        "(\"someone is working in it RIGHT NOW, all my files are changing\").",
        "→ Move this work to its own git worktree BEFORE editing. See CLAUDE.md.",
    ]
    return "\n".join(lines)


def handle_write(session_id, cwd, event, base=None):
    """Refresh heartbeat; return a warning string if we should warn, else None."""
    d = session_dir(cwd, base)
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{session_id}.json"

    prior = {}
    if f.exists():
        try:
            prior = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            prior = {}

    peers = scan_peers(session_id, cwd, base)
    prior_warned = set(prior.get("last_warned_peers", []))

    # SessionStart always warns on a collision; UserPromptSubmit only re-warns when
    # the set of colliding sessions changes (a new chat appeared) to avoid nagging.
    should_warn = bool(peers) and (event == "SessionStart" or set(peers) != prior_warned)

    data = {
        "session_id": session_id,
        "cwd": str(cwd),
        "pid": os.getpid(),
        "last_seen": _now(),
        "last_warned_peers": list(peers) if should_warn else list(prior_warned),
    }
    try:
        f.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass

    return format_warning(cwd, peers) if should_warn else None


def handle_clear(session_id, cwd, base=None):
    f = session_dir(cwd, base) / f"{session_id}.json"
    try:
        f.unlink()
    except OSError:
        pass


def _emit(text):
    """Write UTF-8 to stdout regardless of console codepage (Windows cp1252 would
    otherwise raise UnicodeEncodeError on the emoji and, under fail-open, silently
    drop the whole warning)."""
    payload = (text + "\n").encode("utf-8", errors="replace")
    try:
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()
    except Exception:
        try:
            sys.stdout.write(text.encode("ascii", "replace").decode("ascii") + "\n")
        except Exception:
            pass


def _read_hook_input():
    """Hooks receive event JSON on stdin: {session_id, cwd, hook_event_name, ...}."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["write", "clear"], required=True)
    args = parser.parse_args()

    payload = _read_hook_input()
    session_id = str(payload.get("session_id") or "unknown")
    cwd = payload.get("cwd") or os.getcwd()
    event = payload.get("hook_event_name") or ""

    if args.event == "clear":
        handle_clear(session_id, cwd)
        return

    warning = handle_write(session_id, cwd, event)
    if warning:
        _emit(warning)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open: never obstruct the session
    sys.exit(0)
