import run_all


def _flat(stages):
    return [s[0] for s in stages]


def test_councilmatic_runs_after_council_records():
    live = _flat(run_all.LIVE_STAGES)
    assert "pull_councilmatic.py" in live
    assert live.index("pull_councilmatic.py") > live.index("pull_council_records.py")


def test_councilmatic_pulls_before_classify():
    # classify is a COMMON stage (runs after all LIVE stages), so ordering holds.
    assert "classify_safety_topic.py" in [s[0] for s in run_all.COMMON_STAGES]
