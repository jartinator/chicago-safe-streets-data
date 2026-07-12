"""Pull current alderperson names/contacts from the city's Ward Offices dataset.

Writes site/data/aldermen.json directly (this file was previously manual-fill-only).
Fail-soft: on any fetch/validation failure the existing file is left untouched, so a
bad pull can never blank out real names. Non-fatal — never raises the pipeline.
Idempotent: re-running overwrites cleanly.
"""
import argparse
from datetime import datetime, timezone

from config import SITE_DATA_DIR, WARD_OFFICES_DATASET, ALDERMAN_LOOKUP_URL
from socrata import fetch_all, write_json


def _clean(v):
    if isinstance(v, dict):          # Socrata "url" type: {"url": "..."}
        v = v.get("url")
    v = (v or "").strip() if isinstance(v, str) else v
    return v or None


def build_aldermen(rows):
    by_ward = {str(r.get("ward")): r for r in rows if r.get("ward")}
    wards = []
    for i in range(1, 51):
        r = by_ward.get(str(i), {})
        wards.append({
            "ward": str(i),
            "alderman": _clean(r.get("alderman")),
            "email": _clean(r.get("email")),
            "phone": _clean(r.get("ward_phone")),
            "website": _clean(r.get("website")),
        })
    return wards


def roster_is_valid(wards):
    """Guard against a partial/broken pull replacing good data: require names for
    at least 40 of 50 wards (a few vacancies are normal; a majority is a bad pull)."""
    named = sum(1 for w in wards if w["alderman"])
    return named >= 40


def main():
    argparse.ArgumentParser(description="Pull current alderpersons (Ward Offices).").parse_args()
    try:
        rows = list(fetch_all(WARD_OFFICES_DATASET))
    except Exception as e:  # noqa: BLE001 — fail-soft by design, like pull_mellow.py
        print(f"aldermen: pull failed ({e}); keeping existing aldermen.json")
        return
    wards = build_aldermen(rows)
    if not roster_is_valid(wards):
        print("aldermen: pull returned too few named wards; keeping existing aldermen.json")
        return
    write_json(SITE_DATA_DIR / "aldermen.json", {
        "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Chicago Data Portal — Ward Offices (htai-wnw4)",
        "data_tier": "real",
        "note": ("Current alderperson roster from the city's Ward Offices dataset; "
                 "refreshed each pipeline run. Vacant seats appear as null."),
        "lookup_url": ALDERMAN_LOOKUP_URL,
        "wards": wards,
    })
    named = sum(1 for w in wards if w["alderman"])
    print(f"aldermen: {named}/50 wards have a current alderperson")


if __name__ == "__main__":
    main()
