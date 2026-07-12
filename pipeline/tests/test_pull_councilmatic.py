import pull_councilmatic as pc


def test_parse_classification_unwraps_json_array():
    assert pc.parse_classification('["ordinance"]') == "ordinance"


def test_parse_classification_handles_empty_and_plain():
    assert pc.parse_classification(None) is None
    assert pc.parse_classification("[]") is None
    assert pc.parse_classification("ordinance") == "ordinance"


def test_councilmatic_url():
    assert pc.councilmatic_url("O2025-0015514") == \
        "https://chicago.councilmatic.org/legislation/O2025-0015514/"


def test_extract_recorded_votes_returns_none_when_unanimous():
    pvs = [{"voter_name": "A", "option": "yes"}, {"voter_name": "B", "option": "yes"}]
    assert pc.extract_recorded_votes({"start_date": "2026-03-18", "result": "pass"}, pvs) is None


def test_extract_recorded_votes_tallies_dissent():
    pvs = [
        {"voter_name": "Yes One", "option": "yes"},
        {"voter_name": "No One", "option": "no"},
        {"voter_name": "Absent One", "option": "absent"},
    ]
    rv = pc.extract_recorded_votes({"start_date": "2026-03-18T00:00:00", "result": "pass"}, pvs)
    assert rv == {
        "date": "2026-03-18",
        "yes": 1, "no": 1, "absent": 1,
        "no_voters": ["No One"],
        "result": "pass",
    }


def test_choose_recorded_votes_picks_most_recent_contested():
    events = [
        {"id": "v1", "start_date": "2025-01-01", "result": "pass"},
        {"id": "v2", "start_date": "2026-01-01", "result": "pass"},
    ]
    pvs = {
        "v1": [{"voter_name": "X", "option": "no"}, {"voter_name": "Y", "option": "yes"}],
        "v2": [{"voter_name": "X", "option": "yes"}, {"voter_name": "Y", "option": "yes"}],
    }
    # v2 is more recent but unanimous; v1 is the most recent contested one.
    rv = pc.choose_recorded_votes(events, pvs)
    assert rv["no_voters"] == ["X"]


def test_group_sponsors_primary_first():
    rows = [
        {"bill_id": "b1", "name": "Second, A", "primary": 0},
        {"bill_id": "b1", "name": "Primary, P", "primary": 1},
        {"bill_id": "b2", "name": "Solo, S", "primary": 1},
    ]
    grouped = pc.group_sponsors(rows)
    assert grouped["b1"] == ["Primary, P", "Second, A"]
    assert grouped["b2"] == ["Solo, S"]


def test_build_record_normalizes_and_omits_votes_when_none():
    bill = {"identifier": "O2025-1", "title": "Bike lane thing",
            "classification": '["ordinance"]', "status": "Passed",
            "intro_date": "2025-02-01T00:00:00"}
    rec = pc.build_record(bill, ["Hopkins, Brian"], None)
    assert rec == {
        "matter_id": "O2025-1",
        "title": "Bike lane thing",
        "type": "ordinance",
        "status": "Passed",
        "intro_date": "2025-02-01T00:00:00",
        "body": None,
        "sponsors": ["Hopkins, Brian"],
        "url": "https://chicago.councilmatic.org/legislation/O2025-1/",
        "source": "councilmatic",
    }


def test_build_record_includes_votes_when_present():
    bill = {"identifier": "O2025-2", "title": "x", "classification": "[]",
            "status": "s", "intro_date": "2025-02-01T00:00:00"}
    rv = {"date": "2025-03-01", "yes": 30, "no": 18, "absent": 2,
          "no_voters": ["No One"], "result": "pass"}
    rec = pc.build_record(bill, [], rv)
    assert rec["recorded_votes"] == rv
    assert rec["type"] is None


def test_max_action_date():
    rows = [{"last_action": "2024-05-01"}, {"last_action": "2026-07-09T00:00:00"}]
    assert pc.max_action_date(rows) == "2026-07-09"
    assert pc.max_action_date([]) is None


def test_bills_sql_contains_keywords_and_frozen_boundary():
    sql = pc.bills_sql(["bike", "vision zero"], "2023-06-21")
    assert "like '%bike%'" in sql
    assert "like '%vision zero%'" in sql
    assert "2023-06-21" in sql


def test_quote_ids():
    assert pc._quote_ids(["ocd-bill/a", "ocd-bill/b"]) == "'ocd-bill/a','ocd-bill/b'"
