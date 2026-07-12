"""Pull current street/bike-safety council legislation from Chicago Councilmatic.

Deterministic fetching only — no analysis, no LLMs (see CONTRIBUTING.md). Casts
the same SAFETY_TOPIC_KEYWORDS net as pull_council_records.py, but against
DataMade's Councilmatic Datasette, and owns only records with activity AFTER
LEGISTAR_DATA_FROZEN_AT — i.e. the gap the Legistar Web API cannot see.

Normalizes each bill into the pipeline's existing council-record schema so
classify_safety_topic.py and aggregate.py stay source-agnostic. Attaches
recorded_votes ONLY on the rare bills with a recorded roll-call split (most
council actions pass by voice vote).

Non-fatal, like pull_council_records.py: on any request failure it warns and
leaves raw/councilmatic_records.json absent; aggregate.py falls back.
Idempotent: re-running overwrites cleanly.
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

import requests

from config import RAW_DIR, SAFETY_TOPIC_KEYWORDS, LEGISTAR_DATA_FROZEN_AT
from councilmatic import query
from socrata import write_json


def parse_classification(raw):
    """Councilmatic bill.classification is a JSON-encoded array string like
    '["ordinance"]'. Return the first element, the raw string if it doesn't
    parse, or None if empty/None."""
    if not raw:
        return None
    try:
        vals = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw
    if isinstance(vals, list):
        return vals[0] if vals else None
    return str(vals)


def councilmatic_url(identifier):
    return f"https://chicago.councilmatic.org/legislation/{identifier}/"


def _option(pv):
    return (pv.get("option") or "").lower()


def extract_recorded_votes(vote_row, person_votes):
    """recorded_votes dict for one vote event, or None if there was no dissent."""
    no_voters = sorted(pv["voter_name"] for pv in person_votes if _option(pv) == "no")
    if not no_voters:
        return None
    return {
        "date": (vote_row.get("start_date") or "")[:10] or None,
        "yes": sum(1 for pv in person_votes if _option(pv) == "yes"),
        "no": sum(1 for pv in person_votes if _option(pv) == "no"),
        "absent": sum(1 for pv in person_votes if _option(pv) == "absent"),
        "no_voters": no_voters,
        "result": vote_row.get("result"),
    }


def choose_recorded_votes(vote_rows, personvotes_by_event):
    """Most-recent contested vote for a bill (recorded dissent), else None."""
    for ve in sorted(vote_rows, key=lambda v: v.get("start_date") or "", reverse=True):
        rv = extract_recorded_votes(ve, personvotes_by_event.get(ve["id"], []))
        if rv:
            return rv
    return None


def group_sponsors(sponsor_rows):
    """{bill_id: [sponsor names]} with the primary sponsor first, then A-Z."""
    by_bill = defaultdict(list)
    for r in sorted(sponsor_rows,
                    key=lambda r: (0 if r.get("primary") else 1, r.get("name") or "")):
        by_bill[r["bill_id"]].append(r["name"])
    return dict(by_bill)


def build_record(bill, sponsors, recorded_votes):
    """Normalize a Councilmatic bill into the shared council-record schema."""
    rec = {
        "matter_id": bill["identifier"],
        "title": bill.get("title"),
        "type": parse_classification(bill.get("classification")),
        "status": bill.get("status"),
        "intro_date": bill.get("intro_date"),
        "body": None,
        "sponsors": list(sponsors),
        "url": councilmatic_url(bill["identifier"]),
        "source": "councilmatic",
    }
    if recorded_votes:
        rec["recorded_votes"] = recorded_votes
    return rec


def max_action_date(bill_rows):
    """Max last_action date across fetched bills (for the currency note)."""
    dates = [b.get("last_action") for b in bill_rows if b.get("last_action")]
    return max(dates)[:10] if dates else None


def title_like_clause(keywords, col="b.title"):
    """OR of case-insensitive substring matches. keywords are our own config
    constants (no injection surface)."""
    return " or ".join(f"lower({col}) like '%{kw.lower()}%'" for kw in keywords)


def bills_sql(keywords, frozen):
    """Safety bills whose most recent action is strictly after `frozen`."""
    like = title_like_clause(keywords)
    return (
        "select b.id, b.identifier, b.title, b.classification, "
        "max(a.date) as last_action, "
        "(select a2.description from billaction a2 where a2.bill_id = b.id "
        " order by a2.date desc limit 1) as status, "
        "(select min(a3.date) from billaction a3 where a3.bill_id = b.id) as intro_date "
        "from bill b join billaction a on a.bill_id = b.id "
        f"where ({like}) "
        "group by b.id "
        f"having max(a.date) > '{frozen}' "
        "order by last_action desc"
    )
