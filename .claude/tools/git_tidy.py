#!/usr/bin/env python3
"""git-tidy: safe, on-demand local git housekeeping for this repo.

Why this exists: the remote side is handled automatically now (GitHub's
"delete branch on merge" is on), but the *local* checkout still accretes
three kinds of cruft that no remote setting touches —

  1. ghost worktree admin dirs — `.git/worktrees/<n>` whose working tree is
     already gone. `git worktree prune` can't delete them in this repo (it
     holds a handle open while unlinking and OneDrive locks the file), so a
     plain rm does the job instead.
  2. stale worktrees — a merged/idle worktree checkout still sitting under
     `.claude/worktrees/`.
  3. merged local branches — refs whose work is already in origin/main.

This repo is routinely open in several Claude chats at once (see CLAUDE.md),
so removing a worktree another session is live in is exactly the disruption
we must avoid. Every destructive step here is gated on THREE independent
signals and the tool is **dry-run by default** — it prints a plan and does
nothing until you pass --apply.

A worktree is only ever removed when it is ALL of:
  - not the main checkout and not the one this script runs from,
  - idle: no session-guard heartbeat within the live window (reused from
    .claude/hooks/session_guard.py so the key/window can't drift),
  - merged: its HEAD is an ancestor of origin/main,
  - clean: no tracked changes and no untracked files beyond a tiny
    regenerable allowlist (.claude/launch.json).
Anything failing a check is reported and left untouched. Branch deletion
uses `git branch -d` (never -D), which itself refuses unmerged or
checked-out branches, so WIP and live worktrees are double-protected.

Usage:
  python .claude/tools/git_tidy.py                 # dry-run, all three ops
  python .claude/tools/git_tidy.py --apply         # actually do it
  python .claude/tools/git_tidy.py ghosts branches # scope to some ops
  python .claude/tools/git_tidy.py --no-fetch      # skip the origin/main refresh
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# Reuse the session guard's heartbeat contract (store location + cwd hashing
# + live window) rather than re-deriving it — if the guard changes how it
# keys heartbeats, this tool must change with it, so import, don't copy.
_HOOKS = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(_HOOKS))
import session_guard  # noqa: E402

ALLOWED_UNTRACKED = {".claude/launch.json"}  # regenerable; not real work


# ---- pure helpers (no git, no filesystem side effects) — unit-tested ----

def parse_worktrees(porcelain: str):
    """Parse `git worktree list --porcelain` into dicts. The first record is
    always the main checkout (`main=True`). A record is `detached` when it
    has a `detached` line and no `branch`."""
    records, cur = [], {}
    for line in porcelain.splitlines():
        if line == "":
            if cur:
                records.append(cur)
                cur = {}
            continue
        key, _, val = line.partition(" ")
        if key == "worktree":
            cur = {"path": val, "branch": None, "head": None,
                   "detached": False, "bare": False}
        elif key == "HEAD":
            cur["head"] = val
        elif key == "branch":
            cur["branch"] = val.replace("refs/heads/", "", 1)
        elif key == "detached":
            cur["detached"] = True
        elif key == "bare":
            cur["bare"] = True
    if cur:
        records.append(cur)
    for i, r in enumerate(records):
        r["main"] = (i == 0)
    return records


def classify_dirty(porcelain: str, allowed=ALLOWED_UNTRACKED):
    """Classify `git status --porcelain` output for removal safety.
    Returns (state, details): 'dirty' if any tracked change exists (never
    remove — real work), 'untracked' if only untracked files and at least
    one is outside the allowlist, else 'clean'."""
    tracked, stray = [], []
    for line in porcelain.splitlines():
        if not line:
            continue
        code, path = line[:2], line[3:]
        if code == "??":
            if path.rstrip("/") not in allowed:
                stray.append(path)
        else:
            tracked.append(path)
    if tracked:
        return "dirty", tracked
    if stray:
        return "untracked", stray
    return "clean", []


def parse_prune_dryrun(text: str):
    """Names from `git worktree prune -n -v` (writes to stderr). Each line is
    'Removing worktrees/<name>: <reason>'."""
    names = []
    for line in text.splitlines():
        if line.startswith("Removing worktrees/"):
            names.append(line[len("Removing worktrees/"):].split(":", 1)[0])
    return names


def heartbeat_live(data: dict, now: float, window: float) -> bool:
    """True when a heartbeat's last_seen is within the live window."""
    return (now - float(data.get("last_seen", 0))) <= window


# ---- git / filesystem wrappers ----

def git(args, cwd=None, check=False):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def live_sessions(path: str, now: float) -> list:
    """Read-only heartbeat check for a worktree path (does not prune peers'
    files, unlike the guard's own scan)."""
    d = session_guard.session_dir(path)
    if not d.exists():
        return []
    out = []
    for f in d.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if heartbeat_live(data, now, session_guard.LIVE_WINDOW_SEC):
            out.append(str(data.get("session_id", f.stem))[:8])
    return out


