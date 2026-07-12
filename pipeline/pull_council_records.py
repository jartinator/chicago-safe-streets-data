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

NOT part of the weekly live run anymore. Because the source is frozen at
LEGISTAR_DATA_FROZEN_AT and can never change, we snapshot it once into
pipeline/frozen/council_records.json (committed) and restore_frozen.py copies that
into raw/ each run instead — no pointless weekly re-pull. Run this script by hand
ONLY to regenerate that snapshot (e.g. after editing SAFETY_TOPIC_KEYWORDS or if the
Legistar schema changes), then copy raw/council_records.json into pipeline/frozen/
and commit it.

Idempotent: re-running overwrites cleanly.
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

from config import RAW_DIR, SAFETY_TOPIC_KEYWORDS, LEGISTAR_DATA_FROZEN_AT
from legistar import fetch_all, fetch_one, keyword_filter
from socrata import write_json

# Legistar has no documented batch-by-many-ids endpoint for /sponsors, so this
# is one request per matched matter — bounded concurrency keeps a broad
# keyword-net run (potentially hundreds of matters) from taking many minutes
# of sequential round-trips.
SPONSOR_FETCH_WORKERS = 8


def fetch_sponsors(matter_id):
    try:
        rows = fetch_one(f"matters/{matter_id}/sponsors")
        return matter_id, [r.get("MatterSponsorName") for r in rows if r.get("MatterSponsorName")]
    except requests.RequestException as exc:
        print(f"  WARNING: sponsors fetch failed for matter {matter_id} ({exc}) — "
              f"treating as no sponsors for this record.", file=sys.stderr)
        return matter_id, []


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

    matter_ids = [m.get("MatterId") for m in matters if m.get("MatterId")]
    with ThreadPoolExecutor(max_workers=SPONSOR_FETCH_WORKERS) as pool:
        sponsors_by_id = dict(pool.map(fetch_sponsors, matter_ids))

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
            "sponsors": sponsors_by_id.get(mid, []) if mid else [],
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
