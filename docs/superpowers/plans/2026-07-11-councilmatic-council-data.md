# Councilmatic Council-Data Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the frozen-Legistar (2023-06-21) council-data gap by pulling current Chicago City Council legislation from DataMade's Chicago Councilmatic Datasette, merged with the existing Legistar records, plus an honest contested-votes accountability layer.

**Architecture:** A new deterministic puller (`pull_councilmatic.py`) writes a second raw file; a small shared union helper (`council_merge.py`) stitches the two raw files together at read time; `classify_safety_topic.py` and `aggregate.py` both switch their single read to the helper, so everything downstream is source-agnostic. Contested roll-call splits ride along per-record; a per-alderman `recorded_no_votes` count is added.

**Tech Stack:** Python 3, `requests` (already a dep), Datasette SQL-over-HTTP JSON API, `pytest` (new dev-only dep). No new runtime dependencies.

## Global Constraints

- **Pull modules are deterministic** — no LLMs, no analysis in `pull_*` (CONTRIBUTING.md). Classification stays in `classify_safety_topic.py`.
- **Non-fatal third-party pulls** — a failure in `pull_councilmatic.py` must warn to stderr, leave its raw file absent, and return; the pipeline continues and `aggregate.py` falls back. Mirror `pull_council_records.py`.
- **Datasette URL is the UN-hashed base** `https://puddle.datamade.us/chicago_council` — the hashed route (`chicago_council-464e17d`) changes on nightly DB rebuilds; `requests` follows the 302 and preserves the query string. Never hardcode the hash.
- **Provenance tier `real`**, disclosed as sourced via DataMade's Councilmatic mirror.
- **Out of scope (do NOT build):** per-alderman attendance; committees/meetings; the 3.7 GB DB-dump path (documented in a comment only); `check_provenance.py` wiring (that file isn't on `main`).
- **Platform:** Windows dev shell — use `python` and `pytest` (not `python3`).
- **Frozen-date constant:** `LEGISTAR_DATA_FROZEN_AT = "2023-06-21"` (config.py) is the boundary; Councilmatic owns records with activity strictly after it.
- Reuse `SAFETY_TOPIC_KEYWORDS` (config.py) as the keyword net — do not invent a second list.

---

### Task 1: Project setup — config constant + pytest scaffolding

**Files:**
- Modify: `pipeline/config.py` (after the `LEGISTAR_*` block, ~line 48)
- Create: `pipeline/requirements-dev.txt`
- Create: `pipeline/tests/conftest.py`
- Create: `pipeline/tests/test_config.py`

**Interfaces:**
- Produces: `config.COUNCILMATIC_DATASETTE_URL: str`

- [ ] **Step 1: Add the config constant**

In `pipeline/config.py`, immediately after the `LEGISTAR_DATA_FROZEN_AT = "2023-06-21"` line, add:

```python
# Chicago Councilmatic (DataMade, MIT-licensed) — official Chicago City Council
# data republished as a public Datasette (SQL-over-HTTP JSON API), updated
# nightly and CURRENT to the present day. This is how we cross the
# LEGISTAR_DATA_FROZEN_AT gap above. Confirmed live 2026-07-11 (data through
# 2026-07-09). Use the UN-hashed base URL: Datasette serves the DB under a
# content-hashed route (e.g. /chicago_council-464e17d) that changes on each
# nightly rebuild, and 302-redirects the un-hashed path to it (requests follows
# the redirect and preserves the ?sql= query string).
# Robust fallback if this host ever disappears: the nightly full-DB dump
# chicago_council.db.zip at github.com/datamade/chicago-council-scrapers/releases.
COUNCILMATIC_DATASETTE_URL = "https://puddle.datamade.us/chicago_council"
```

Also update the existing `LEGISTAR_DATA_FROZEN_AT` comment's final sentence (the one saying Legistar "CANNOT answer 'what's happening now'") by appending: `Councilmatic (COUNCILMATIC_DATASETTE_URL, below) now covers the far side of this boundary.`

- [ ] **Step 2: Create the dev requirements file**

`pipeline/requirements-dev.txt`:

```
# Dev/test only — not needed to run the pipeline.
-r requirements.txt
pytest>=8
```

- [ ] **Step 3: Create the test path shim**

Pipeline modules use flat imports (`from config import ...`), so tests need the `pipeline/` dir on `sys.path`. `pipeline/tests/conftest.py`:

```python
import pathlib
import sys

# Put the pipeline/ directory (parent of tests/) on sys.path so tests can
# `import config`, `import councilmatic`, etc. the same flat way the modules do.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
```

- [ ] **Step 4: Write the setup test**

`pipeline/tests/test_config.py`:

```python
import config


def test_councilmatic_url_is_unhashed_base():
    # Must be the un-hashed base so the nightly content-hash change can't break us.
    assert config.COUNCILMATIC_DATASETTE_URL == "https://puddle.datamade.us/chicago_council"
```

- [ ] **Step 5: Install and run**

Run: `python -m pip install -r pipeline/requirements-dev.txt && python -m pytest pipeline/tests/test_config.py -v`
Expected: PASS (1 passed).

- [ ] **Step 6: Commit**

```bash
git add pipeline/config.py pipeline/requirements-dev.txt pipeline/tests/conftest.py pipeline/tests/test_config.py
git commit -m "feat: add Councilmatic Datasette config + pytest scaffolding"
```

---

### Task 2: Councilmatic fetch helper (`councilmatic.py`)

**Files:**
- Create: `pipeline/councilmatic.py`
- Create: `pipeline/tests/test_councilmatic_fetch.py`

**Interfaces:**
- Consumes: `config.COUNCILMATIC_DATASETTE_URL`
- Produces: `councilmatic.query(sql: str, retries: int = 3) -> list[dict]`

- [ ] **Step 1: Write the failing test**

`pipeline/tests/test_councilmatic_fetch.py`:

```python
import councilmatic


def test_query_builds_url_params_and_returns_rows(monkeypatch):
    calls = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return [{"x": 42}]

        def raise_for_status(self):
            raise AssertionError("raise_for_status should not be called on 200")

    def fake_get(url, params, timeout):
        calls["url"] = url
        calls["params"] = params
        return FakeResp()

    monkeypatch.setattr(councilmatic._SESSION, "get", fake_get)

    rows = councilmatic.query("select 42 as x")

    assert rows == [{"x": 42}]
    assert calls["url"] == "https://puddle.datamade.us/chicago_council.json"
    assert calls["params"] == {"sql": "select 42 as x", "_shape": "array"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest pipeline/tests/test_councilmatic_fetch.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'councilmatic'`.

- [ ] **Step 3: Write the implementation**

`pipeline/councilmatic.py`:

```python
"""Shared Chicago Councilmatic (DataMade) fetch helper — read-only SQL over HTTP.

puddle.datamade.us republishes official Chicago City Council data as a public
Datasette instance whose JSON API accepts arbitrary read-only SQL. This is how
we cross the post-2023-06-21 gap the Legistar Web API cannot (see config.py).
Public, no auth. Confirmed live 2026-07-11.

COUNCILMATIC_DATASETTE_URL is the UN-hashed base; the DB lives under a
content-hashed route that changes on nightly rebuilds, and Datasette 302s the
un-hashed path to it. requests follows the redirect and preserves ?sql=.
"""
import time

import requests

from config import COUNCILMATIC_DATASETTE_URL

_SESSION = requests.Session()


def query(sql, retries=3):
    """Run read-only SQL against the Councilmatic Datasette; return list[dict]."""
    url = f"{COUNCILMATIC_DATASETTE_URL}.json"
    params = {"sql": sql, "_shape": "array"}
    delay = 2
    for attempt in range(retries + 1):
        resp = _SESSION.get(url, params=params, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        if attempt == retries:
            resp.raise_for_status()
        time.sleep(delay)
        delay *= 2
    raise RuntimeError("unreachable")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest pipeline/tests/test_councilmatic_fetch.py -v`
Expected: PASS.

- [ ] **Step 5: Live smoke check (network)**

Run: `cd pipeline && python -c "import councilmatic; print(councilmatic.query('select 7 as n'))"`
Expected: `[{'n': 7}]`. (If offline, skip — this only confirms the live endpoint.)

- [ ] **Step 6: Commit**

```bash
git add pipeline/councilmatic.py pipeline/tests/test_councilmatic_fetch.py
git commit -m "feat: add Councilmatic Datasette SQL fetch helper"
```

---

### Task 3: Pure transform helpers in `pull_councilmatic.py`

These are the pure, network-free functions the puller's `main()` (Task 4) composes. TDD each.

**Files:**
- Create: `pipeline/pull_councilmatic.py` (helpers only this task; `main()` in Task 4)
- Create: `pipeline/tests/test_pull_councilmatic.py`

**Interfaces:**
- Produces:
  - `parse_classification(raw: str | None) -> str | None`
  - `councilmatic_url(identifier: str) -> str`
  - `extract_recorded_votes(vote_row: dict, person_votes: list[dict]) -> dict | None`
  - `choose_recorded_votes(vote_rows: list[dict], personvotes_by_event: dict[str, list[dict]]) -> dict | None`
  - `group_sponsors(sponsor_rows: list[dict]) -> dict[str, list[str]]`
  - `build_record(bill: dict, sponsors: list[str], recorded_votes: dict | None) -> dict`
  - `max_action_date(bill_rows: list[dict]) -> str | None`
  - `title_like_clause(keywords: list[str], col: str = "b.title") -> str`
  - `bills_sql(keywords: list[str], frozen: str) -> str`

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/test_pull_councilmatic.py`:

```python
import pull_councilmatic as pc


def test_parse_classification_unwraps_json_array():
    assert pc.parse_classification('["ordinance"]') == "ordinance"


def test_parse_classification_handles_empty_and_plain():
    assert pc.parse_classification(None) is None
    assert pc.parse_classification("[]") is None
    assert pc.parse_classification("ordinance") == "ordinance"


def test_councilmatic_url():
    assert pc.councilmatic_url("O2025-0015514") == \
        "https://chicago.councilmatic.org/legislation/O2025-0015514/"


def test_extract_recorded_votes_returns_none_when_unanimous():
    pvs = [{"voter_name": "A", "option": "yes"}, {"voter_name": "B", "option": "yes"}]
    assert pc.extract_recorded_votes({"start_date": "2026-03-18", "result": "pass"}, pvs) is None


def test_extract_recorded_votes_tallies_dissent():
    pvs = [
        {"voter_name": "Yes One", "option": "yes"},
        {"voter_name": "No One", "option": "no"},
        {"voter_name": "Absent One", "option": "absent"},
    ]
    rv = pc.extract_recorded_votes({"start_date": "2026-03-18T00:00:00", "result": "pass"}, pvs)
    assert rv == {
        "date": "2026-03-18",
        "yes": 1, "no": 1, "absent": 1,
        "no_voters": ["No One"],
        "result": "pass",
    }


def test_choose_recorded_votes_picks_most_recent_contested():
    events = [
        {"id": "v1", "start_date": "2025-01-01", "result": "pass"},
        {"id": "v2", "start_date": "2026-01-01", "result": "pass"},
    ]
    pvs = {
        "v1": [{"voter_name": "X", "option": "no"}, {"voter_name": "Y", "option": "yes"}],
        "v2": [{"voter_name": "X", "option": "yes"}, {"voter_name": "Y", "option": "yes"}],
    }
    # v2 is more recent but unanimous; v1 is the most recent contested one.
    rv = pc.choose_recorded_votes(events, pvs)
    assert rv["no_voters"] == ["X"]


def test_group_sponsors_primary_first():
    rows = [
        {"bill_id": "b1", "name": "Second, A", "primary": 0},
        {"bill_id": "b1", "name": "Primary, P", "primary": 1},
        {"bill_id": "b2", "name": "Solo, S", "primary": 1},
    ]
    grouped = pc.group_sponsors(rows)
    assert grouped["b1"] == ["Primary, P", "Second, A"]
    assert grouped["b2"] == ["Solo, S"]


def test_build_record_normalizes_and_omits_votes_when_none():
    bill = {"identifier": "O2025-1", "title": "Bike lane thing",
            "classification": '["ordinance"]', "status": "Passed",
            "intro_date": "2025-02-01T00:00:00"}
    rec = pc.build_record(bill, ["Hopkins, Brian"], None)
    assert rec == {
        "matter_id": "O2025-1",
        "title": "Bike lane thing",
        "type": "ordinance",
        "status": "Passed",
        "intro_date": "2025-02-01T00:00:00",
        "body": None,
        "sponsors": ["Hopkins, Brian"],
        "url": "https://chicago.councilmatic.org/legislation/O2025-1/",
        "source": "councilmatic",
    }


def test_build_record_includes_votes_when_present():
    bill = {"identifier": "O2025-2", "title": "x", "classification": "[]",
            "status": "s", "intro_date": "2025-02-01T00:00:00"}
    rv = {"date": "2025-03-01", "yes": 30, "no": 18, "absent": 2,
          "no_voters": ["No One"], "result": "pass"}
    rec = pc.build_record(bill, [], rv)
    assert rec["recorded_votes"] == rv
    assert rec["type"] is None


def test_max_action_date():
    rows = [{"last_action": "2024-05-01"}, {"last_action": "2026-07-09T00:00:00"}]
    assert pc.max_action_date(rows) == "2026-07-09"
    assert pc.max_action_date([]) is None


def test_bills_sql_contains_keywords_and_frozen_boundary():
    sql = pc.bills_sql(["bike", "vision zero"], "2023-06-21")
    assert "like '%bike%'" in sql
    assert "like '%vision zero%'" in sql
    assert "2023-06-21" in sql
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest pipeline/tests/test_pull_councilmatic.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pull_councilmatic'`.

- [ ] **Step 3: Write the helpers**

`pipeline/pull_councilmatic.py` (helpers only for now — `main()` added in Task 4):

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest pipeline/tests/test_pull_councilmatic.py -v`
Expected: PASS (all).

- [ ] **Step 5: Commit**

```bash
git add pipeline/pull_councilmatic.py pipeline/tests/test_pull_councilmatic.py
git commit -m "feat: add pure transform helpers for Councilmatic puller"
```

---

### Task 4: Councilmatic puller `main()` (orchestration + non-fatal I/O)

**Files:**
- Modify: `pipeline/pull_councilmatic.py` (append `_quote_ids`, `fetch_sponsors_and_votes`, `main`, and the `__main__` guard)

**Interfaces:**
- Consumes: `councilmatic.query`, all Task 3 helpers, `RAW_DIR`, `SAFETY_TOPIC_KEYWORDS`, `LEGISTAR_DATA_FROZEN_AT`
- Produces: `raw/councilmatic_records.json` with shape
  `{source, fetched_at, covers_from, latest_action_date, keywords, records:[...]}`

- [ ] **Step 1: Write the SQL-quoting helper test**

Append to `pipeline/tests/test_pull_councilmatic.py`:

```python
def test_quote_ids():
    assert pc._quote_ids(["ocd-bill/a", "ocd-bill/b"]) == "'ocd-bill/a','ocd-bill/b'"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest pipeline/tests/test_pull_councilmatic.py::test_quote_ids -v`
Expected: FAIL with `AttributeError: module 'pull_councilmatic' has no attribute '_quote_ids'`.

- [ ] **Step 3: Append orchestration to `pull_councilmatic.py`**

```python
def _quote_ids(ids):
    return ",".join("'" + str(i).replace("'", "''") + "'" for i in ids)


def fetch_sponsors_and_votes(bill_ids):
    """Return (sponsors_by_bill, votes_by_bill) for the given internal bill ids.

    sponsors_by_bill: {bill_id: [names]}; votes_by_bill: {bill_id: recorded_votes}.
    Bills with no sponsors/votes simply won't appear as keys.
    """
    if not bill_ids:
        return {}, {}
    id_list = _quote_ids(bill_ids)

    sponsor_rows = query(
        'select bs.bill_id, bs.name, bs."primary" from billsponsorship bs '
        f"where bs.bill_id in ({id_list})"
    )
    sponsors_by_bill = group_sponsors(sponsor_rows)

    vote_rows = query(
        "select ve.id, ve.bill_id, ve.start_date, ve.result from voteevent ve "
        f"where ve.bill_id in ({id_list})"
    )
    votes_by_bill = {}
    if vote_rows:
        event_ids = [v["id"] for v in vote_rows]
        pv_rows = query(
            "select pv.vote_event_id, pv.voter_name, pv.option from personvote pv "
            f"where pv.vote_event_id in ({_quote_ids(event_ids)})"
        )
        pv_by_event = defaultdict(list)
        for pv in pv_rows:
            pv_by_event[pv["vote_event_id"]].append(pv)
        events_by_bill = defaultdict(list)
        for v in vote_rows:
            events_by_bill[v["bill_id"]].append(v)
        for bid, events in events_by_bill.items():
            rv = choose_recorded_votes(events, pv_by_event)
            if rv:
                votes_by_bill[bid] = rv
    return sponsors_by_bill, votes_by_bill


def main():
    argparse.ArgumentParser(
        description="Pull current safety-related council legislation from Chicago Councilmatic."
    ).parse_args()

    frozen = LEGISTAR_DATA_FROZEN_AT
    try:
        print("Fetching councilmatic_records from the Councilmatic Datasette...",
              file=sys.stderr)
        bills = query(bills_sql(SAFETY_TOPIC_KEYWORDS, frozen))
    except requests.RequestException as exc:
        print(f"WARNING: councilmatic pull failed ({exc}) — councilmatic_records.json "
              f"will be absent this run; aggregate.py falls back to Legistar-only. "
              f"See DECISIONS.md.", file=sys.stderr)
        return

    if not bills:
        print(f"councilmatic: no safety bills with activity after {frozen} "
              f"(nothing to write this run).", file=sys.stderr)
        return

    try:
        sponsors_by_bill, votes_by_bill = fetch_sponsors_and_votes([b["id"] for b in bills])
    except requests.RequestException as exc:
        print(f"WARNING: councilmatic sponsors/votes fetch failed ({exc}) — writing bills "
              f"without sponsors/votes this run.", file=sys.stderr)
        sponsors_by_bill, votes_by_bill = {}, {}

    records = [build_record(b, sponsors_by_bill.get(b["id"], []), votes_by_bill.get(b["id"]))
               for b in bills]

    output_path = RAW_DIR / "councilmatic_records.json"
    write_json(output_path, {
        "source": "councilmatic",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "covers_from": frozen,
        "latest_action_date": max_action_date(bills),
        "keywords": SAFETY_TOPIC_KEYWORDS,
        "records": records,
    })
    contested = sum(1 for r in records if r.get("recorded_votes"))
    print(f"councilmatic_records: {len(records)} bills after {frozen} "
          f"(through {max_action_date(bills)}), {contested} with a recorded contested vote")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the quote-ids test**

Run: `python -m pytest pipeline/tests/test_pull_councilmatic.py::test_quote_ids -v`
Expected: PASS.

- [ ] **Step 5: Live smoke run (network)**

Run: `cd pipeline && python pull_councilmatic.py`
Expected: stderr shows the fetch line; stdout prints e.g. `councilmatic_records: 2x bills after 2023-06-21 (through 2026-0x-xx), N with a recorded contested vote`. A `pipeline/raw/councilmatic_records.json` file appears.
Verify a record: `python -c "import json;d=json.load(open('raw/councilmatic_records.json'));r=d['records'][0];print(r['matter_id'],r['type'],r['source']);print('latest',d['latest_action_date'])"`
Expected: an identifier like `O2025-...`, a lowercase type, `councilmatic`, and a `latest` date after 2023-06-21.

- [ ] **Step 6: Commit**

```bash
git add pipeline/pull_councilmatic.py pipeline/tests/test_pull_councilmatic.py
git commit -m "feat: wire Councilmatic puller main() with non-fatal I/O"
```

*(Do not commit `raw/councilmatic_records.json` — raw/ is a working dir; confirm it's gitignored or leave it unstaged.)*

---

### Task 5: Shared union helper (`council_merge.py`)

**Files:**
- Create: `pipeline/council_merge.py`
- Create: `pipeline/tests/test_council_merge.py`

**Interfaces:**
- Consumes: `config.LEGISTAR_DATA_FROZEN_AT`
- Produces: `council_merge.load_all_council_records(raw_dir: pathlib.Path) -> tuple[list[dict], dict]`
  where meta = `{"has_councilmatic": bool, "legistar_frozen_at": str | None, "councilmatic_latest": str | None}`

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/test_council_merge.py`:

```python
import json

from council_merge import load_all_council_records


def _write(path, obj):
    path.write_text(json.dumps(obj))


def test_union_tags_sources_and_flags_meta(tmp_path):
    _write(tmp_path / "council_records.json", {
        "data_frozen_at": "2023-06-21",
        "records": [{"matter_id": 100, "title": "old legistar bill"}],
    })
    _write(tmp_path / "councilmatic_records.json", {
        "source": "councilmatic", "latest_action_date": "2026-07-09",
        "records": [{"matter_id": "O2025-1", "title": "new bill", "source": "councilmatic"}],
    })

    records, meta = load_all_council_records(tmp_path)

    by_id = {r["matter_id"]: r for r in records}
    assert by_id[100]["source"] == "legistar"      # defaulted in
    assert by_id["O2025-1"]["source"] == "councilmatic"
    assert meta == {"has_councilmatic": True,
                    "legistar_frozen_at": "2023-06-21",
                    "councilmatic_latest": "2026-07-09"}


def test_missing_councilmatic_file(tmp_path):
    _write(tmp_path / "council_records.json", {
        "data_frozen_at": "2023-06-21", "records": [{"matter_id": 1, "title": "x"}]})
    records, meta = load_all_council_records(tmp_path)
    assert len(records) == 1
    assert meta["has_councilmatic"] is False
    assert meta["councilmatic_latest"] is None


def test_missing_both_files(tmp_path):
    records, meta = load_all_council_records(tmp_path)
    assert records == []
    assert meta["has_councilmatic"] is False


def test_dedupes_within_source(tmp_path):
    _write(tmp_path / "council_records.json", {"records": [
        {"matter_id": 1, "title": "a"}, {"matter_id": 1, "title": "dup"}]})
    records, _ = load_all_council_records(tmp_path)
    assert len(records) == 1
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest pipeline/tests/test_council_merge.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'council_merge'`.

- [ ] **Step 3: Write the implementation**

`pipeline/council_merge.py`:

```python
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m pytest pipeline/tests/test_council_merge.py -v`
Expected: PASS (all).

- [ ] **Step 5: Commit**

```bash
git add pipeline/council_merge.py pipeline/tests/test_council_merge.py
git commit -m "feat: add council_merge union helper for the two raw sources"
```

---

### Task 6: Point `classify_safety_topic.py` at the union

**Files:**
- Modify: `pipeline/classify_safety_topic.py` (imports; `main()` lines ~105-111)
- Create: `pipeline/tests/test_classify_union.py`

**Interfaces:**
- Consumes: `council_merge.load_all_council_records`

- [ ] **Step 1: Write the failing test (offline, no API key)**

`pipeline/tests/test_classify_union.py`:

```python
import json
import os

import classify_safety_topic as cls


def test_classify_tags_councilmatic_records_via_union(tmp_path, monkeypatch):
    # No API key -> deterministic keyword_fallback path (no network).
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cls, "RAW_DIR", tmp_path)

    (tmp_path / "councilmatic_records.json").write_text(json.dumps({
        "source": "councilmatic", "latest_action_date": "2026-07-09",
        "records": [{"matter_id": "O2025-1", "title": "Protected bike lane on Main",
                     "type": "ordinance", "sponsors": [], "source": "councilmatic"}],
    }))

    cls.main()

    tags = {t["matter_id"]: t for t in
            json.loads((tmp_path / "safety_topic_tags.json").read_text())}
    assert "O2025-1" in tags
    assert tags["O2025-1"]["tagged_by"] == "keyword_fallback"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest pipeline/tests/test_classify_union.py -v`
Expected: FAIL — currently `main()` reads only `council_records.json`, so `safety_topic_tags.json` won't contain `O2025-1` (KeyError/assert fails).

- [ ] **Step 3: Edit `classify_safety_topic.py`**

Add to the imports block (near `from config import RAW_DIR`):

```python
from council_merge import load_all_council_records
```

Replace these lines in `main()`:

```python
    records_path = RAW_DIR / "council_records.json"
    if not records_path.exists():
        print("classify_safety_topic: no council_records.json (pull stage produced "
              "nothing or failed) — nothing to classify", file=sys.stderr)
        return

    records = json.loads(records_path.read_text()).get("records", [])
```

with:

```python
    records, _ = load_all_council_records(RAW_DIR)
    if not records:
        print("classify_safety_topic: no council records (pull stage produced "
              "nothing or failed) — nothing to classify", file=sys.stderr)
        return
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest pipeline/tests/test_classify_union.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/classify_safety_topic.py pipeline/tests/test_classify_union.py
git commit -m "feat: classify both council sources via the union helper"
```

---

### Task 7: Merge + note-flip in `aggregate.build_council_records`

**Files:**
- Modify: `pipeline/aggregate.py` (add import; rewrite `build_council_records`, lines ~539-597)
- Create: `pipeline/tests/test_aggregate_council.py`

**Interfaces:**
- Consumes: `council_merge.load_all_council_records`
- Produces: `build_council_records(name_to_ward)` output records now carry `source` and optional `recorded_votes`; the note reflects currency when Councilmatic data is present.

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/test_aggregate_council.py`:

```python
import json

import aggregate


def _seed(raw_dir, with_councilmatic):
    (raw_dir / "council_records.json").write_text(json.dumps({
        "data_frozen_at": "2023-06-21",
        "records": [{"matter_id": 100, "title": "Old bike ordinance", "type": "Ordinance",
                     "status": "Passed", "intro_date": "2022-01-01T00:00:00",
                     "sponsors": ["Legacy, L"], "url": "http://legistar/100"}],
    }))
    tags = [{"matter_id": 100, "topic_relevant": True, "topic_reason": "r",
             "tagged_by": "llm"}]
    if with_councilmatic:
        (raw_dir / "councilmatic_records.json").write_text(json.dumps({
            "source": "councilmatic", "latest_action_date": "2026-07-09",
            "records": [{"matter_id": "O2025-1", "title": "New protected lane",
                         "type": "ordinance", "status": "Passed",
                         "intro_date": "2025-02-01T00:00:00", "sponsors": ["Hopkins, Brian"],
                         "url": "http://cm/O2025-1", "source": "councilmatic",
                         "recorded_votes": {"date": "2025-03-01", "yes": 30, "no": 18,
                                            "absent": 2, "no_voters": ["No, N"],
                                            "result": "pass"}}],
        }))
        tags.append({"matter_id": "O2025-1", "topic_relevant": True,
                     "topic_reason": "r", "tagged_by": "llm"})
    (raw_dir / "safety_topic_tags.json").write_text(json.dumps(tags))


def test_merge_carries_source_and_votes_and_flips_note(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    _seed(tmp_path, with_councilmatic=True)

    out, records = aggregate.build_council_records({})

    by_id = {r["matter_id"]: r for r in records}
    assert by_id[100]["source"] == "legistar"
    assert by_id["O2025-1"]["source"] == "councilmatic"
    assert by_id["O2025-1"]["recorded_votes"]["no"] == 18
    assert "current through 2026-07-09" in out["note"]


def test_note_stays_frozen_without_councilmatic(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    _seed(tmp_path, with_councilmatic=False)

    out, records = aggregate.build_council_records({})

    assert len(records) == 1
    assert "only current through 2023-06-21" in out["note"]
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest pipeline/tests/test_aggregate_council.py -v`
Expected: FAIL (current code reads one file, has no `source`/`recorded_votes`/currency note).

- [ ] **Step 3: Edit `aggregate.py`**

Add to the imports near the top of the module:

```python
from council_merge import load_all_council_records
```

Replace the entire `build_council_records` function (lines ~539-597) with:

```python
def build_council_records(name_to_ward):
    records, meta = load_all_council_records(RAW_DIR)
    if not records:
        return empty_council_records(), []

    tags = {t["matter_id"]: t for t in
            json.loads((RAW_DIR / "safety_topic_tags.json").read_text())} \
        if (RAW_DIR / "safety_topic_tags.json").exists() else {}
    corrections = {t["matter_id"]: t for t in
                   json.loads((RAW_DIR / "safety_topic_corrections.json").read_text())} \
        if (RAW_DIR / "safety_topic_corrections.json").exists() else {}

    out = []
    for r in records:
        mid = r["matter_id"]
        if corrections.get(mid):
            tag, tag_source = corrections[mid], "manual_correction"
        elif tags.get(mid):
            tag, tag_source = tags[mid], tags[mid].get("tagged_by", "unknown")
        else:
            continue  # not yet classified this run
        sponsor_wards = sorted({name_to_ward[s.strip().lower()] for s in (r.get("sponsors") or [])
                                if s.strip().lower() in name_to_ward})
        rec = {
            "matter_id": mid,
            "title": r.get("title"),
            "type": r.get("type"),
            "status": r.get("status"),
            "intro_date": r.get("intro_date"),
            "sponsors": r.get("sponsors") or [],
            "sponsor_wards": sponsor_wards,
            "url": r.get("url"),
            "source": r.get("source", "legistar"),
            "topic_relevant": tag.get("topic_relevant", True),
            "topic_reason": tag.get("topic_reason", "(manual correction, no reason given)"),
            "topic_tagged_by": tag_source,
            "data_tier": "real",
            "topic_tag_tier": "derived",
        }
        if r.get("recorded_votes"):
            rec["recorded_votes"] = r["recorded_votes"]
        out.append(rec)
    out.sort(key=lambda r: r.get("intro_date") or "", reverse=True)

    if meta["has_councilmatic"]:
        note = (f"Merged from two sources: the Legistar Web API (historical, through "
                f"{meta['legistar_frozen_at']}) and DataMade's Chicago Councilmatic mirror "
                f"(current through {meta['councilmatic_latest']}), which covers the period "
                f"after Chicago's council left Legistar. Each record carries a `source`. "
                f"recorded_votes appears only on the rare bills with a recorded roll-call "
                f"split — most council actions pass by voice vote. sponsor_wards resolves "
                f"only when a sponsor's name exactly matches a manually-filled entry in "
                f"aldermen.json; empty means unresolved, not 'no sponsors'. "
                f"topic_relevant/topic_reason are automated tags (topic_tag_tier: derived) "
                f"— see topic_tagged_by ('llm' vs 'keyword_fallback').")
    else:
        note = (f"Sourced from the Legistar Web API, which is only current through "
                f"{meta['legistar_frozen_at']} (Chicago's council migrated to a new system "
                f"after that date — see DECISIONS.md). Councilmatic data was not available "
                f"this run, so records after that date are missing. sponsor_wards resolves "
                f"only when a sponsor's name exactly matches a manually-filled entry in "
                f"aldermen.json; empty means unresolved, not 'no sponsors'. "
                f"topic_relevant/topic_reason are automated tags (topic_tag_tier: derived) "
                f"— see topic_tagged_by ('llm' vs 'keyword_fallback').")

    return {
        "data_tier": "real",
        "topic_tag_tier": "derived",
        "note": note,
        "records": out,
    }, out
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m pytest pipeline/tests/test_aggregate_council.py -v`
Expected: PASS (both).

- [ ] **Step 5: Commit**

```bash
git add pipeline/aggregate.py pipeline/tests/test_aggregate_council.py
git commit -m "feat: merge Councilmatic into council_records with currency note"
```

---

### Task 8: `recorded_no_votes` in `build_aldermen_safety_record`

**Files:**
- Modify: `pipeline/aggregate.py` (rewrite `build_aldermen_safety_record`, lines ~600-632)
- Create: `pipeline/tests/test_aggregate_aldermen.py`

**Interfaces:**
- Consumes: council-record dicts from Task 7 (may carry `recorded_votes.no_voters`)
- Produces: each alderman entry gains `recorded_no_votes: int`; aldermen who only appear as no-voters (never sponsored) are still listed.

- [ ] **Step 1: Write the failing tests**

`pipeline/tests/test_aggregate_aldermen.py`:

```python
import aggregate


def test_recorded_no_votes_counted_and_nonsponsor_included():
    council_records = [{
        "matter_id": "O2025-1", "title": "t", "type": "ordinance", "status": "Passed",
        "intro_date": "2025-02-01", "url": "u", "topic_relevant": True,
        "sponsors": ["Sponsor, S"],
        "recorded_votes": {"no_voters": ["Dissenter, D"]},
    }]
    result = aggregate.build_aldermen_safety_record(council_records, {})
    by_name = {a["sponsor_name"]: a for a in result["aldermen"]}

    # Sponsor: 1 safety sponsorship, 0 recorded no-votes.
    assert by_name["Sponsor, S"]["safety_sponsorships"] == 1
    assert by_name["Sponsor, S"]["recorded_no_votes"] == 0

    # Dissenter never sponsored but must appear, with the no-vote counted.
    assert by_name["Dissenter, D"]["recorded_no_votes"] == 1
    assert by_name["Dissenter, D"]["safety_sponsorships"] == 0


def test_no_votes_ignored_when_topic_irrelevant():
    council_records = [{
        "matter_id": "O2025-2", "title": "t", "type": "ordinance", "status": "Passed",
        "intro_date": "2025-02-01", "url": "u", "topic_relevant": False,
        "sponsors": [], "recorded_votes": {"no_voters": ["Dissenter, D"]},
    }]
    result = aggregate.build_aldermen_safety_record(council_records, {})
    assert result["aldermen"] == []
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest pipeline/tests/test_aggregate_aldermen.py -v`
Expected: FAIL (no `recorded_no_votes` key; non-sponsor not included).

- [ ] **Step 3: Rewrite `build_aldermen_safety_record`**

Replace the function (lines ~600-632) with:

```python
def build_aldermen_safety_record(council_records, name_to_ward):
    by_sponsor = defaultdict(lambda: {"relevant_count": 0, "total_count": 0, "records": []})

    # Count recorded 'no' votes on topic-relevant matters, per alderman name.
    no_votes_by_name = defaultdict(int)
    for r in council_records:
        if r.get("topic_relevant") and r.get("recorded_votes"):
            for name in r["recorded_votes"].get("no_voters", []):
                no_votes_by_name[name] += 1

    for r in council_records:
        for sponsor in r["sponsors"]:
            d = by_sponsor[sponsor]
            d["total_count"] += 1
            if r["topic_relevant"]:
                d["relevant_count"] += 1
            d["records"].append({
                "matter_id": r["matter_id"], "title": r["title"], "type": r["type"],
                "status": r["status"], "intro_date": r["intro_date"],
                "topic_relevant": r["topic_relevant"], "url": r["url"],
            })

    # Aldermen who only ever appear as a recorded 'no' voter (never sponsored)
    # must still be listed — otherwise the honest signal we added is invisible.
    for name in no_votes_by_name:
        by_sponsor[name]

    out = []
    for sponsor, d in sorted(by_sponsor.items(),
                             key=lambda kv: (-kv[1]["relevant_count"],
                                             -no_votes_by_name.get(kv[0], 0))):
        out.append({
            "sponsor_name": sponsor,
            "ward": name_to_ward.get(sponsor.strip().lower()),
            "safety_sponsorships": d["relevant_count"],
            "total_matched_sponsorships": d["total_count"],
            "recorded_no_votes": no_votes_by_name.get(sponsor, 0),
            "records": d["records"],
            "data_tier": "derived",
        })
    return {
        "data_tier": "derived",
        "note": ("Aggregate of Chicago City Council sponsorships on matters tagged "
                 "topic_relevant (see council_records.json), plus recorded_no_votes: the "
                 "count of the rare recorded roll-call votes where this member voted 'no' "
                 "on a topic-relevant matter. Most council street-safety actions pass by "
                 "voice vote with no individual vote recorded, so recorded_no_votes is "
                 "near-zero for nearly everyone by design, not omission. ward is null until "
                 "sponsor_name exactly matches the manually-filled aldermen.json "
                 "(DECISIONS.md #8) — never auto-matched by fuzzy name similarity."),
        "aldermen": out,
    }
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m pytest pipeline/tests/test_aggregate_aldermen.py -v`
Expected: PASS (both).

- [ ] **Step 5: Commit**

```bash
git add pipeline/aggregate.py pipeline/tests/test_aggregate_aldermen.py
git commit -m "feat: add recorded_no_votes to the alderman safety record"
```

---

### Task 9: Fixtures for offline runs

**Files:**
- Modify: `pipeline/make_fixtures.py` (add `build_councilmatic_records`; wire into `main()`; update summary print)
- Create: `pipeline/tests/test_fixtures_councilmatic.py`

**Interfaces:**
- Consumes: existing module constants `SAFETY_TITLES`, `NON_SAFETY_TITLES`, `FIXTURE_SPONSORS`, and helper `rand_date` (all already in `make_fixtures.py`)
- Produces: `raw/councilmatic_records.json` under `--fixtures`

- [ ] **Step 1: Write the failing test**

`pipeline/tests/test_fixtures_councilmatic.py`:

```python
import random

import make_fixtures


def test_build_councilmatic_records_shape_and_one_contested():
    out = make_fixtures.build_councilmatic_records(random.Random(0))
    assert out["source"] == "councilmatic"
    assert out["covers_from"] == "2023-06-21"
    assert out["latest_action_date"] > "2023-06-21"
    assert len(out["records"]) >= 1
    assert all(r["source"] == "councilmatic" for r in out["records"])
    # Exactly the seeded contested record carries recorded_votes.
    with_votes = [r for r in out["records"] if "recorded_votes" in r]
    assert len(with_votes) == 1
    assert with_votes[0]["recorded_votes"]["no"] > 0
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest pipeline/tests/test_fixtures_councilmatic.py -v`
Expected: FAIL with `AttributeError: module 'make_fixtures' has no attribute 'build_councilmatic_records'`.

- [ ] **Step 3: Add the fixture builder**

In `pipeline/make_fixtures.py`, add after `build_council_records` (~line 255):

```python
def build_councilmatic_records(rng, n=8):
    """Synthetic post-2023 council records mirroring pull_councilmatic's output,
    so `run_all.py --fixtures` exercises the two-source merge and the
    recorded_votes path offline."""
    records = []
    for i in range(n):
        is_safety = rng.random() < 0.7
        title = rng.choice(SAFETY_TITLES if is_safety else NON_SAFETY_TITLES)
        sponsors = rng.sample(FIXTURE_SPONSORS, k=rng.randrange(1, 3))
        d = rand_date(rng, datetime(2023, 7, 1), datetime(2026, 6, 1))
        ident = f"O2025-{10000 + i}"
        records.append({
            "matter_id": ident,
            "title": title,
            "type": rng.choice(["ordinance", "resolution", "order"]),
            "status": rng.choice(["Passed", "Introduced", "Referred"]),
            "intro_date": d.strftime("%Y-%m-%dT%H:%M:%S"),
            "body": None,
            "sponsors": sponsors,
            "url": f"https://chicago.councilmatic.org/legislation/{ident}/",
            "source": "councilmatic",
        })
    # One record carries a contested split so the merge + accountability paths run.
    records[0]["recorded_votes"] = {
        "date": "2026-03-18", "yes": 30, "no": 18, "absent": 2,
        "no_voters": rng.sample(FIXTURE_SPONSORS, k=3), "result": "pass",
    }
    return {
        "source": "councilmatic",
        "covers_from": "2023-06-21",
        "latest_action_date": max(r["intro_date"] for r in records)[:10],
        "keywords": ["bike", "traffic safety"],
        "records": records,
    }
```

- [ ] **Step 4: Wire it into `main()`**

In `make_fixtures.main()`, after `council_records = build_council_records(rng)` (~line 301):

```python
    councilmatic_records = build_councilmatic_records(rng)
```

After `write_json(RAW_DIR / "council_records.json", council_records)` (~line 313):

```python
    write_json(RAW_DIR / "councilmatic_records.json", councilmatic_records)
```

Update the final summary print (~line 320) to include Councilmatic — change the `council_records` count fragment to also report:

```python
          f"{len(council_records['records'])} legistar + "
          f"{len(councilmatic_records['records'])} councilmatic council rows, "
```

(Match the surrounding f-string's existing punctuation; keep the rest of the line intact.)

- [ ] **Step 5: Run to verify it passes**

Run: `python -m pytest pipeline/tests/test_fixtures_councilmatic.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pipeline/make_fixtures.py pipeline/tests/test_fixtures_councilmatic.py
git commit -m "feat: add Councilmatic fixtures for offline pipeline runs"
```

---

### Task 10: Wire the puller into `run_all.py`

**Files:**
- Modify: `pipeline/run_all.py` (`LIVE_STAGES`, ~line 33; docstring stage list ~line 11)
- Create: `pipeline/tests/test_run_all_order.py`

**Interfaces:**
- Produces: `pull_councilmatic.py` runs after `pull_council_records.py` and before `classify_safety_topic.py`.

- [ ] **Step 1: Write the failing test**

`pipeline/tests/test_run_all_order.py`:

```python
import run_all


def _flat(stages):
    return [s[0] for s in stages]


def test_councilmatic_runs_after_council_records():
    live = _flat(run_all.LIVE_STAGES)
    assert "pull_councilmatic.py" in live
    assert live.index("pull_councilmatic.py") > live.index("pull_council_records.py")


def test_councilmatic_pulls_before_classify():
    # classify is a COMMON stage (runs after all LIVE stages), so ordering holds.
    assert "classify_safety_topic.py" in [s[0] for s in run_all.COMMON_STAGES]
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest pipeline/tests/test_run_all_order.py -v`
Expected: FAIL on the first assert (`pull_councilmatic.py` not in `LIVE_STAGES`).

- [ ] **Step 3: Edit `run_all.py`**

In `LIVE_STAGES`, change the line:

```python
    ["pull_ward_demographics.py"], ["pull_council_records.py"],
```

to:

```python
    ["pull_ward_demographics.py"], ["pull_council_records.py"], ["pull_councilmatic.py"],
```

In the module docstring's stage list (step 4), append to the `pull_council_records` line: `, pull_councilmatic (post-2023 council data via Councilmatic — see DECISIONS.md)`.

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest pipeline/tests/test_run_all_order.py -v`
Expected: PASS (both).

- [ ] **Step 5: Commit**

```bash
git add pipeline/run_all.py pipeline/tests/test_run_all_order.py
git commit -m "feat: run pull_councilmatic in the pipeline after pull_council_records"
```

---

### Task 11: Docs + full end-to-end verification

**Files:**
- Modify: `DECISIONS.md`, `SCHEMA.md`, `README.md`

- [ ] **Step 1: Full offline pipeline run (the real integration test)**

Run: `cd pipeline && python run_all.py --fixtures`
Expected: exits 0; final line `run_all: done — site/data is fresh; commit it to publish.`

- [ ] **Step 2: Assert the merged output is correct**

Run:
```bash
cd pipeline && python -c "import json; d=json.load(open('../site/data/council_records.json')); srcs={r.get('source') for r in d['records']}; print('sources:', srcs); print('note_has_current:', 'current through' in d['note']); print('votes:', sum('recorded_votes' in r for r in d['records']))"
```
Expected: `sources: {'legistar', 'councilmatic'}`, `note_has_current: True`, `votes: 1` (or more).

Run:
```bash
cd pipeline && python -c "import json; a=json.load(open('../site/data/aldermen_safety_record.json')); print('has_field:', all('recorded_no_votes' in x for x in a['aldermen'])); print('any_no:', any(x['recorded_no_votes'] for x in a['aldermen']))"
```
Expected: `has_field: True`, `any_no: True`.

- [ ] **Step 3: Run the whole test suite**

Run: `python -m pytest pipeline/tests -v`
Expected: all pass.

- [ ] **Step 4: Update `DECISIONS.md`**

Append a new decision entry (match the file's existing numbered/heading style) covering:
- **Source:** Chicago Councilmatic (DataMade) Datasette closes the frozen-Legistar (2023-06-21) gap; data current to the present.
- **Live SQL API over the 3.7 GB nightly dump** — volume is a few dozen keyword-filtered bills; dump documented as fallback only.
- **Two raw files + union helper**, not appending into one file — keeps each puller independently degradable.
- **Contested votes only; attendance dropped** — of 12,302 post-2023 vote events only ~1.4% had any 'no'; raw `absent` conflates committee non-membership, so a naive "voting record" or attendance metric would mislead. We surface the real split votes and a `recorded_no_votes` count instead.
- **Unverified upstream** — how Councilmatic's scraper reaches post-2023 data isn't fully pinned down; data is fresh and correct from the outside.

- [ ] **Step 5: Update `SCHEMA.md`**

- In the `council_records.json` record contract: add `source` (`"legistar" | "councilmatic"`) and the optional `recorded_votes` object (`date, yes, no, absent, no_voters[], result`), present only on bills with a recorded roll-call split.
- In the `aldermen_safety_record.json` contract: add `recorded_no_votes` (int) and note aldermen may appear solely as recorded no-voters.

- [ ] **Step 6: Update `README.md`**

- In the "Data sources & limitations" table, add a **Councilmatic** row (tier `real`; limitation: republished mirror of official council data, current post-2023, scraper mechanism unverified from outside).
- Update the Traffic-Crashes/Legistar-related council text so the "frozen at 2023-06-21" caveat notes the gap is now covered by Councilmatic for the post-2023 window.

- [ ] **Step 7: Commit**

```bash
git add DECISIONS.md SCHEMA.md README.md
git commit -m "docs: document Councilmatic source, contested votes, and dropped attendance"
```

- [ ] **Step 8 (optional, network): live end-to-end**

Run: `cd pipeline && python pull_councilmatic.py && python classify_safety_topic.py && python aggregate.py`
Then re-run the Step 2 assertions against the live-built `site/data/council_records.json`. Note: this overwrites `site/data/` with a mix of fixture (non-council) and live (council) data — **do not commit** that mixed state; a real refresh is the weekly `run_all.py` step. `git checkout site/data` afterward to discard.

---

## Self-Review

**Spec coverage:**
- Component 1 (`councilmatic.py` fetch helper) → Task 2. ✓
- Component 2 (`pull_councilmatic.py` bills + contested votes, non-fatal) → Tasks 3–4. ✓
- Component 3 (union helper; classify + aggregate switch reads; note flip) → Tasks 5, 6, 7. ✓
- Component 4 (accountability auto-refresh + `recorded_no_votes`) → Task 8. ✓
- Component 5 (config, run_all, fixtures, meta/SCHEMA, DECISIONS) → Tasks 1, 9, 10, 11. ✓
- Out-of-scope items (attendance, dump, committees, check_provenance) → none built; recorded in DECISIONS (Task 11). ✓

**Placeholder scan:** No TBD/TODO/"handle edge cases"/"similar to Task N". All code shown in full. `meta.json` needs no code change (its `council_records` entry already uses `len(council_records_list)`), so no task claims one — intentional, noted here.

**Type consistency:** `load_all_council_records(raw_dir) -> (records, meta)` used identically in Tasks 5/6/7. `recorded_votes` keys (`date, yes, no, absent, no_voters, result`) identical across `extract_recorded_votes` (Task 3), fixtures (Task 9), and aggregate tests (Tasks 7/8). `source` values `"legistar"`/`"councilmatic"` consistent throughout. `matter_id` is int (Legistar) or str (Councilmatic) everywhere; dedup key is `(source, matter_id)` in Task 5.

**One flagged consideration for the executor:** `build_council_records` skips records with no classification tag (`continue`). Under `--fixtures`, `classify_safety_topic.py` runs in `COMMON_STAGES` after fixtures are written, so Councilmatic fixture records DO get tagged — verified by Task 11 Step 2. If you run `aggregate.py` in isolation without a prior classify pass, Councilmatic records will be absent from the output; that's existing behavior, not a regression.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-11-councilmatic-council-data.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session with checkpoints for review.

Which approach?
