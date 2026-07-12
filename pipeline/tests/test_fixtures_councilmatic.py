import random

import make_fixtures


def test_build_councilmatic_records_shape_and_one_contested():
    out = make_fixtures.build_councilmatic_records(random.Random(0))
    assert out["source"] == "councilmatic"
    assert out["covers_from"] == "2023-06-21"
    assert out["latest_action_date"] > "2023-06-21"
    assert len(out["records"]) >= 1
    assert all(r["source"] == "councilmatic" for r in out["records"])
    # Exactly the seeded contested record carries recorded_votes.
    with_votes = [r for r in out["records"] if "recorded_votes" in r]
    assert len(with_votes) == 1
    assert with_votes[0]["recorded_votes"]["no"] > 0
