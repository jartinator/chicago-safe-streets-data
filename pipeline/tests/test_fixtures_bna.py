from bna_metrics import build_bna_scores, build_bna_finding
from make_fixtures import build_bna_raw


def test_fixture_bna_flows_through_real_shaping():
    raw = build_bna_raw()
    scores = build_bna_scores(raw)
    assert scores["data_tier"] == "crowdsourced"
    assert 0 <= scores["score"] <= 100
    assert scores["version"]
    assert scores["history"], "fixture must exercise the trend path"
    finding = build_bna_finding(scores)
    assert finding["id"] == "bna-score"
    assert finding["stat"].endswith("/100")
