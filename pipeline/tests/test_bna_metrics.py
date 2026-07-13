from bna_metrics import build_bna_scores, build_bna_finding


def _raw():
    return {
        "city": {"id": "chi", "name": "Chicago", "state": "Illinois"},
        "history": [
            {"id": "r24", "score": 9, "version": "24.01",
             "created_at": "2024-03-08T13:51:00Z"},
            {"id": "r26", "score": 11.08, "version": "26.05",
             "created_at": "2026-05-08T21:53:50.740620Z"},
        ],
        "latest": {
            "id": "r26", "score": 11.08, "version": "26.05",
            "infrastructure": {"low_stress_miles": 1834.3,
                               "high_stress_miles": 6267.2},
            "people": {"people": 5.28},
            "opportunity": {"employment": 3.75, "score": 7.67},
            "core_services": {"grocery": 8.86, "score": 6.29},
            "recreation": {"parks": 17.52, "score": 9.41},
            "retail": {"retail": 32.55},
            "transit": {"transit": 6.47},
        },
        "cities_index": [
            {"id": "chi", "name": "Chicago", "score": 11.08, "population": 2746349},
            {"id": "nyc", "name": "New York", "score": 40.0, "population": 8000000},
            {"id": "mpls", "name": "Minneapolis", "score": 70.0, "population": 430000},
            {"id": "lz", "name": "Lake Zurich", "score": 20.9, "population": 19759},
        ],
    }


def test_scores_shape_and_values():
    out = build_bna_scores(_raw())
    assert out["data_tier"] == "crowdsourced"
    assert out["score"] == 11.08
    assert out["version"] == "26.05"
    assert out["as_of"] == "2026-05-08"
    assert out["low_stress_miles"] == 1834.3
    assert out["high_stress_miles"] == 6267.2
    # subscores flattened: category -> 0-100 number, including the
    # single-key categories (people/retail/transit) that have no "score" field
    assert out["subscores"]["people"] == 5.28
    assert out["subscores"]["retail"] == 32.55
    assert out["subscores"]["opportunity"] == 7.67
    # history ascending by date, simplified entries
    assert [h["version"] for h in out["history"]] == ["24.01", "26.05"]
    assert out["history"][0] == {"version": "24.01", "score": 9, "as_of": "2024-03-08"}


def test_scores_context_mean_and_large_city_rank():
    out = build_bna_scores(_raw())
    ctx = out["context"]
    # mean over ALL rated cities, one decimal: (11.08+40+70+20.9)/4 = 35.495
    assert ctx["mean_score"] == 35.5
    assert ctx["cities_rated"] == 4
    # large = population >= 300k: NYC(40), Mpls(70), Chicago(11.08) -> Chicago rank 3 of 3
    assert ctx["large_city_count"] == 3
    assert ctx["large_city_rank"] == 3
    # OSM-currency disclosure travels with the data file itself
    assert "OpenStreetMap" in out["note"]


def test_finding_required_copy_elements():
    scores = build_bna_scores(_raw())
    f = build_bna_finding(scores)
    assert f["id"] == "bna-score"
    assert f["data_tier"] == "crowdsourced"
    assert f["stat"] == "11/100"
    # context on the average (verdict B1 change #2)
    assert "36" in f["description"] or "35.5" in f["description"]
    # reconciliation vs our own crash data (verdict B1 change #1):
    # the card must say the score measures the network, not crashes
    assert "crash" in f["description"].lower()
    assert "network" in f["description"].lower()
    # trend appears (9 -> 11)
    assert "9" in f["description"]
    # anti-discouragement + OSM currency live in the caveat (verdict B1 change #3)
    assert "not a reason not to ride" in f["caveat"]
    assert "OpenStreetMap" in f["caveat"]
    assert "May 2026" in f["caveat"]
    # deep-link goes to the map, never a per-ward ranking surface
    assert f["map_state"]["screen"] == "map"


def test_finding_handles_single_run_history():
    raw = _raw()
    raw["history"] = raw["history"][-1:]
    f = build_bna_finding(build_bna_scores(raw))
    # no trend sentence when there's only one analysis year — must not crash
    assert f["stat"] == "11/100"


def test_finding_trend_ignores_incomparable_old_methodology_scores():
    # Real history reaches back to 2017 across PFB methodology changes
    # (33 in 2017 -> 5 in 2020 -> 11 now). The trend sentence must only
    # compare within the last few analyses, never against the old-method era.
    raw = _raw()
    raw["history"] = [
        {"id": "r17", "score": 33, "version": "17.1",
         "created_at": "2017-05-02T00:00:00Z"},
        {"id": "r20", "score": 5, "version": "20.1",
         "created_at": "2020-06-01T00:00:00Z"},
    ] + raw["history"]
    f = build_bna_finding(build_bna_scores(raw))
    assert "33" not in f["description"]
    assert "2017" not in f["description"]
    assert "2024" in f["description"]  # comparable-window anchor: 9 in 2024
    # and the data file's note warns chart-builders about comparability
    scores = build_bna_scores(raw)
    assert "not comparable" in scores["note"]


def test_finding_states_last_place_when_rank_equals_count():
    f = build_bna_finding(build_bna_scores(_raw()))
    # fixture: 3 large cities, Chicago scores lowest -> rank 3 of 3
    assert "last" in f["description"]
    assert "3" in f["description"]
