"""Unit coverage for check_colocation.py — Check 5, the caveat co-location
contract.

Drives check_colocation() directly with synthetic {rel_path: data} trees, the
same shape _check_schema_conformance() returns. That keeps each case to the one
rule it exercises, rather than standing up a schema-valid tree per assertion;
test_check_api.py already covers the wired-together path against the real tree.

The cases that matter most here are the ones where the checker must NOT fire.
A CI check that turns a legitimate data condition into a blocked PR gets
switched off, and a switched-off check protects nothing — so the per-glob rule,
the {"available": false} skip and the partial-tree skip each get a test proving
they stay quiet.
"""
import pytest

import caveats
from check_colocation import check_colocation


def _ward(window_end="2026-07-20", recent=66, prior=61, **overrides):
    """A ward payload migrated exactly as emit_api._qualify_safety() emits it."""
    safety = {
        "ward": "40",
        "comparable_danger_score": 96.0,
        "comparable_danger_score_caveat_tags": ["relative_rank"],
        "comparable_danger_score_caveat": caveats.rank_caveat(
            "relative concern rank among wards, higher = worse"),
        "monthly": [
            {"month": "2026-05", "crashes": 5},
            {"month": "2026-06", "crashes": 6, "caveat_tags": ["provisional"]},
            {"month": "2026-07", "crashes": 7, "caveat_tags": ["provisional"]},
        ],
        "monthly_caveat_tags": ["provisional", "not_ridership_normalized"],
        "monthly_caveat": caveats.monthly_caveat(window_end),
        "windows": {
            "window_end": window_end,
            "recent_12mo": caveats.qualify(
                {"crashes": recent, "injury_crashes": 35, "ksi": 5, "fatal": 0},
                "real", ["provisional", "not_ridership_normalized"],
                caveats.window_caveat(window_end, provisional=True)),
            "prior_12mo": caveats.qualify(
                {"crashes": prior, "injury_crashes": 37, "ksi": 7, "fatal": 0},
                "real", ["not_ridership_normalized"],
                caveats.window_caveat(window_end, provisional=False)),
        },
        "crash_trend": caveats.qualify(
            {"direction": "worsening", "window_end": window_end,
             "recent_12mo": recent, "prior_12mo": prior, "pct_change": 8.2},
            "derived", ["provisional", "not_ridership_normalized"],
            caveats.trend_caveat(window_end, recent, prior)),
    }
    safety.update(overrides)
    return {
        "_meta": {"caveat_contract": caveats.CAVEAT_CONTRACT_VERSION,
                 "agent_instruction": caveats.AGENT_INSTRUCTION,
                 "data_tier": "mixed"},
        "ward": "40",
        "safety": safety,
    }


def _tree(n=2, **kw):
    return {f"wards/ward-{i:02d}.json": _ward(**kw) for i in range(1, n + 1)}


# --- the happy path -----------------------------------------------------------

def test_migrated_ward_files_satisfy_the_contract(capsys):
    check_colocation(_tree(3))
    out = capsys.readouterr().out
    assert "OK:" in out
    assert "15 enforced claim(s)" in out       # 3 files x 5 selectors


# --- regressions the check exists to catch ------------------------------------

def test_stripped_caveat_is_caught():
    tree = _tree(2)
    del tree["wards/ward-01.json"]["safety"]["windows"]["recent_12mo"]["caveat"]
    with pytest.raises(SystemExit) as e:
        check_colocation(tree)
    assert "recent_12mo" in str(e.value)


def test_missing_envelope_declaration_is_caught():
    tree = _tree(2)
    del tree["wards/ward-01.json"]["_meta"]["agent_instruction"]
    with pytest.raises(SystemExit) as e:
        check_colocation(tree)
    assert "agent_instruction" in str(e.value)


def test_unknown_caveat_tag_is_caught():
    tree = _tree(2)
    tree["wards/ward-01.json"]["safety"]["crash_trend"]["caveat_tags"] = ["made_up"]
    with pytest.raises(SystemExit) as e:
        check_colocation(tree)
    assert "made_up" in str(e.value)


