"""Union the two council-record raw files for downstream consumers.

Legistar (raw/council_records.json, activity <= LEGISTAR_DATA_FROZEN_AT) and
Councilmatic (raw/councilmatic_records.json, activity > that date) are pulled
independently and may each be absent. classify_safety_topic.py and aggregate.py
both read the combined set through here, so neither has to know about two files.
"""
import json

from config import LEGISTAR_DATA_FROZEN_AT


def _read(path):
    return json.loads(path.read_text()) if path.exists() else None


def load_all_council_records(raw_dir):
    """Return (records, meta).

    records: council-record dicts, each tagged with `source` ('legistar' or
    'councilmatic'), deduped by (source, matter_id), Councilmatic appended after
    Legistar.
    meta: {'has_councilmatic', 'legistar_frozen_at', 'councilmatic_latest'}.
    """
    legistar = _read(raw_dir / "council_records.json")
    councilmatic = _read(raw_dir / "councilmatic_records.json")

    records = []
    seen = set()
    for raw, default_source in ((legistar, "legistar"), (councilmatic, "councilmatic")):
        for r in (raw or {}).get("records", []):
            rec = dict(r)
            rec.setdefault("source", default_source)
            key = (rec["source"], rec["matter_id"])
            if key in seen:
                continue
            seen.add(key)
            records.append(rec)

    meta = {
        "has_councilmatic": bool(councilmatic and councilmatic.get("records")),
        "legistar_frozen_at": (legistar.get("data_frozen_at", LEGISTAR_DATA_FROZEN_AT)
                               if legistar else None),
        "councilmatic_latest": (councilmatic.get("latest_action_date")
                                if councilmatic else None),
    }
    return records, meta
