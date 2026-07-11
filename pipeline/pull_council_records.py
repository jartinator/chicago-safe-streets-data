"""Pull street/bike-safety-related legislation from the Legistar Web API.

Deterministic data fetching only — no analysis, no LLMs (see CONTRIBUTING.md).
Casts a broad net: any Matter (ordinance/order/resolution) whose title matches
SAFETY_TOPIC_KEYWORDS (config.py), plus its sponsors and action history. Topic
relevance is refined later by classify_safety_topic.py — this module's job is
just to fetch real records, not judge them.

IMPORTANT — coverage gap: Chicago's council migrated off Legistar around
2023-06-21 (LEGISTAR_DATA_FROZEN_AT). This module cannot see anything after
that date; aggregate.py surfaces that gap explicitly rather than silently
presenting stale data as current. See DECISIONS.md.

Unlike the core Socrata pulls, this hits a third-party-hosted API outside our
control, so a failure here is non-fatal: it warns and leaves
raw/council_records.json absent, and aggregate.py falls back to a stub.

Idempotent: re-running overwrites cleanly.
"""
import argparse
import sys

import requests

from config import RAW_DIR, SAFETY_TOPIC_KEYWORDS, LEGISTAR_DATA_FROZEN_AT
from legistar import fetch_all, fetch_one, keyword_filter
from socrata import write_json


def fetch_sponsors(matter_id):
    try:
        rows = fetch_one(f"matters/{matter_id}/sponsors")
        return [r.get("MatterSponsorName") for r in rows if r.get("MatterSponsorName")]
    except requests.RequestException:
        return []


def main():
    argparse.ArgumentParser(
        description="Pull safety-related council legislation from the Legistar Web API."
    ).parse_args()

    try:
        filter_ = keyword_filter("MatterTitle", SAFETY_TOPIC_KEYWORDS)
        print("Fetching council_records from Legistar Web API...", file=sys.stderr)
        matters = list(fetch_all(
            "matters",
            filter_=filter_,
            orderby="MatterIntroDate desc",
        ))
    except requests.RequestException as exc:
        print(f"WARNING: council_records pull failed ({exc}) — council_records.json "
              f"will ship as a stub this run. See DECISIONS.md.", file=sys.stderr)
        return

    records = []
    for m in matters:
        mid = m.get("MatterId")
        records.append({
            "matter_id": mid,
            "title": m.get("MatterTitle"),
            "type": m.get("MatterTypeName"),
            "status": m.get("MatterStatusName"),
            "intro_date": m.get("MatterIntroDate"),
            "body": m.get("MatterBodyName"),
            "sponsors": fetch_sponsors(mid) if mid else [],
            "url": f"https://chicago.legistar.com/LegislationDetail.aspx?ID={mid}" if mid else None,
        })

    output_path = RAW_DIR / "council_records.json"
    write_json(output_path, {
        "data_frozen_at": LEGISTAR_DATA_FROZEN_AT,
        "keywords": SAFETY_TOPIC_KEYWORDS,
        "records": records,
    })
    print(f"council_records: {len(records)} matching matters "
          f"(Legistar data current only through {LEGISTAR_DATA_FROZEN_AT})")


if __name__ == "__main__":
    main()
