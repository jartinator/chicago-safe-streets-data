import json
from pathlib import Path

from commitments_metrics import build_commitments_finding, delivered_since

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_committed_fixtures():
    commitments = json.loads((REPO_ROOT / "data" / "commitments.json").read_text())
    series = json.loads((REPO_ROOT / "site" / "data" / "bikeway_mileage_series.json").read_text())
    return commitments, series


def test_commitments_roster_is_non_empty_and_cited():
    commitments, _ = _load_committed_fixtures()
    assert commitments["commitments"]
    for c in commitments["commitments"]:
        assert c["citations"], f"{c['id']} has no citation"


def test_finding_shape_matches_existing_findings_json():
    commitments, series = _load_committed_fixtures()
    finding = build_commitments_finding(commitments, series)

    required_keys = {"id", "title", "stat", "description", "caveat",
                     "data_tier", "map_state"}
    assert required_keys.issubset(finding.keys())
    assert finding["id"] == "commitments-vs-delivered"
    assert finding["data_tier"] == "derived"
    assert isinstance(finding["map_state"], dict)
    assert "screen" in finding["map_state"] and "layers" in finding["map_state"]


def test_finding_references_150_and_current_total():
    commitments, series = _load_committed_fixtures()
    finding = build_commitments_finding(commitments, series)

    assert "150" in finding["stat"] or "150" in finding["description"]
    latest_total = round(series["series"][-1]["total"])
    assert str(latest_total) in finding["description"]


def test_finding_falls_back_honestly_without_the_released_history():
    # Environments without data/cdot_bikeway_history.json (a fixtures run, a fork that
    # hasn't pulled it) must say delivery wasn't measured, never imply it was.
    commitments, series = _load_committed_fixtures()
    finding = build_commitments_finding(commitments, series, history_doc=None)

    caveat = finding["caveat"].lower()
    assert "not against what has been delivered" in caveat
    assert "not available in this environment" in caveat


# --- the delivered ledger (post-FOIA) ------------------------------------------------

def _history():
    path = REPO_ROOT / "data" / "cdot_bikeway_history.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def test_delivered_since_separates_upgrades_from_new_miles():
    history = _history()
    if history is None:
        return
    ledger = delivered_since(history, 2023)
    # CDOT counts concrete upgrades of existing protected lanes toward "miles installed";
    # the pledge says "new", so the two must not be allowed to collapse into one number.
    assert ledger["cdot_counted_miles"] > ledger["new_miles"]
    assert round(ledger["new_miles"] + ledger["concrete_upgrade_miles"], 2) == \
        ledger["cdot_counted_miles"]
    assert ledger["concrete_upgrade_miles"] > 0
    assert ledger["since_year"] == 2023


def test_low_stress_share_is_lower_on_the_new_only_basis():
    history = _history()
    if history is None:
        return
    ledger = delivered_since(history, 2023)
    # Upgrades are protected lanes, so CDOT's basis counts them as low-stress on both
    # sides of the ratio. Removing them lowers the share — if this ever inverts, the
    # two bases have been mixed up somewhere.
    assert ledger["low_stress_share_cdot_basis"] > ledger["low_stress_share_new_basis"]


def test_finding_leads_with_new_miles_and_still_shows_cdots_number():
    commitments, series = _load_committed_fixtures()
    history = _history()
    if history is None:
        return
    finding = build_commitments_finding(commitments, series, history)
    ledger = delivered_since(history, 2023)

    # Headline stat is the new-only figure, not CDOT's larger one.
    assert f"{ledger['new_miles']:,.1f}" in finding["stat"]
    assert "150" in finding["stat"]
    # CDOT's own number and the upgrade gap both appear rather than being suppressed.
    assert f"{ledger['cdot_counted_miles']:,.1f}" in finding["description"]
    assert f"{ledger['concrete_upgrade_miles']:,.1f}" in finding["description"]
    # The buffered-lane definitional divergence is disclosed.
    assert "buffered" in finding["caveat"].lower()


def test_delivered_since_returns_none_without_history():
    assert delivered_since(None, 2023) is None
    assert delivered_since({"annual": {"installed": []}}, 2023) is None


def test_returns_none_on_empty_roster_or_series():
    assert build_commitments_finding({"commitments": []}, {"series": [{"total": 1, "date": "x", "by_category": {}}]}) is None
    assert build_commitments_finding({"commitments": [{"id": "x", "number": 1, "unit": "miles", "year_committed": 2023, "source_name": "s"}]}, {"series": []}) is None
    assert build_commitments_finding(None, None) is None
