"""Pull upcoming Transportation / Pedestrian & Traffic Safety committee hearings.

Chicago's live meeting calendar moved to eLMS (chicityclerkelms.chicago.gov)
when the city retired Legistar in 2023. The Meetings page renders a real
calendar, but no public JSON/RSS endpoint could be found during research
(direct guesses at /api/meetings, /api/Events, swagger.json all 404'd — see
DECISIONS.md). Legistar's own API is not a substitute here: its data is frozen
at 2023-06-21, so it cannot answer "what's upcoming."

This module tries a same-page JSON content-negotiation request (a common
ASP.NET pattern) as a best-effort attempt, refreshed every pipeline run. If
that doesn't return structured rows, it writes an honest "link out" fallback
listing the committees of interest and the live official calendar URL, rather
than fabricating or silently going stale. Non-fatal either way — this module
never raises the pipeline.

Idempotent: re-running overwrites cleanly.
"""
import argparse
from datetime import datetime, timezone

import requests

from config import RAW_DIR, ELMS_MEETINGS_URL, ELMS_COMMITTEES_OF_INTEREST
from socrata import write_json


def try_fetch_structured(committee):
    try:
        resp = requests.get(
            ELMS_MEETINGS_URL,
            params={"body": committee},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        if resp.status_code == 200 and "application/json" in resp.headers.get("Content-Type", ""):
            return resp.json()
    except requests.RequestException:
        pass
    return None


def main():
    argparse.ArgumentParser(
        description="Pull upcoming bike/traffic-safety committee hearings (best-effort)."
    ).parse_args()

    as_of = datetime.now(timezone.utc).isoformat(timespec="seconds")
    committees_out = []
    any_structured = False
    for committee in ELMS_COMMITTEES_OF_INTEREST:
        rows = try_fetch_structured(committee)
        if rows:
            any_structured = True
        committees_out.append({
            "committee": committee,
            "meetings": rows or [],
            "calendar_url": f"{ELMS_MEETINGS_URL}?body={committee.replace(' ', '+')}",
        })

    output_path = RAW_DIR / "hearings.json"
    write_json(output_path, {
        "as_of": as_of,
        "structured_data_available": any_structured,
        "note": (
            "No public JSON/RSS endpoint for the eLMS meeting calendar was confirmed; "
            "this links to the live official calendar per committee rather than showing "
            "unverified or stale hearing dates. See DECISIONS.md."
            if not any_structured else
            "Structured meeting data fetched directly from eLMS."
        ),
        "committees": committees_out,
    })
    print(f"hearings: {len(committees_out)} committees tracked, "
          f"structured_data_available={any_structured} (as_of {as_of})")


if __name__ == "__main__":
    main()
