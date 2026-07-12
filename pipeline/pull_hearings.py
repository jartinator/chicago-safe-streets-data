"""Pull upcoming Transportation / Pedestrian & Traffic Safety committee meetings.

Chicago's live meeting calendar moved to eLMS (chicityclerkelms.chicago.gov)
when the city retired Legistar in 2023. Earlier research could not find a
public JSON endpoint (guesses at /api/meetings, /api/Events, swagger.json all
404'd — see DECISIONS.md #14), so this module used to link out to the calendar
page instead of showing structured data.

CORRECTED 2026-07-12: the eLMS public API exists at singular-noun endpoints on
the API root (GET api.chicityclerkelms.chicago.gov/meeting with OData-ish
filter/sort/limit params; rows arrive under the "data" key). This module now
pulls real meetings per committee of interest, keeping only future,
non-cancelled ones. The API is undocumented and unversioned, so it is treated
as best-effort: if every committee's fetch fails, the honest "link out"
fallback (committee name + live official calendar URL) is written instead of
fabricated or stale hearing dates. Non-fatal either way — this module never
raises the pipeline.

Idempotent: re-running overwrites cleanly.
"""
import argparse
from datetime import datetime, timezone

import requests

from config import RAW_DIR, ELMS_API_URL, ELMS_MEETINGS_URL, ELMS_COMMITTEES_OF_INTEREST
from socrata import write_json

VALID_STATUSES = {"Scheduled", "Scheduled & Published"}


def fetch_committee_meetings(committee):
    """One filtered call to the eLMS public API; returns raw rows or None on any failure."""
    try:
        resp = requests.get(
            f"{ELMS_API_URL}/meeting",
            params={"filter": f"body eq '{committee}'", "sort": "date desc", "limit": 50},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        # The live API wraps rows in a {"facets": [...], "data": [...], "meta": {...}}
        # envelope (verified 2026-07-12); accept a bare list too in case that changes.
        rows = data if isinstance(data, list) else data.get("data") or data.get("items")
        return rows if isinstance(rows, list) else None
    except (requests.RequestException, ValueError):
        return None


def _file_url(files, kind):
    for f in files or []:
        if (f.get("attachmentType") or "").lower() == kind:
            return f.get("path") or None
    return None


def normalize_meetings(rows, today):
    """Future, non-cancelled meetings with a parseable ISO date, oldest first."""
    out = []
    for r in rows or []:
        if r.get("status") not in VALID_STATUSES:
            continue
        d = str(r.get("date") or "")
        if len(d) < 10 or d[:10] < today or d[4] != "-":
            continue
        out.append({
            "date": d,
            "status": r["status"],
            "location": r.get("location") or None,
            "agenda_url": _file_url(r.get("files"), "agenda"),
            "notice_url": _file_url(r.get("files"), "notice"),
            "comment": r.get("comment") or None,
        })
    return sorted(out, key=lambda m: m["date"])


def main():
    argparse.ArgumentParser(
        description="Pull upcoming bike/traffic-safety committee meetings from the eLMS API."
    ).parse_args()

    as_of = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today = datetime.now(timezone.utc).date().isoformat()
    committees_out = []
    any_structured = False
    for committee in ELMS_COMMITTEES_OF_INTEREST:
        rows = fetch_committee_meetings(committee)
        if rows is not None:
            # An empty list of *validated* future meetings still counts as structured
            # data — "no meetings scheduled" is honest data, not a fetch failure.
            any_structured = True
        committees_out.append({
            "committee": committee,
            "meetings": normalize_meetings(rows, today) if rows is not None else [],
            "calendar_url": f"{ELMS_MEETINGS_URL}?body={committee.replace(' ', '+')}",
        })

    output_path = RAW_DIR / "hearings.json"
    payload = {
        "as_of": as_of,
        "structured_data_available": any_structured,
        "note": (
            "Meetings from the City Clerk eLMS public API "
            "(api.chicityclerkelms.chicago.gov), refreshed each pipeline run; "
            "best-effort — verify against the official calendar before attending."
            if any_structured else
            "The eLMS public API was unreachable this run; this links to the live "
            "official calendar per committee rather than showing unverified or "
            "stale hearing dates. See DECISIONS.md."
        ),
        "committees": committees_out,
    }
    if any_structured:
        payload["source"] = "elms_api"
    write_json(output_path, payload)
    total = sum(len(c["meetings"]) for c in committees_out)
    print(f"hearings: {len(committees_out)} committees tracked, {total} upcoming meetings, "
          f"structured_data_available={any_structured} (as_of {as_of})")


if __name__ == "__main__":
    main()
