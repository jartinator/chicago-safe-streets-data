import pytest

from refresh_reporting import guard_provenance, tuples_from_geojson


def _feat(props):
    return {"type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-87.6, 41.9]},
            "properties": props}


def test_tuples_from_geojson_maps_renamed_keys():
    gj = {"type": "FeatureCollection", "features": [
        _feat({"date": "2026-07-01T10:00:00", "injury_severity": "incapacitating",
               "hit_and_run": True, "dooring": False, "ward": "1"}),
        _feat({"date": "2026-06-15T08:00:00", "injury_severity": "none",
               "hit_and_run": False, "dooring": True, "ward": None}),
    ]}
    tuples = tuples_from_geojson(gj)
    assert tuples[0] == {"date": "2026-07-01", "severity": "incapacitating",
                         "hit_and_run": True, "dooring": False, "ward": "1"}
    assert tuples[1] == {"date": "2026-06-15", "severity": "none",
                         "hit_and_run": False, "dooring": True, "ward": None}


def test_refresh_refuses_non_socrata_provenance():
    # Fixture data must never be re-stamped as reporting truth — see the
    # provenance-stamp history in git (fix: make live pipeline authoritative).
    with pytest.raises(SystemExit):
        guard_provenance({"provenance": "fixtures"})
    with pytest.raises(SystemExit):
        guard_provenance({})
    guard_provenance({"provenance": "socrata"})  # must not raise
