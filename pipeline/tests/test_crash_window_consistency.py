"""safety.crash_trend and safety.windows must describe the SAME 12-month window.

Regression tests for the cold-agent probe finding (2026-07-22 build): per-ward
files carried crash_trend anchored at the ward's own latest crash date while
windows was anchored at the global latest crash date, so the two blocks
published disagreeing recent/prior counts for nominally the same window.
"""
import pytest

import aggregate
from crash_metrics import window_counts, check_trend_window_consistency


def _t(date, ward="1"):
    return {"date": date, "severity": "none", "hit_and_run": False,
            "dooring": False, "ward": ward}


# Ward-1 crashes whose latest date (2026-07-16) trails the global anchor
# (2026-07-20) — the exact shape that produced the ward-35 disagreement.
# 2025-07-18 sits between ward-anchor-365 and global-anchor-365, so it flips
# from "recent" to "prior" depending on which anchor is used.
DATES = ["2024-01-10", "2025-07-18", "2025-08-01", "2026-07-16"]
GLOBAL_ANCHOR = "2026-07-20"


def test_crash_trend_uses_explicit_anchor_date():
    out = aggregate.crash_trend(DATES, anchor_date=GLOBAL_ANCHOR)
    assert out["window_end"] == GLOBAL_ANCHOR
    # vs 2026-07-20: recent > 2025-07-20 -> {2025-08-01, 2026-07-16};
    # prior (2024-07-21 .. 2025-07-20] -> {2025-07-18}.
    assert out["recent_12mo"] == 2
    assert out["prior_12mo"] == 1


def test_crash_trend_default_anchor_is_latest_date():
    out = aggregate.crash_trend(DATES)
    assert out["window_end"] == "2026-07-16"


def test_crash_trend_empty_dates_with_anchor_reports_that_anchor():
    out = aggregate.crash_trend([], anchor_date=GLOBAL_ANCHOR)
    assert out["direction"] == "insufficient_data"
    assert out["window_end"] == GLOBAL_ANCHOR


def test_crash_trend_agrees_with_window_counts_on_shared_anchor():
    trend = aggregate.crash_trend(DATES, anchor_date=GLOBAL_ANCHOR)
    windows = window_counts([_t(d) for d in DATES], GLOBAL_ANCHOR)
    assert trend["window_end"] == windows["window_end"]
    assert trend["recent_12mo"] == windows["recent_12mo"]["crashes"]
    assert trend["prior_12mo"] == windows["prior_12mo"]["crashes"]
    check_trend_window_consistency(trend, windows, "ward 1")  # must not raise


def test_consistency_check_raises_on_anchor_mismatch():
    trend = aggregate.crash_trend(DATES)                       # ward anchor
    windows = window_counts([_t(d) for d in DATES], GLOBAL_ANCHOR)
    with pytest.raises(ValueError, match="ward 1"):
        check_trend_window_consistency(trend, windows, "ward 1")


def test_consistency_check_raises_on_count_mismatch():
    trend = dict(aggregate.crash_trend(DATES, anchor_date=GLOBAL_ANCHOR),
                 recent_12mo=99)
    windows = window_counts([_t(d) for d in DATES], GLOBAL_ANCHOR)
    with pytest.raises(ValueError, match="recent_12mo"):
        check_trend_window_consistency(trend, windows, "ward 1")


def test_consistency_check_skips_counts_for_insufficient_data():
    # A ward whose history starts inside the prior window: trend has no counts,
    # but the anchors must still line up.
    short = ["2026-07-01", "2026-07-10"]
    trend = aggregate.crash_trend(short, anchor_date=GLOBAL_ANCHOR)
    assert trend["direction"] == "insufficient_data"
    windows = window_counts([_t(d) for d in short], GLOBAL_ANCHOR)
    check_trend_window_consistency(trend, windows, "ward 1")  # must not raise