def rm_rf_retry(path: Path, tries=3):
    """rm -rf with retries — OneDrive can hold a transient lock right after
    git deregisters a worktree."""
    for i in range(tries):
        if not path.exists():
            return True
        try:
            if path.is_dir():
                import shutil
                shutil.rmtree(path, ignore_errors=(i < tries - 1))
            else:
                path.unlink()
        except OSError:
            pass
        if not path.exists():
            return True
        time.sleep(0.4)
    return not path.exists()


# ---- operations ----

def op_ghosts(repo: Path, apply: bool):
    ghosts = parse_prune_dryrun(git(["worktree", "prune", "-n", "-v"]).stderr)
    print(f"\n[ghosts] {len(ghosts)} dead worktree admin dir(s)")
    for name in ghosts:
        print(f"  - .git/worktrees/{name}")
        if apply:
            ok = rm_rf_retry(repo / ".git" / "worktrees" / name)
            print(f"      {'removed' if ok else 'STILL LOCKED — retry later'}")
    return len(ghosts)


def op_worktrees(repo: Path, apply: bool):
    records = parse_worktrees(git(["worktree", "list", "--porcelain"]).stdout)
    here = str(Path.cwd().resolve()).lower()
    now = time.time()
    removable = 0
    print("\n[worktrees]")
    for r in records:
        if r["main"] or r.get("bare"):
            continue
        p = r["path"]
        name = Path(p).name
        if str(Path(p).resolve()).lower() == here:
            print(f"  keep {name}: this session's worktree")
            continue
        peers = live_sessions(p, now)
        if peers:
            print(f"  keep {name}: LIVE ({', '.join(peers)})")
            continue
        head = r["head"] or ""
        merged = head and git(["merge-base", "--is-ancestor", head, "origin/main"]).returncode == 0
        if not merged:
            print(f"  keep {name}: not merged into origin/main")
            continue
        state, details = classify_dirty(git(["status", "--porcelain"], cwd=p).stdout)
        if state != "clean":
            print(f"  keep {name}: {state} ({', '.join(details[:3])})")
            continue
        removable += 1
        print(f"  DROP {name}: idle + merged + clean")
        if apply:
            git(["worktree", "remove", "--force", p])  # deregisters even if file-delete fails
            ok = rm_rf_retry(Path(p)) and rm_rf_retry(repo / ".git" / "worktrees" / name)
            print(f"      {'removed' if ok else 'deregistered; dir STILL LOCKED — retry later'}")
    if apply:
        git(["worktree", "prune"])
    return removable


def op_branches(repo: Path, apply: bool):
    """Delete local branches merged into origin/main. A branch checked out in
    ANY worktree is excluded (git -d would refuse it anyway) — note this runs
    AFTER op_worktrees, so in --apply a branch freed by an idle-worktree
    removal is no longer checked out and becomes eligible in the same run."""
    cur = git(["branch", "--show-current"]).stdout.strip()
    checked_out = {r["branch"] for r in
                   parse_worktrees(git(["worktree", "list", "--porcelain"]).stdout)
                   if r["branch"]}
    merged = {b.strip().lstrip("*+ ").strip()
              for b in git(["branch", "--merged", "origin/main"]).stdout.splitlines()
              if b.strip()}
    cand = [b for b in merged if b not in ({"main", cur} | checked_out)]
    print("\n[branches] merged local branches (checked-out/unmerged left alone)")
    dropped = 0
    for b in sorted(cand):
        if apply:
            if git(["branch", "-d", b]).returncode == 0:
                dropped += 1
                print(f"  dropped {b}")
            else:
                print(f"  kept {b}: git refused (unmerged or checked out)")
        else:
            print(f"  would drop {b}")
    if not cand:
        print("  (none)")
    return dropped if apply else len(cand)


OPS = {"ghosts": op_ghosts, "worktrees": op_worktrees, "branches": op_branches}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safe local git housekeeping (dry-run by default).")
    ap.add_argument("ops", nargs="*", default=None,
                    help=f"which ops to run (default: all). Choices: {', '.join(OPS)}")
    ap.add_argument("--apply", action="store_true", help="actually delete (default: dry-run)")
    ap.add_argument("--no-fetch", action="store_true", help="skip refreshing origin/main")
    args = ap.parse_args(argv)

    bad = [o for o in (args.ops or []) if o not in OPS]
    if bad:
        ap.error(f"unknown op(s): {', '.join(bad)} (choose from {', '.join(OPS)})")

    repo_top = git(["rev-parse", "--show-toplevel"])
    if repo_top.returncode != 0:
        print("not inside a git repository", file=sys.stderr)
        return 2
    repo = Path(repo_top.stdout.strip())

    if not args.no_fetch:
        git(["fetch", "origin", "main", "-q"])

    ops = args.ops or list(OPS)
    mode = "APPLY" if args.apply else "DRY-RUN (nothing deleted)"
    print(f"git-tidy - {mode} - ops: {', '.join(ops)}")

    total = sum(OPS[name](repo, args.apply) for name in ops)
    if not args.apply:
        print(f"\n{total} item(s) eligible. Re-run with --apply to execute.")
    else:
        print(f"\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