def test_false_restatement_is_caught_in_committed_json():
    """CC-8 in CI, not only at emit time.

    Hand-edited JSON never runs through qualify(), so the emit-time assert
    cannot see it. This is the check that would have caught the shipped
    "(116 crashes)" beside a sibling key reading 117.
    """
    tree = _tree(2)
    trend = tree["wards/ward-01.json"]["safety"]["crash_trend"]
    trend["caveat"] = caveats.trend_caveat("2026-07-20", 116, 123)
    with pytest.raises(SystemExit) as e:
        check_colocation(tree)
    assert "116" in str(e.value) or "restat" in str(e.value).lower()


def test_field_claim_needs_its_own_pair_not_an_enclosing_block():
    """CC-2. A block stapled onto `safety` must not satisfy `safety#monthly`.

    A field selector exists precisely because that number needs its OWN
    qualifier — if the enclosing block genuinely covered it, the selector would
    be an object selector instead.
    """
    tree = _tree(2)
    safety = tree["wards/ward-01.json"]["safety"]
    del safety["monthly_caveat"]
    del safety["monthly_caveat_tags"]
    safety["data_tier"] = "derived"
    safety["caveat_tags"] = ["provisional"]
    safety["caveat"] = "Everything in this object is provisional through 2026-07-20."
    with pytest.raises(SystemExit) as e:
        check_colocation(tree)
    assert "monthly" in str(e.value)


def test_claim_gone_from_every_file_under_the_glob_is_fatal():
    tree = _tree(3)
    for doc in tree.values():
        del doc["safety"]["crash_trend"]
    with pytest.raises(SystemExit) as e:
        check_colocation(tree)
    assert "crash_trend" in str(e.value)
    assert "regressed" in str(e.value)


# --- the cases where the check MUST stay quiet --------------------------------

def test_claim_absent_from_one_file_only_is_not_fatal(capsys):
    """A refresh emitting one ward without crash_trend is a data condition, not
    a regression. The per-file version of this rule blocked the Monday PR."""
    tree = _tree(3)
    del tree["wards/ward-01.json"]["safety"]["crash_trend"]

    check_colocation(tree)                      # must not raise
    out = capsys.readouterr().out
    assert "NOTE:" in out
    assert "crash_trend" in out
    assert "Not a failure" in out


def test_unmatched_glob_is_not_fatal_and_says_so(capsys):
    """A tree with no ward files at all — check_api.py already tolerates a
    wholly absent api/v1, so a partial tree is anticipated, not broken. It is
    still reported: enforcement that goes quiet without saying so is
    indistinguishable from enforcement that passed."""
    check_colocation({"citywide.json": {"_meta": {}, "findings": []}})
    out = capsys.readouterr().out
    assert "NOTE:" in out
    assert "no file matches" in out
    assert "wards/ward-*.json" in out


def test_available_false_subtree_is_skipped(capsys):
    """"This data is missing" is a stated condition, and a missing number needs
    no caveat. The repo's own rule is never to invent zeros."""
    tree = _tree(2)
    tree["wards/ward-01.json"]["safety"]["windows"] = {"available": False}
    tree["wards/ward-01.json"]["safety"]["crash_trend"] = {"available": False}

    check_colocation(tree)                      # must not raise
    assert "OK:" in capsys.readouterr().out


def test_audit_mode_never_exits_nonzero(capsys):
    """The backlog report is safe to run anywhere, including against a tree
    that would fail enforcement."""
    tree = _tree(2)
    del tree["wards/ward-01.json"]["safety"]["windows"]["recent_12mo"]["caveat"]

    check_colocation(tree, audit_only=True)     # must not raise
    out = capsys.readouterr().out
    assert "AUDIT:" in out


def test_audit_backlog_deduplicates_across_files_and_indices(capsys):
    """50 ward files with the same gap are one line, not fifty. An unreadable
    backlog is an ignored backlog."""
    tree = _tree(20, **{"sr311": {"total": 12, "by_type": {"Bicycle": 12}}})
    check_colocation(tree, audit_only=True)
    out = capsys.readouterr().out
    sr311_lines = [ln for ln in out.splitlines() if "sr311" in ln]
    assert len(sr311_lines) <= 2, f"backlog not deduplicated:\n{out}"
    assert any("20 file(s)" in ln for ln in sr311_lines)
