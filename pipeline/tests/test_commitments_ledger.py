import json
from pathlib import Path

import pytest

from commitments_metrics import build_commitments_ledger, score_commitment

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _history():
    p = REPO_ROOT / "data" / "cdot_bikeway_history.json"
    return json.loads(p.read_text()) if p.exists() else None


def _roster():
    return json.loads((REPO_ROOT / "data" / "commitments.json").read_text())


# --- scoring bases -------------------------------------------------------------------

HIST = {"annual": {
    "network": [
        {"year": 2015, "by_category": {"protected": 20.0, "buffered": 80.0, "painted": 10.0,
                                       "greenway": 1.0, "sharrow": 5.0}},
        {"year": 2019, "by_category": {"protected": 25.0, "buffered": 90.0, "painted": 10.0,
                                       "greenway": 2.0, "sharrow": 5.0}},
    ],
    "installed": [
        {"year": 2019, "by_category": {"protected": 3.0, "greenway": 1.0}, "protected_concrete_upgrade": 2.0},
    ],
    "cdot_reported_totals": {"installed_on_street": {"2019": 10.0}},
}}


def test_network_state_scores_the_standing_network_in_the_target_year():
    row = score_commitment({"id": "x", "number": 100, "unit": "miles", "basis": "network_state",
                            "categories": ["protected"], "target_year": 2015}, HIST)
    assert row["measurable"] and row["actual"] == 20.0
    assert row["pct_of_target"] == 20 and row["met"] is False
    assert row["window"] == "as of 2015"


def test_alt_categories_publishes_the_generous_reading_too():
    """Where a claim only works if buffered counts as protected, publish BOTH numbers."""
    row = score_commitment({"id": "x", "number": 100, "unit": "miles", "basis": "network_state",
                            "categories": ["protected"], "target_year": 2015,
                            "alt_categories": ["protected", "buffered"]}, HIST)
    assert row["actual"] == 20.0 and row["met"] is False          # honest reading
    assert row["actual_as_claimed"] == 100.0 and row["as_claimed_met"] is True
    assert row["as_claimed_categories"] == ["protected", "buffered"]


def test_network_delta_measures_change_between_two_years():
    row = score_commitment({"id": "x", "number": 50, "unit": "miles", "basis": "network_delta",
                            "categories": ["protected"], "baseline_year": 2015,
                            "target_year": 2019}, HIST)
    assert row["actual"] == 5.0 and row["window"] == "2015 to 2019"


def test_miles_added_excludes_concrete_upgrades():
    # CDOT reports 10.0 installed for 2019, of which 2.0 is a concrete upgrade to an
    # existing protected lane — no new mileage, so the ledger must not count it.
    row = score_commitment({"id": "x", "number": 100, "unit": "miles", "basis": "miles_added",
                            "categories": None, "baseline_year": 2018, "target_year": 2019}, HIST)
    assert row["actual"] == 8.0


def test_unmeasurable_commitments_get_a_reason_and_never_a_number():
    row = score_commitment({"id": "x", "number": 70, "unit": "percent",
                            "basis": "not_measurable",
                            "not_measurable_reason": "needs a population analysis"}, HIST)
    assert row["measurable"] is False
    assert "population" in row["reason"]
    assert "actual" not in row and "pct_of_target" not in row


def test_missing_year_is_reported_not_guessed():
    row = score_commitment({"id": "x", "number": 10, "unit": "miles", "basis": "network_state",
                            "categories": ["protected"], "target_year": 1999}, HIST)
    assert row["measurable"] is False and "1999" in row["reason"]


# --- the committed ledger ------------------------------------------------------------

@pytest.fixture(scope="module")
def ledger():
    history = _history()
    if history is None:
        pytest.skip("cdot_bikeway_history.json not built")
    return build_commitments_ledger(_roster(), history)


def test_ledger_spans_administrations(ledger):
    """The lens is the network, not who was in office — so the roster must not be
    confined to the current administration's pledges."""
    years = {r["year_committed"] for r in ledger["commitments"]}
    assert min(years) <= 2015 and max(years) >= 2023
    assert len(years) >= 3


def test_ledger_rows_are_sorted_oldest_first(ledger):
    ys = [r["year_committed"] for r in ledger["commitments"]]
    assert ys == sorted(ys)


def test_every_row_carries_its_citation(ledger):
    for r in ledger["commitments"]:
        assert r["citations"], f"{r['id']} has no citation"
        assert r["source_name"]


def test_the_2015_protected_pledge_only_clears_by_counting_buffered(ledger):
    row = next(r for r in ledger["commitments"] if r["id"] == "100-miles-protected-2015")
    assert row["met"] is False
    assert row["actual"] < 25            # protected alone
    assert row["actual_as_claimed"] > 100  # only with buffered folded in
    assert row["as_claimed_met"] is True


def test_a_met_commitment_is_reported_as_met(ledger):
    # Not a hunt for failures: the ledger must report success where it happened.
    row = next(r for r in ledger["commitments"] if r["id"] == "100-new-miles-first-term")
    assert row["met"] is True and row["actual"] > 100


def test_ledger_counts_agree_with_its_rows(ledger):
    scored = [r for r in ledger["commitments"] if r["measurable"]]
    assert ledger["scored"] == len(scored)
    assert ledger["met"] == sum(1 for r in scored if r["met"])
    assert ledger["data_tier"] == "derived"


def test_published_ledger_matches_a_fresh_build(ledger):
    published = REPO_ROOT / "site" / "data" / "commitments_ledger.json"
    if not published.exists():
        pytest.skip("ledger not published in this checkout")
    assert json.loads(published.read_text()) == ledger
