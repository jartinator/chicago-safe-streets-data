import aggregate


def test_recorded_no_votes_counted_and_nonsponsor_included():
    council_records = [{
        "matter_id": "O2025-1", "title": "t", "type": "ordinance", "status": "Passed",
        "intro_date": "2025-02-01", "url": "u", "topic_relevant": True,
        "sponsors": ["Sponsor, S"],
        "recorded_votes": {"no_voters": ["Dissenter, D"]},
    }]
    result = aggregate.build_aldermen_safety_record(council_records, {})
    by_name = {a["sponsor_name"]: a for a in result["aldermen"]}

    # Sponsor: 1 safety sponsorship, 0 recorded no-votes.
    assert by_name["Sponsor, S"]["safety_sponsorships"] == 1
    assert by_name["Sponsor, S"]["recorded_no_votes"] == 0

    # Dissenter never sponsored but must appear, with the no-vote counted.
    assert by_name["Dissenter, D"]["recorded_no_votes"] == 1
    assert by_name["Dissenter, D"]["safety_sponsorships"] == 0


def test_no_votes_ignored_when_topic_irrelevant():
    council_records = [{
        "matter_id": "O2025-2", "title": "t", "type": "ordinance", "status": "Passed",
        "intro_date": "2025-02-01", "url": "u", "topic_relevant": False,
        "sponsors": [], "recorded_votes": {"no_voters": ["Dissenter, D"]},
    }]
    result = aggregate.build_aldermen_safety_record(council_records, {})
    assert result["aldermen"] == []
