#!/usr/bin/env python3
"""Tests for git_tidy's pure helpers. Run: python .claude/tools/test_git_tidy.py

Only the side-effect-free logic is tested here — the parsers and the
safety classifiers that decide whether a worktree/branch may be removed.
The git/filesystem wrappers are thin and exercised by the tool's own
dry-run against the live repo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import git_tidy as gt  # noqa: E402


def test_parse_worktrees_marks_main_and_branch():
    porc = (
        "worktree /repo\nHEAD aaa\nbranch refs/heads/main\n\n"
        "worktree /repo/.claude/worktrees/feat\nHEAD bbb\nbranch refs/heads/claude/feat\n\n"
    )
    recs = gt.parse_worktrees(porc)
    assert len(recs) == 2
    assert recs[0]["main"] is True and recs[0]["branch"] == "main"
    assert recs[1]["main"] is False and recs[1]["branch"] == "claude/feat"
    assert recs[1]["head"] == "bbb"


def test_parse_worktrees_detached():
    recs = gt.parse_worktrees("worktree /repo/wt\nHEAD ccc\ndetached\n\n")
    assert recs[0]["detached"] is True and recs[0]["branch"] is None


def test_classify_dirty_clean():
    state, details = gt.classify_dirty("")
    assert state == "clean" and details == []


def test_classify_dirty_allowlisted_untracked_is_clean():
    # a lone untracked launch.json is regenerable -> not a blocker
    state, _ = gt.classify_dirty("?? .claude/launch.json\n")
    assert state == "clean"


def test_classify_dirty_stray_untracked_blocks():
    state, details = gt.classify_dirty("?? life-os/\n?? notes.txt\n")
    assert state == "untracked" and "life-os/" in details


def test_classify_dirty_tracked_change_is_dirty():
    # real work (modified tracked file) always blocks removal
    state, details = gt.classify_dirty(" M site/app.js\n?? .claude/launch.json\n")
    assert state == "dirty" and details == ["site/app.js"]


def test_parse_prune_dryrun_extracts_names():
    text = (
        "Removing worktrees/ghost-a: gitdir file does not exist\n"
        "Removing worktrees/ghost-b: gitdir file does not exist\n"
    )
    assert gt.parse_prune_dryrun(text) == ["ghost-a", "ghost-b"]


def test_heartbeat_live_window():
    now = 1000.0
    assert gt.heartbeat_live({"last_seen": now - 10}, now, 900) is True
    assert gt.heartbeat_live({"last_seen": now - 1000}, now, 900) is False
    assert gt.heartbeat_live({}, now, 900) is False  # missing == ancient


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
