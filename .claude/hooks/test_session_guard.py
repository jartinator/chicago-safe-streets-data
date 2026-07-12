#!/usr/bin/env python3
"""Tests for session_guard. Run: python .claude/hooks/test_session_guard.py"""
import json
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_guard as sg  # noqa: E402


def _fresh_base():
    return Path(tempfile.mkdtemp(prefix="sg-test-"))


def _plant(base, cwd, sid, last_seen):
    d = sg.session_dir(cwd, base)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sid}.json").write_text(
        json.dumps({"session_id": sid, "cwd": str(cwd), "last_seen": last_seen}),
        encoding="utf-8",
    )


def test_self_excluded():
    base, cwd = _fresh_base(), "/repo/a"
    warn = sg.handle_write("me", cwd, "SessionStart", base=base)
    assert warn is None, "a session must not warn about itself"


def test_warns_on_live_peer():
    base, cwd = _fresh_base(), "/repo/a"
    _plant(base, cwd, "other", sg._now())
    warn = sg.handle_write("me", cwd, "SessionStart", base=base)
    assert warn and "CONCURRENT SESSION" in warn, "should warn on a live peer"
    assert "other"[:8] in warn


def test_stale_peer_ignored_and_pruned():
    base, cwd = _fresh_base(), "/repo/a"
    _plant(base, cwd, "ghost", sg._now() - (sg.LIVE_WINDOW_SEC + 60))
    warn = sg.handle_write("me", cwd, "SessionStart", base=base)
    assert warn is None, "stale peer must not trigger a warning"
    assert not (sg.session_dir(cwd, base) / "ghost.json").exists(), "stale file pruned"


def test_different_cwd_no_collision():
    base = _fresh_base()
    _plant(base, "/repo/a", "other", sg._now())
    warn = sg.handle_write("me", "/repo/b", "SessionStart", base=base)
    assert warn is None, "sessions in different folders must not collide"


def test_debounce_on_prompt_submit():
    base, cwd = _fresh_base(), "/repo/a"
    _plant(base, cwd, "other", sg._now())
    first = sg.handle_write("me", cwd, "SessionStart", base=base)
    assert first is not None, "SessionStart warns"
    # same peers on next prompt -> no repeat warning
    second = sg.handle_write("me", cwd, "UserPromptSubmit", base=base)
    assert second is None, "unchanged peer set must not re-warn on prompt"
    # a NEW peer appears -> warn again
    _plant(base, cwd, "newbie", sg._now())
    third = sg.handle_write("me", cwd, "UserPromptSubmit", base=base)
    assert third is not None, "a newly appeared peer should re-warn"


def test_malformed_file_tolerated():
    base, cwd = _fresh_base(), "/repo/a"
    d = sg.session_dir(cwd, base)
    d.mkdir(parents=True, exist_ok=True)
    (d / "broken.json").write_text("{not json", encoding="utf-8")
    warn = sg.handle_write("me", cwd, "SessionStart", base=base)
    assert warn is None, "malformed peer files are skipped, not fatal"


def test_clear_removes_heartbeat():
    base, cwd = _fresh_base(), "/repo/a"
    sg.handle_write("me", cwd, "SessionStart", base=base)
    f = sg.session_dir(cwd, base) / "me.json"
    assert f.exists()
    sg.handle_clear("me", cwd, base=base)
    assert not f.exists(), "clear must remove the heartbeat"


def test_case_insensitive_cwd_key():
    # Windows paths differing only in case must map to the same folder key.
    assert sg.cwd_key("/Repo/A") == sg.cwd_key("/repo/a")


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
    sys.exit(1 if failed else 0)
