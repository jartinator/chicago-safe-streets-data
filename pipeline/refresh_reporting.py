"""Offline refresh of the committed reporting data — no live pull required.

Recomputes findings.json, citywide_trend.json, and the windows/monthly fields in
ward_safety_index.json from data ALREADY COMMITTED under site/data/ (the last
socrata pull), using the exact same crash_metrics functions as aggregate.py, so
the published numbers can ship without a multi-hour live run and without logic
drift. The weekly `python run_all.py` remains the canonical path.

Provenance guard: refuses to run when meta.json's provenance is not "socrata" —
fixture/synthetic data must never be re-stamped as reporting truth (see the
provenance-stamp history: fix "make live pipeline authoritative about provenance").

What it deliberately does NOT recompute: per-ward danger scores, geometry-derived
mileage, corridors, or ward crash counts — those need population/geometry/raw
inputs this script doesn't have. Corridors and ward counts are read from the
committed files as-is; protected-share miles come from the latest entry of the
committed bikeway_mileage_series.json (same centerline methodology as the live path).

Usage: python refresh_reporting.py
"""
import argparse
import json

from config import SITE_DATA_DIR, CONTRACT_VERSION, CRASH_START_DATE
from crash_metrics import (monthly_counts, per_ward_monthly, window_counts,
                           build_findings_core)
from socrata import write_json


def guard_provenance(meta):
    """Exit rather than re-stamp non-socrata (e.g. fixtures) data as reporting truth."""
    provenance = meta.get("provenance")
    if provenance != "socrata":
        raise SystemExit(
            f"refresh_reporting: site/data/meta.json provenance is {provenance!r}, not "
            "'socrata' — refusing to recompute reporting files from non-live data. "
            "Run `python run_all.py` (live) first.")


def tuples_from_geojson(gj):
    """crashes_cyclist.geojson features -> crash tuples.

    The geojson carries the RENAMED published keys (date, injury_severity,
    hit_and_run, dooring, ward), not the raw Socrata ones aggregate.py reads.
    """
    tuples = []
    for f in gj.get("features", []):
        p = f.get("properties") or {}
        d = (p.get("date") or "")[:10]
        if not d:
            continue
        tuples.append({
            "date": d,
            "severity": p.get("injury_severity"),
            "hit_and_run": bool(p.get("hit_and_run")),
            "dooring": bool(p.get("dooring")),
            "ward": p.get("ward"),
        })
    return tuples


def _load(name):
    return json.loads((SITE_DATA_DIR / name).read_text())


def main():
    argparse.ArgumentParser(
        description="Recompute committed reporting JSON from the last socrata pull."
    ).parse_args()

    meta = _load("meta.json")
    guard_provenance(meta)

    tuples = tuples_from_geojson(_load("crashes_cyclist.geojson"))
    if not tuples:
        raise SystemExit("refresh_reporting: no crash tuples in crashes_cyclist.geojson")

    # Protected share: latest committed mileage snapshot (CDOT centerline methodology,
    # same as the live path); the trail exclusion happens inside protected_share.
    series = _load("bikeway_mileage_series.json")["series"]
    if not series:
        raise SystemExit("refresh_reporting: bikeway_mileage_series.json has no snapshots")
    by_category_miles = series[-1]["by_category"]
    as_of_date = series[-1]["date"]

    corridors = _load("corridors.json")
    ward_counts = {f["properties"]["ward"]: f["properties"]["cyclist_crashes"]
                   for f in _load("wards.geojson")["features"]}

    old_ids = [f["id"] for f in _load("findings.json")]
    findings = build_findings_core(tuples, by_category_miles, corridors, ward_counts,
                                   as_of_date)
    write_json(SITE_DATA_DIR / "findings.json", findings)

    # Citywide monthly trend — identical assembly to aggregate.main().
    anchor = max(t["date"] for t in tuples)
    months = monthly_counts(tuples, CRASH_START_DATE[:7], anchor[:7])
    citywide_trend = {
        "data_tier": "real",
        "window_end": anchor,
        "note": ("Monthly counts of police-reported cyclist crashes citywide since Sept 2017; "
                 "ksi = crashes whose worst injury was fatal or incapacitating (\"killed or "
                 "seriously injured\"). Recent months are provisional — records get amended."),
        "months": months,
    }
    write_json(SITE_DATA_DIR / "citywide_trend.json", citywide_trend)

    # Merge windows/monthly into the existing ward records in place — danger scores,
    # trends, and mileage need inputs this script doesn't have and are left untouched.
    wsi = _load("ward_safety_index.json")
    start_month, end_month = CRASH_START_DATE[:7], anchor[:7]
    ward_monthly = per_ward_monthly(tuples, start_month, end_month)
    tuples_by_ward = {}
    for t in tuples:
        if t["ward"]:
            tuples_by_ward.setdefault(t["ward"], []).append(t)
    for rec in wsi["wards"]:
        w = rec["ward"]
        rec["windows"] = window_counts(tuples_by_ward.get(w, []), anchor)
        rec["monthly"] = ward_monthly.get(w) or monthly_counts([], start_month, end_month)
    write_json(SITE_DATA_DIR / "ward_safety_index.json", wsi)

    # meta.json: stamp the (possibly newer) contract version and register the new
    # citywide_trend source if this meta predates it. generated_at stays — it
    # describes the underlying pull, which this script does not redo.
    meta["contract_version"] = CONTRACT_VERSION
    if not any(s.get("id") == "citywide_trend" for s in meta.get("sources", [])):
        entry = {"id": "citywide_trend", "name": "Citywide Crash Trend (monthly counts)",
                 "tier": "real", "records": len(months),
                 "date_range": [CRASH_START_DATE, anchor]}
        ids = [s.get("id") for s in meta["sources"]]
        pos = ids.index("ward_safety_index") if "ward_safety_index" in ids else len(ids)
        meta["sources"].insert(pos, entry)  # same position as aggregate.py's list
    write_json(SITE_DATA_DIR / "meta.json", meta)

    print(f"refresh_reporting: {len(tuples)} crash tuples through {anchor}")
    print(f"  findings: {old_ids} -> {[f['id'] for f in findings]}")
    print(f"  citywide_trend: {len(months)} months; ward_safety_index: "
          f"{len(wsi['wards'])} wards got windows+monthly; "
          f"contract_version={CONTRACT_VERSION}")


if __name__ == "__main__":
    main()
