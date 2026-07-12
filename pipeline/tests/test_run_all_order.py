import run_all


def _flat(stages):
    return [s[0] for s in stages]


def test_councilmatic_runs_after_council_records():
    # Pre-2023 (frozen) council records are restored from a committed snapshot rather than
    # pulled live; post-2023 Councilmatic must still run after they're in place.
    live = _flat(run_all.LIVE_STAGES)
    assert "pull_councilmatic.py" in live
    assert live.index("pull_councilmatic.py") > live.index("restore_frozen.py")


def test_councilmatic_pulls_before_classify():
    # classify is a COMMON stage (runs after all LIVE stages), so ordering holds.
    assert "classify_safety_topic.py" in [s[0] for s in run_all.COMMON_STAGES]


def test_live_provenance_overwrites_stale_fixtures_marker(tmp_path, monkeypatch):
    # Regression: a live run performed after a prior `--fixtures` run must not
    # inherit the stale "fixtures" marker and mislabel real data as fixtures.
    monkeypatch.setattr(run_all, "RAW_DIR", tmp_path)
    (tmp_path / "PROVENANCE").write_text("fixtures\n")  # left by a prior --fixtures run

    run_all.write_live_provenance()

    assert (tmp_path / "PROVENANCE").read_text().strip() == "socrata"


def test_live_provenance_creates_marker_when_absent(tmp_path, monkeypatch):
    # A fresh live run (no raw dir yet) writes the socrata marker from scratch.
    raw = tmp_path / "raw"
    monkeypatch.setattr(run_all, "RAW_DIR", raw)

    run_all.write_live_provenance()

    assert (raw / "PROVENANCE").read_text().strip() == "socrata"
