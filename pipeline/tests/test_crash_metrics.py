from crash_metrics import (monthly_counts, per_ward_monthly, window_counts,
                           hit_and_run_shares, protected_share, build_findings_core)


def _t(date, severity="none", hit_and_run=False, dooring=False, ward="1"):
    return {"date": date, "severity": severity, "hit_and_run": hit_and_run,
            "dooring": dooring, "ward": ward}


# 9 crashes across 4 months (2026-01 .. 2026-04, with an empty 2026-03),
# mixed severities and flags.
TUPLES = [
    _t("2026-01-05", "fatal", hit_and_run=True),
    _t("2026-01-15", "incapacitating"),
    _t("2026-01-25", "none", dooring=True),
    _t("2026-02-01", "non_incapacitating", hit_and_run=True, ward="2"),
    _t("2026-02-11", "none", ward="2"),
    _t("2026-02-21", "reported_not_evident"),
    _t("2026-04-02", "incapacitating", hit_and_run=True, ward=None),
    _t("2026-04-12", "none"),
    _t("2026-04-22", "fatal", dooring=True, ward="2"),
]


def test_monthly_counts_are_contiguous_with_zero_months():
    months = monthly_counts(TUPLES, "2026-01", "2026-04")
    assert [m["month"] for m in months] == ["2026-01", "2026-02", "2026-03", "2026-04"]
    m3 = months[2]
    assert m3 == {"month": "2026-03", "crashes": 0, "injury_crashes": 0, "ksi": 0, "fatal": 0}
    assert months[0]["crashes"] == 3


def test_ksi_counts_fatal_and_incapacitating_only():
    months = monthly_counts(TUPLES, "2026-01", "2026-04")
    jan = months[0]
    assert jan["ksi"] == 2                # fatal + incapacitating
    assert jan["fatal"] == 1
    assert jan["injury_crashes"] == 2     # non_incapacitating counts too, none in Jan
    feb = months[1]
    assert feb["ksi"] == 0
    assert feb["injury_crashes"] == 1     # the non_incapacitating crash


def test_per_ward_monthly_groups_located_crashes():
    by_ward = per_ward_monthly(TUPLES, "2026-01", "2026-04")
    assert set(by_ward) == {"1", "2"}     # ward None dropped
    assert sum(m["crashes"] for m in by_ward["1"]) == 5
    assert sum(m["crashes"] for m in by_ward["2"]) == 3
    assert [m["month"] for m in by_ward["2"]] == ["2026-01", "2026-02", "2026-03", "2026-04"]


def test_window_counts_uses_365_day_windows_anchored_at_anchor():
    tuples = [
        _t("2026-04-22", "fatal"),          # anchor day (recent)
        _t("2025-06-01", "incapacitating"),  # within recent 365 days
        _t("2025-04-22", "none"),            # exactly anchor-365 -> prior window (matches crash_trend's > boundary)
        _t("2024-06-01", "fatal"),           # prior window
        _t("2023-01-01", "none"),            # before prior window -> dropped
    ]
    out = window_counts(tuples, "2026-04-22")
    assert out["window_end"] == "2026-04-22"
    assert out["recent_12mo"]["crashes"] == 2
    assert out["recent_12mo"]["ksi"] == 2
    assert out["recent_12mo"]["fatal"] == 1
    assert out["prior_12mo"]["crashes"] == 2
    assert out["prior_12mo"]["fatal"] == 1


def test_hit_and_run_shares_round_to_one_decimal():
    out = hit_and_run_shares(TUPLES)
    assert out["total"] == 9
    assert out["hit_and_run"] == 3
    assert out["share_pct"] == 33.3
    assert out["injury_total"] == 5       # fatal x2, incapacitating x2, non_incapacitating x1
    assert out["injury_hit_and_run"] == 3
    assert out["injury_share_pct"] == 60.0


def test_protected_share_excludes_trail_from_numerator_and_denominator():
    # Off-street trails live in the separate OSM crowdsourced layer and must never
    # enter real-tier statistics: the share is over ON-STREET bikeway miles only.
    ps = protected_share({"protected": 68.74, "buffered": 65.0,
                          "painted": 200.0, "trail": 112.17})
    assert ps["total_mi"] == 333.74       # trail's 112.17 mi not in the denominator
    assert ps["protected_mi"] == 68.74
    assert ps["buffered_mi"] == 65.0
    assert ps["protected_pct"] == 20.6
    assert ps["protected_plus_buffered_pct"] == 40.1


def test_build_findings_core_ids_and_order():
    corridors = [
        {"street": "MILWAUKEE AVE", "crashes_per_km": 12.0},
        {"street": "KINZIE ST", "crashes_per_km": 10.0},
        {"street": "NOWHERE ST", "crashes_per_km": None},
    ]
    ward_counts = {"1": 50, "2": 30, "3": 10, "4": 5, "5": 3, "6": 2}
    by_cat = {"protected": 10.0, "painted": 30.0, "trail": 99.0}
    road_coverage = {"road_miles": 2000.0, "onstreet_bikeway_miles": 240.0,
                     "pct_with_bike_infra": 12.0}
    findings = build_findings_core(TUPLES, by_cat, corridors, ward_counts, "2026-07-12",
                                   road_coverage=road_coverage)
    assert [f["id"] for f in findings] == [
        "ksi-trend", "protected-share", "street-coverage", "top-corridors",
        "hit-and-run", "ward-concentration", "dooring-undercount"]
    by_id = {f["id"]: f for f in findings}
    assert by_id["dooring-undercount"]["title"] == "Dooring: structurally undercounted"
    assert by_id["dooring-undercount"]["stat"] == "2+"
    assert by_id["ward-concentration"]["wards"] == ["1", "2", "3", "4", "5"]
    assert "since Sept 2017" in by_id["ward-concentration"]["description"]
    assert "on-street bikeway miles" in by_id["protected-share"]["description"]
    assert "Kinzie" in by_id["top-corridors"]["caveat"]
    assert by_id["street-coverage"]["stat"] == "12%"
    assert all(f["data_tier"] == "real" for f in findings)


def test_build_findings_core_omits_street_coverage_without_road_data():
    corridors = [{"street": "MILWAUKEE AVE", "crashes_per_km": 12.0}]
    ward_counts = {"1": 50, "2": 30, "3": 10, "4": 5, "5": 3}
    by_cat = {"protected": 10.0, "painted": 30.0, "trail": 99.0}
    findings = build_findings_core(TUPLES, by_cat, corridors, ward_counts, "2026-07-12",
                                   road_coverage=None)
    assert "street-coverage" not in [f["id"] for f in findings]
