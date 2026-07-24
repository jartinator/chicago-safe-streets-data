import json
from pathlib import Path

from commitments_metrics import build_commitments_finding

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


def test_finding_caveat_states_no_delivery_measurement():
    commitments, series = _load_committed_fixtures()
    finding = build_commitments_finding(commitments, series)

    caveat = finding["caveat"].lower()
    assert "install-date" in caveat or "install date" in caveat
    assert "cannot measure" in caveat or "not measurable" in caveat


def test_returns_none_on_empty_roster_or_series():
    assert build_commitments_finding({"commitments": []}, {"series": [{"total": 1, "date": "x", "by_category": {}}]}) is None
    assert build_commitments_finding({"commitments": [{"id": "x", "number": 1, "unit": "miles", "year_committed": 2023, "source_name": "s"}]}, {"series": []}) is None
    assert build_commitments_finding(None, None) is None
