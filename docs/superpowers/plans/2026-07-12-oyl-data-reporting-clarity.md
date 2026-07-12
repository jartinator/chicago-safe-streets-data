# OYL Data-Reporting Clarity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the dashboard "On Your Left!", make every displayed number carry its full identity (what it counts, over what window, from which source, at what trust level, one tap from its explanation), unify the ward report into a single document, and wire in two newly-verified real data sources (eLMS meetings API, Ward Offices alderperson roster).

**Architecture:** Static site (vanilla JS pages rendering into `#app`, shared `window.BSD` runtime in `site/assets/js/common.js`) fed by a Python pipeline (`pipeline/*.py`) that writes versioned JSON into `site/data/`. New crash-metric computations live in one shared module (`pipeline/crash_metrics.py`) consumed by both the live aggregate path and an offline refresh script, so committed site data can be regenerated without a full live pull and without logic drift.

**Tech Stack:** Python 3 (requests, geopandas — pipeline), vanilla ES5-ish JS (browser + Node-testable pure functions), Node built-in test runner for `tests/ui/*.test.js`, pytest for `pipeline/tests/`.

## Global Constraints

- Brand is exactly **"On Your Left!"** — the exclamation point is required everywhere the name renders. Colloquial short form "OYL". Tagline (site header `<small>`): **"Chicago bike safety, on the record"**. `<title>` pattern: `{Page} — On Your Left!`.
- Data-quality tier visibility is a hard product constraint: every displayed number carries its tier badge; badges become tappable, never hover-only.
- Never fabricate data. New pulls fail soft (link-out / previous file preserved). Provisional/mock/stub labeling stays.
- Sponsor-name matching stays **exact-match-only** (no fuzzing) — a wrong match misattributes a real person's record.
- Copy decisions locked at checkpoint 1: "Talking Points" → **"Performance report"**; dooring finding title → **"Dooring: structurally undercounted"**; nav renames "Data Table" → **"Explore Data"**, "Open Data" → **"Downloads & Docs"**; findings page h1 → **"What the data shows"**; alderman labels → **"Current alderperson"**.
- Findings page: full swap (retire `painted-vs-protected` and `vehicle-types`; add protected-share, hit-and-run, KSI-trend).
- Sources + Downloads pages stay separate this round (incremental IA): anchors + cross-links, no merge.
- Every stat rendered gets a printed time window ("in the last 12 months", "since Sept 2017", "as of {date}").
- Commit after each task: `git add <files>; git commit -m "<type>: <what>"`. All commits end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Run `node --test tests/ui/` and `python -m pytest pipeline/tests -q` before every commit that touches the respective side. (Read one existing test file first and follow its conventions exactly.)
- Worktree root (all paths below relative to it): `C:\Users\jared\OneDrive\chicago-safe-streets-data\.claude\worktrees\data-reporting-clarity-d2db77`
- **OSM trails are merged into main (PR #12) and this branch is fast-forwarded onto it** — the trails layer is part of the base, not a conflict risk. Consequences threaded through this plan: (a) Task 8 folds the existing `osm_trails` entry in `sources.js` into the new 1-column card format with an `id="src-osm_trails"` anchor (use the id already present in SOURCES); (b) Task 9's Downloads table includes an `osm_trails.geojson` row — title "Off-street trails (OSM)", description "Named off-street trails (Lakefront, 606, Major Taylor…) from OpenStreetMap — volunteer-mapped, unverified.", tier `crowdsourced`; (c) Task 5's protected-share finding **excludes the `trail` facility category from numerator and denominator** and phrases its total as "on-street bikeway miles" — off-street trails now live in the separate OSM layer at crowdsourced tier and must never enter real-tier statistics; (d) `map.js`/`network.js`/`aggregate.py`/`config.py`/`run_all.py`/`make_fixtures.py` all changed in the base — read the current file before editing, don't work from pre-merge memory.
- **Phase 2 (Tasks 14–17, main routes)** implements the approved design in `docs/superpowers/specs/2026-07-12-main-routes-design.md` (in this worktree). Its three user-locked decisions are binding: a "line" = a named corridor end-to-end with facility grade shown along its length; the roster is hand-curated in checked-in config and auto-filled each run; never fabricate gap geometry. Grade order: off-street > protected > painted > none. Street lines and trail lines never blend tiers (CDOT/`derived` vs OSM/`crowdsourced`). Phase 2 depends on Task 2's `openModal` + tappable badges and lands after Phase 1.

---

### Task 1: Branding — "On Your Left!"

**Files:**
- Modify: `site/assets/js/common.js` (initPage header), all seven `site/*.html` `<title>`s, `README.md` (first heading/line), `SCHEMA.md` + `CONTRIBUTING.md` (title references only, if they say "Chicago Bike Safety")
- Test: `tests/ui/common-helpers.test.js` (extend)

**Interfaces:**
- Produces: header brand markup `<a class="brand" href="index.html">On Your Left!<small>Chicago bike safety, on the record</small></a>`. Later tasks assume this exact copy.

**Steps:**

- [ ] **Step 1:** In `common.js` `initPage()`, replace the brand line:

```js
`<a class="brand" href="index.html">On Your Left!<small>Chicago bike safety, on the record</small></a>` +
```

- [ ] **Step 2:** Update each `site/*.html` `<title>`: `index.html` → `Map — On Your Left!`, `network.html` → `Network — On Your Left!`, `findings.html` → `Findings — On Your Left!`, `table.html` → `Explore Data — On Your Left!`, `sources.html` → `Sources — On Your Left!`, `action.html` → `Take Action — On Your Left!`, `contributing.html` → `Downloads & Docs — On Your Left!`. Add to each `<head>`: `<meta name="description" content="On Your Left! — Chicago bike safety, on the record. Crash, infrastructure, and council accountability data by ward.">`
- [ ] **Step 3:** `README.md`: retitle to `# On Your Left! (OYL)` with first line "On Your Left! (OYL) — a Chicago bike-safety evidence dashboard. *Chicago bike safety, on the record.*" Keep all existing content; adjust only name references. Same treatment for stray "Chicago Bike Safety" occurrences in SCHEMA.md/CONTRIBUTING.md headings (grep for them; content otherwise untouched). Keep "evidence layer, not a collection layer" language in the footer/README — it is positioning, not the tagline.
- [ ] **Step 4:** Extend `tests/ui/common-helpers.test.js` with a test asserting the exported module still works; brand is DOM-only so just verify no export regressions (`esc`, `fmt`, `trendHTML`, `scoreColor`, `money` behave as before).
- [ ] **Step 5:** `node --test tests/ui/` → all pass. Commit: `feat: rebrand to "On Your Left!" with tagline`.

---

### Task 2: UI primitives — modal, tappable badges, shared CSS classes, nav renames

**Files:**
- Modify: `site/assets/js/common.js`, `site/assets/css/style.css`
- Test: `tests/ui/common-helpers.test.js`

**Interfaces:**
- Produces (later tasks rely on these exact names):
  - `BSD.openModal({ title, bodyHTML })` → shows a shared `<dialog class="modal">`; returns the dialog element. Close button `aria-label="Close"`; focus returns to the invoking element on close.
  - `BSD.badgeHTML(tier)` now returns `<button type="button" class="badge tier-{t}" data-tier="{t}">{label}</button>` (label: `stub` renders "no data yet", others render the tier word). A **delegated** document-level click handler on `.badge[data-tier]` opens the tier-explainer modal.
  - `BSD.TIER_PLAIN` = `{ real: "from official records", proxy: "a related signal, not a direct measure", derived: "calculated by us from real data", mock: "fake demo data — not real reports", crowdsourced: "volunteer-reported, unverified", stub: "no data yet — a placeholder for a future source" }`.
  - CSS classes: `.card-heading` (flex h3+badge row), `.fine-print` (muted 0.8rem, top border, 0.6rem padding-top), `.kv-list` (line-height 1.8 stat stacks), `.section-gap` (margin-top 2rem), `.card-link` (anchor-card reset), `.table-stack` (≤600px: thead hidden, rows as stacked bordered blocks), `dialog.modal` + `.modal-head` + `.modal-body`, `.report`, `.report-head`, `.report-kicker`, `.report-meta`, `.report-section`, `.report-foot`, `.linklike` (button styled as link).
- Consumes: existing `TIER_INFO`, `esc`.

**Steps:**

- [ ] **Step 1 (test first):** In `tests/ui/common-helpers.test.js`, add assertions: `badgeHTML("proxy")` contains `<button`, `data-tier="proxy"`, and class `tier-proxy`; `badgeHTML("bogus")` falls back to stub with label "no data yet"; module exports `TIER_PLAIN` with all six tiers. Run → FAIL.
- [ ] **Step 2:** Implement in `common.js`:

```js
const TIER_PLAIN = {
  real: "from official records",
  proxy: "a related signal, not a direct measure",
  derived: "calculated by us from real data",
  mock: "fake demo data — not real reports",
  crowdsourced: "volunteer-reported, unverified",
  stub: "no data yet — a placeholder for a future source",
};

function badgeHTML(tier) {
  const t = TIER_INFO[tier] ? tier : "stub";
  return `<button type="button" class="badge tier-${t}" data-tier="${t}">` +
    `${t === "stub" ? "no data yet" : t}</button>`;
}

let _modal = null;
function openModal({ title, bodyHTML }) {
  const opener = document.activeElement;
  if (!_modal) {
    _modal = document.createElement("dialog");
    _modal.className = "modal";
    document.body.appendChild(_modal);
  }
  _modal.innerHTML =
    `<div class="modal-head"><strong>${esc(title)}</strong>` +
    `<button type="button" class="btn modal-close" aria-label="Close">×</button></div>` +
    `<div class="modal-body">${bodyHTML}</div>`;
  _modal.querySelector(".modal-close").addEventListener("click", () => _modal.close());
  _modal.addEventListener("close", function onClose() {
    _modal.removeEventListener("close", onClose);
    if (opener && opener.focus) opener.focus();
  });
  _modal.showModal();
  return _modal;
}
```

  Delegated badge handler (inside the existing browser-only section / `initPage`):

```js
document.addEventListener("click", e => {
  const b = e.target.closest && e.target.closest(".badge[data-tier]");
  if (!b) return;
  const t = b.dataset.tier;
  openModal({
    title: `Data quality: ${t === "stub" ? "no data yet" : t}`,
    bodyHTML: `<p><strong>${esc(TIER_PLAIN[t])}.</strong></p><p>${esc(TIER_INFO[t])}</p>` +
      `<p><a href="sources.html">See where every dataset comes from →</a></p>`,
  });
});
```

  Export `TIER_PLAIN` and `openModal` on `window.BSD` and in `module.exports` (`TIER_PLAIN` only for Node — `openModal` is DOM-bound).
- [ ] **Step 3:** Add the CSS block to `style.css` (values from the design spec):

```css
.card-heading { margin-top: 0; display: flex; align-items: center; justify-content: space-between; gap: .5rem; flex-wrap: wrap; }
.fine-print { color: var(--ink-soft); font-size: .8rem; margin-top: .6rem; padding-top: .6rem; border-top: 1px solid var(--line); }
.kv-list { line-height: 1.8; }
.section-gap { margin-top: 2rem; }
.card-link { text-decoration: none; color: inherit; display: block; }
.linklike { background: none; border: none; padding: 0; color: var(--accent); cursor: pointer; font: inherit; text-decoration: underline; }
dialog.modal { border: 1px solid var(--line); border-radius: 12px; padding: 0; max-width: 560px; width: calc(100vw - 2rem); }
dialog.modal::backdrop { background: rgba(16,32,43,.55); }
.modal-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: .8rem 1.2rem; border-bottom: 1px solid var(--line); }
.modal-body { padding: 1rem 1.2rem; max-height: 70vh; overflow: auto; }
.report { background: var(--card, #fff); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; margin: 1rem 0; }
.report-head { background: #10202b; color: #fff; padding: .9rem 1.2rem; }
.report-kicker { font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; opacity: .8; display: block; }
.report-meta { font-size: .82rem; opacity: .85; margin: .2rem 0 0; }
.report-section { padding: 1rem 1.2rem; border-top: 1px solid var(--line); }
.report-foot { padding: .7rem 1.2rem; border-top: 1px solid var(--line); background: #f3f6f9; font-size: .85rem; }
@media (max-width: 600px) {
  .table-stack thead { display: none; }
  .table-stack tr { display: block; border: 1px solid var(--line); border-radius: 8px; margin: .5rem 0; }
  .table-stack td { display: block; border: none; }
}
```

  Also make sure `.badge` still looks like a badge as a `<button>`: add `button.badge { font: inherit; cursor: pointer; }` and match existing badge padding/border-radius (read the current `.badge` rule and extend it rather than duplicating).
- [ ] **Step 4:** `common.js` NAV renames: `["table.html", "Explore Data"]`, `["contributing.html", "Downloads & Docs"]` (others unchanged). Footer: append legend line `Every number is labeled — real · proxy · derived · mock · crowdsourced — tap any label to see what it means.`
- [ ] **Step 5:** `node --test tests/ui/` → PASS (fix `tests/ui/table-datasets.test.js` or others if they assert on old badge markup). Commit: `feat: shared modal primitive, tappable badges, reusable layout classes`.

---

### Task 3: Pipeline — current alderpersons from Ward Offices (`htai-wnw4`)

**Files:**
- Create: `pipeline/pull_aldermen.py`
- Modify: `pipeline/config.py`, `pipeline/run_all.py`, `DECISIONS.md`
- Test: `pipeline/tests/test_pull_aldermen.py`

**Interfaces:**
- Consumes: `socrata.fetch_all(dataset_id, ...)` (generator of dict rows), `socrata.write_json(path, obj)`, `config.SITE_DATA_DIR`.
- Produces: `site/data/aldermen.json` with shape (UI tasks depend on these keys):

```json
{
  "as_of": "2026-07-12T…+00:00",
  "source": "Chicago Data Portal — Ward Offices (htai-wnw4)",
  "data_tier": "real",
  "note": "Current alderperson roster from the city's Ward Offices dataset; refreshed each pipeline run. Vacant seats appear as null.",
  "lookup_url": "https://www.chicago.gov/city/en/about/wards.html",
  "wards": [{ "ward": "1", "alderman": "La Spata, Daniel", "email": "Ward01@cityofchicago.org", "phone": "…", "website": "…" }, …]
}
```

**Steps:**

- [ ] **Step 1 (test first):** `pipeline/tests/test_pull_aldermen.py` — pure-function test of `build_aldermen(rows)`:

```python
from pull_aldermen import build_aldermen

def test_build_aldermen_fills_all_50_wards_and_normalizes():
    rows = [
        {"ward": "1", "alderman": " La Spata, Daniel ", "email": "Ward01@cityofchicago.org",
         "ward_phone": "312-555-0001", "website": {"url": "https://www.the1stward.com"}},
        {"ward": "3", "alderman": "Dowell, Pat", "email": "Ward03@cityofchicago.org"},
    ]
    wards = build_aldermen(rows)
    assert len(wards) == 50
    w1 = next(w for w in wards if w["ward"] == "1")
    assert w1["alderman"] == "La Spata, Daniel"          # trimmed
    assert w1["website"] == "https://www.the1stward.com" # Socrata url-type unwrapped
    w2 = next(w for w in wards if w["ward"] == "2")
    assert w2["alderman"] is None                         # missing ward -> nulls, never invented

def test_validate_roster_rejects_sparse_pull():
    from pull_aldermen import roster_is_valid
    assert not roster_is_valid([{"ward": str(i), "alderman": None} for i in range(1, 51)])
    assert roster_is_valid([{"ward": str(i), "alderman": f"Name{i}, Test"} for i in range(1, 51)])
```

  Run `python -m pytest pipeline/tests/test_pull_aldermen.py -q` → FAIL (module missing). Check `pipeline/tests/conftest.py` for how imports resolve and follow it.
- [ ] **Step 2:** Add to `config.py` near the other dataset IDs:

```python
# Ward Offices — the city's official roster of current alderpersons (name, email,
# phone, website per ward). Same Socrata portal as crashes. Ingesting the official
# roster is NOT the "never auto-generate" guessing DECISIONS.md #8 forbids — that
# rule was about inferring names. Verified live 2026-07-12.
WARD_OFFICES_DATASET = "htai-wnw4"
ALDERMAN_LOOKUP_URL = "https://www.chicago.gov/city/en/about/wards.html"
```

- [ ] **Step 3:** Create `pipeline/pull_aldermen.py`:

```python
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
```

  Before finalizing, verify the live field names once: `python -c "import requests; print(requests.get('https://data.cityofchicago.org/resource/htai-wnw4.json?$limit=1').json())"` — adjust `_clean` mapping if `website` isn't a dict or `ward_phone` differs.
- [ ] **Step 4:** `run_all.py` LIVE_STAGES: add `["pull_aldermen.py"]` right after `["pull_wards.py"]`. Update the stage list in the module docstring. `aggregate.py`'s "create aldermen.json only if missing" block (near line 946) stays — it is now the fixtures/offline fallback; update its inline note text to say the live path fills this via pull_aldermen.py.
- [ ] **Step 5:** Amend `DECISIONS.md` #8: append (don't rewrite history) a dated note: "2026-07-12: the never-auto-generate rule was about *guessing* names. The city's own Ward Offices dataset (htai-wnw4) is the authoritative roster and is now ingested by pull_aldermen.py; exact-match-only sponsor resolution unchanged; failed pulls keep the previous file." Run `python -m pytest pipeline/tests -q` → PASS. Commit: `feat: pull current alderpersons from Ward Offices dataset`.

---

### Task 4: Pipeline — real hearings from the eLMS public API

**Files:**
- Modify: `pipeline/pull_hearings.py`, `pipeline/config.py`, `DECISIONS.md`
- Test: `pipeline/tests/test_pull_hearings.py` (create)

**Interfaces:**
- Consumes: `config.ELMS_MEETINGS_URL`, `ELMS_COMMITTEES_OF_INTEREST`, `socrata.write_json`, `requests`.
- Produces: `site/data/hearings.json` (via RAW_DIR + aggregate passthrough `build_hearings()` — verify it copies raw/hearings.json through unchanged) with meetings shape the UI depends on:

```json
{ "as_of": "…", "structured_data_available": true, "source": "elms_api",
  "note": "Meetings from the City Clerk eLMS public API (api.chicityclerkelms.chicago.gov), refreshed each pipeline run; best-effort — verify against the official calendar before attending.",
  "committees": [{ "committee": "Committee on Transportation and Public Way",
    "calendar_url": "https://chicityclerkelms.chicago.gov/Meetings?body=…",
    "meetings": [{ "date": "2026-07-14T13:00:00", "status": "Scheduled & Published",
      "location": "City Hall, Room 201-A", "agenda_url": "https://…pdf" , "notice_url": null,
      "comment": "Written Public Comment deadline is July 10, 2026 12:30 PM at committeeontransportationandpublicway@cityofchicago.org" }] }] }
```

**Steps:**

- [ ] **Step 1 (test first):** `pipeline/tests/test_pull_hearings.py` testing the pure transform `normalize_meetings(api_rows, today)`:

```python
from pull_hearings import normalize_meetings

API_ROWS = [
    {"meetingId": 1, "status": "Scheduled & Published", "date": "2026-07-14T13:00:00",
     "location": "City Hall, Room 201-A",
     "comment": "Written Public Comment deadline is July 10, 2026 12:30 PM at ctpw@cityofchicago.org",
     "files": [{"path": "https://x/agenda.pdf", "attachmentType": "Agenda"},
                {"path": "https://x/notice.pdf", "attachmentType": "Notice"}]},
    {"meetingId": 2, "status": "Cancelled", "date": "2026-07-20T10:00:00", "files": []},
    {"meetingId": 3, "status": "Scheduled", "date": "2026-01-05T10:00:00", "files": []},  # past
    {"meetingId": 4, "status": "Scheduled", "date": "not-a-date", "files": []},           # invalid
]

def test_normalize_keeps_future_scheduled_only_and_extracts_files():
    out = normalize_meetings(API_ROWS, today="2026-07-12")
    assert len(out) == 1
    m = out[0]
    assert m["date"] == "2026-07-14T13:00:00"
    assert m["agenda_url"] == "https://x/agenda.pdf"
    assert m["notice_url"] == "https://x/notice.pdf"
    assert "Written Public Comment" in m["comment"]

def test_normalize_empty_input():
    assert normalize_meetings([], today="2026-07-12") == []
```

  Run → FAIL.
- [ ] **Step 2:** `config.py`: replace the "no working endpoint" comment block on ELMS with the corrected finding and add:

```python
# eLMS public API — CONFIRMED WORKING 2026-07-12 (earlier research guessed plural/
# prefixed paths; the real endpoints are singular nouns at the API root, e.g.
# GET https://api.chicityclerkelms.chicago.gov/meeting?filter=body eq '<committee>'
# &sort=date desc&limit=50). Undocumented and unversioned — treat as best-effort;
# pull_hearings.py keeps the link-out fallback shape on any failure.
ELMS_API_URL = "https://api.chicityclerkelms.chicago.gov"
```

- [ ] **Step 3:** Rewrite `pull_hearings.py`'s fetch path (keep the module fail-soft; keep the link-out fallback exactly as today when anything fails):

```python
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
        # The API wraps rows; accept either a bare list or a {"data": [...]}-style
        # envelope — inspect the live response once and normalize here.
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
```

  `main()` calls `fetch_committee_meetings` per committee, normalizes with `today = datetime.now(timezone.utc).date().isoformat()`, sets `structured_data_available = True` only if at least one committee returned a non-None row list (empty list of *validated* future meetings still counts as structured — "no meetings scheduled" is honest data), adds `"source": "elms_api"` and the note from the Interfaces block above; on all-None keeps today's exact fallback output (old note text, `structured_data_available: False`). Update the module docstring (the "no public endpoint" story is now historical).
- [ ] **Step 4:** Verify `aggregate.py build_hearings()` (≈line 777) passes raw/hearings.json through without reshaping; if it filters keys, add the new `source` key through. Run `python -m pytest pipeline/tests -q` → PASS.
- [ ] **Step 5:** One live smoke run: `python pipeline/pull_hearings.py` then inspect `pipeline/raw/hearings.json` — confirm real meetings appear with dates/status/agenda URLs (committee calendars may legitimately be empty in July recess; `structured_data_available` should still be true). Amend `DECISIONS.md` #14 (and the #17 cross-reference) with a dated correction note: the API exists at singular-noun endpoints; guesses in the original research were plural/prefixed. Commit: `feat: pull real committee meetings from the eLMS public API`.

---

### Task 5: Pipeline — crash metrics module (monthly series, KSI, hit-and-run, protected share) + findings rewrite

**Files:**
- Create: `pipeline/crash_metrics.py`, `pipeline/tests/test_crash_metrics.py`
- Modify: `pipeline/aggregate.py` (build_findings, build_ward_safety_index, main), `SCHEMA.md`, `pipeline/config.py` (CONTRACT_VERSION → "1.7")

**Interfaces:**
- Produces `pipeline/crash_metrics.py` (pure, no geopandas/network — trivially testable), consumed by aggregate.py AND Task 6's refresh script:

```python
# A crash tuple is a dict: {"date": "YYYY-MM-DD", "severity": <enum str>,
#   "hit_and_run": bool, "dooring": bool, "ward": str|None}
INJURY_SEVERITIES = ("fatal", "incapacitating", "non_incapacitating")
KSI_SEVERITIES = ("fatal", "incapacitating")

def monthly_counts(tuples, start_month, end_month) -> list  # contiguous [{month:"YYYY-MM", crashes, injury_crashes, ksi, fatal}]
def per_ward_monthly(tuples, start_month, end_month) -> dict  # {ward: same list shape}
def window_counts(tuples, anchor_date) -> dict  # {"recent_12mo": {...crashes/injury_crashes/ksi/fatal}, "prior_12mo": {...}, "window_end": iso}
def hit_and_run_shares(tuples) -> dict  # {"total": n, "hit_and_run": n, "share_pct": float, "injury_total": n, "injury_hit_and_run": n, "injury_share_pct": float}
def protected_share(by_category_miles) -> dict  # {"protected_mi": x, "buffered_mi": y, "total_mi": z, "protected_pct": p, "protected_plus_buffered_pct": q}
```

- Produces new site-data fields (UI tasks and SCHEMA.md depend on these names):
  - `site/data/ward_safety_index.json` per-ward: existing fields plus `"windows": <window_counts output>` and `"monthly": <per_ward_monthly list>`.
  - New file `site/data/citywide_trend.json`: `{"data_tier": "real", "window_end": "YYYY-MM-DD", "note": "Monthly counts of police-reported cyclist crashes citywide since Sept 2017; ksi = crashes whose worst injury was fatal or incapacitating (\"killed or seriously injured\"). Recent months are provisional — records get amended.", "months": [...] }`.
  - Rewritten `site/data/findings.json` (see Step 4).

**Steps:**

- [ ] **Step 1 (test first):** `pipeline/tests/test_crash_metrics.py` covering: monthly buckets are contiguous (a month with no crashes appears with zeros); ksi counts fatal+incapacitating only; `window_counts` matches `crash_trend`-style 365-day windows anchored at `anchor_date`; `hit_and_run_shares` percentages round to 1 decimal; `protected_share({"protected": 68.74, "buffered": 65.0, "painted": 200.0, "trail": 112.17})` returns `protected_pct == 15.4`. Write concrete fixture tuples (≥8 crashes across ≥3 months, mixed severities/flags). Run → FAIL.
- [ ] **Step 2:** Implement `crash_metrics.py`. Month iteration:

```python
def _month_range(start_month, end_month):
    y, m = int(start_month[:4]), int(start_month[5:7])
    ey, em = int(end_month[:4]), int(end_month[5:7])
    while (y, m) <= (ey, em):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1
```

  Each bucket: `{"month": m, "crashes": 0, "injury_crashes": 0, "ksi": 0, "fatal": 0}`; increment per tuple by `date[:7]`; `injury_crashes` counts severity in `INJURY_SEVERITIES`; `window_counts` reuses the same 365/730-day boundaries as `aggregate.crash_trend` (copy the boundary logic; don't import aggregate — that module imports geopandas). Run tests → PASS.
- [ ] **Step 3:** Wire into `aggregate.py`: in `build_ward_safety_index`, build crash tuples once — `{"date": c["crash_date"][:10], "severity": severity(c), "hit_and_run": flag(c, "hit_and_run_i"), "dooring": flag(c, "dooring_i"), "ward": c.get("ward")}` (verify the raw flag key names against the existing `flag()` call sites in this file) — and attach `windows` + `monthly` (start month from `CRASH_START_DATE`, end month = latest crash date) to each ward record. In `main()`, write `citywide_trend.json` from the same tuples and add it to meta.json's sources list (`id: "citywide_trend", tier: "real"`). Extend `pipeline/tests/test_aggregate_*`-style coverage only if an existing test file already exercises build_ward_safety_index; otherwise the crash_metrics tests carry this.
- [ ] **Step 4:** Rewrite `build_findings` (full swap, checkpoint-1 approved). Remove the `painted-vs-protected` and `vehicle-types` blocks. Keep `top-corridors` (append to its caveat: "Per-km rates inflate short segments — Kinzie's rate rides on very few km.") and `ward-concentration` (add `"wards": [w for w, _ in top_wards]` so the UI can link each ward; append "since Sept 2017" to its description). Retitle dooring:

```python
findings.append({
    "id": "dooring-undercount",
    "title": "Dooring: structurally undercounted",
    "stat": f"{doorings}+",
    "description": (f"{doorings} crashes since Sept 2017 carry a dooring flag. Dooring is "
                    "structurally excluded from 'reportable' crash records unless damage/injury "
                    "thresholds are met, so the real number is higher than any count on this site."),
    "caveat": "A floor, not a full count.",
    "map_state": {"screen": "map", "layers": ["crashes"], "filters": {"dooring": True}},
    "data_tier": "real",
})
```

  Add three new findings (all from `crash_metrics` + `citywide_miles_by_category(routes_gj)`):

```python
ps = protected_share(citywide_miles_by_category(routes_gj))
findings.append({
    "id": "protected-share",
    "title": "How much of the network protects riders",
    "stat": f"{ps['protected_pct']:.0f}%",
    "description": (f"Only {ps['protected_pct']:.0f}% of Chicago's {ps['total_mi']:.0f} bikeway miles "
                    f"are physically protected lanes ({ps['protected_mi']:.0f} mi); counting buffered "
                    f"lanes brings it to {ps['protected_plus_buffered_pct']:.0f}%. The rest is paint, "
                    "sharrows, greenways, and trails."),
    "caveat": f"Share of current network mileage as of {as_of_date}; protected = barrier/curb-protected on-street lanes.",
    "map_state": {"screen": "map", "layers": ["infrastructure"], "filters": {}},
    "data_tier": "real",
})

hr = hit_and_run_shares(tuples)
findings.append({
    "id": "hit-and-run",
    "title": "How often the driver leaves",
    "stat": f"{hr['share_pct']:.0f}%",
    "description": (f"In {hr['share_pct']:.0f}% of police-reported cyclist crashes since Sept 2017 "
                    f"({hr['hit_and_run']} of {hr['total']}), the driver left the scene — "
                    f"{hr['injury_share_pct']:.0f}% when the cyclist was injured."),
    "caveat": "Share of reported crashes; unreported crashes are not counted.",
    "map_state": {"screen": "table", "layers": [], "filters": {}},
    "data_tier": "real",
})

ksi = window_counts(tuples, anchor_date)   # anchor = latest crash date
findings.append({
    "id": "ksi-trend",
    "title": "Cyclists killed or seriously injured",
    "stat": str(ksi["recent_12mo"]["ksi"]),
    "description": (f"{ksi['recent_12mo']['ksi']} cyclists were killed or seriously injured "
                    f"(\"incapacitating\" in police records) in the 12 months through "
                    f"{ksi['window_end']}, vs {ksi['prior_12mo']['ksi']} the prior 12 months. "
                    "Vision Zero's goal is zero."),
    "caveat": "Counts, not rates — ridership growth is not netted out. Recent months are provisional.",
    "map_state": {"screen": "map", "layers": ["crashes"], "filters": {}},
    "data_tier": "real",
})
```

  Order findings: ksi-trend, protected-share, top-corridors, hit-and-run, ward-concentration, dooring-undercount.
- [ ] **Step 5:** `config.py` `CONTRACT_VERSION = "1.7"`. Document in `SCHEMA.md`: the new `windows`/`monthly` fields, `citywide_trend.json`, the new/removed findings ids, the aldermen.json new shape (Task 3), hearings meetings shape (Task 4), and KSI/injury severity definitions (`KSI = fatal + incapacitating`). Run `python -m pytest pipeline/tests -q` → PASS. Commit: `feat: crash metrics module, monthly trend series, advocacy-grounded findings`.

---

### Task 6: Pipeline — offline refresh of committed reporting data

**Files:**
- Create: `pipeline/refresh_reporting.py`
- Test: `pipeline/tests/test_refresh_reporting.py`

**Interfaces:**
- Consumes: `crash_metrics.*` (Task 5), committed `site/data/crashes_cyclist.geojson`, `site/data/bikeway_mileage_series.json`, `site/data/ward_safety_index.json`, `site/data/meta.json`.
- Produces: refreshed `site/data/findings.json`, `site/data/citywide_trend.json`, and `windows`/`monthly` fields merged into `site/data/ward_safety_index.json` — **derived from the already-committed socrata pull**, so provenance stays honest without a multi-hour live run. (This exists so the PR ships with real new findings/charts; the weekly `run_all.py` remains the canonical path.)

**Steps:**

- [ ] **Step 1 (test first):** `test_refresh_reporting.py` — test `tuples_from_geojson(gj)`: given a 2-feature FeatureCollection with properties `{date: "2026-07-01T10:00:00", injury_severity: "incapacitating", hit_and_run: true, dooring: false, ward: "1"}`, returns crash tuples with `date == "2026-07-01"`, severity/flags/ward passed through. And `test_refresh_refuses_non_socrata_provenance`: `guard_provenance({"provenance": "fixtures"})` raises SystemExit (fixture data must never be re-stamped as reporting truth — see the provenance-stamp history in git). Run → FAIL.
- [ ] **Step 2:** Implement. `tuples_from_geojson` maps feature properties (geojson uses the *renamed* keys: `date`, `injury_severity`, `hit_and_run`, `dooring`, `ward`). Main flow: guard provenance from `meta.json` (`provenance != "socrata"` → exit with message); build tuples; recompute findings via the same functions Task 5 put in `crash_metrics` (protected share comes from the **latest entry** of `bikeway_mileage_series.json`'s `series[].by_category`; corridors/ward-concentration findings are recomputed from committed `corridors.json` + `wards.geojson` with the same code paths — extract the findings assembly from `aggregate.build_findings` into a shared helper `build_findings_core(tuples, per_km_inputs, corridors, ward_counts, as_of_date)` in `crash_metrics.py` if aggregate's version can't run without RAW_DIR; both callers use it); write `citywide_trend.json`; merge `windows`/`monthly` into the existing `ward_safety_index.json` records in place (do not recompute danger scores — those need population/geometry inputs this script doesn't have); update `meta.json` `contract_version` and append the `citywide_trend` source entry if absent. Print a summary diff (finding ids before/after).
- [ ] **Step 3:** `python -m pytest pipeline/tests -q` → PASS. Run it for real: `python pipeline/refresh_reporting.py` → inspect `site/data/findings.json` (6 findings, new ids present, dooring retitled) and `site/data/citywide_trend.json` (~107 months). Commit code and the refreshed `site/data/*.json` separately: `feat: offline reporting refresh from committed crash data` then `data: refresh findings, citywide trend, ward windows from committed 2026-07-10 pull`.

---

### Task 7: UI — trend chart + trailing-window + .ics helpers

**Files:**
- Modify: `site/assets/js/common.js`
- Test: `tests/ui/common-helpers.test.js` (extend)

**Interfaces:**
- Produces on `window.BSD` **and** `module.exports` (all pure string/array functions, Node-testable):
  - `BSD.rollingSums(months, key, window)` → `[{month, value}]` — trailing-`window` sum of `key` over `[{month, crashes, injury_crashes, ksi, fatal}]`; entries before a full window are omitted.
  - `BSD.trendChartSVG(points, opts)` → SVG string. `points` = `[{month, value}]`; `opts` = `{ width=560, height=120, label, median=null, dots=[] }` (`dots` = `[{month, count, kind:"fatal"|"ksi"}]` rendered as circles on the baseline). Renders: polyline of values, first/last month text labels, current-value dot + numeric label, optional horizontal dashed median line labeled "city median". No axes/gridlines (sparkline-plus per design). Colors via `var(--accent)` / `var(--sev-incap)` CSS vars.
  - `BSD.icsForEvent({title, startISO, location, url, description})` → RFC-5545 string (VCALENDAR/VEVENT, DTSTART in floating local time `YYYYMMDDTHHMMSS`, LF-normalized to CRLF, UID from title+start hash).
  - `BSD.downloadICS(filename, icsString)` → Blob download, `type: "text/calendar"` (same pattern as `downloadCSV`).

**Steps:**

- [ ] **Step 1 (test first):** Extend `tests/ui/common-helpers.test.js`:

```js
const months = [];
for (let i = 0; i < 24; i++) {
  months.push({ month: `20${24 + Math.floor(i / 12)}-${String((i % 12) + 1).padStart(2, "0")}`,
    crashes: 10, injury_crashes: 3, ksi: 1, fatal: 0 });
}
// rollingSums: 24 input months, window 12 -> 13 points, each value 120
// trendChartSVG: returns a string starting "<svg", containing "polyline", both month labels, and the final value "120"
// icsForEvent: contains "BEGIN:VEVENT", "DTSTART:20260714T130000", escaped commas in location, CRLF line endings
```

  Run → FAIL.
- [ ] **Step 2:** Implement the four functions in `common.js` (pure section, exported for Node). `trendChartSVG` core:

```js
function trendChartSVG(points, opts) {
  const o = Object.assign({ width: 560, height: 120, label: "", median: null, dots: [] }, opts || {});
  if (!points || points.length < 2) return "";
  const pad = { l: 8, r: 46, t: 14, b: 18 };
  const w = o.width - pad.l - pad.r, h = o.height - pad.t - pad.b;
  const vals = points.map(p => p.value);
  const max = Math.max(...vals, o.median || 0) || 1;
  const x = i => pad.l + (i / (points.length - 1)) * w;
  const y = v => pad.t + h - (v / max) * h;
  const line = points.map((p, i) => `${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const last = points[points.length - 1];
  let svg = `<svg viewBox="0 0 ${o.width} ${o.height}" role="img" aria-label="${esc(o.label)}" xmlns="http://www.w3.org/2000/svg">`;
  if (o.median != null) {
    svg += `<line x1="${pad.l}" x2="${pad.l + w}" y1="${y(o.median)}" y2="${y(o.median)}" stroke="var(--ink-soft)" stroke-dasharray="4 3" stroke-width="1"/>` +
      `<text x="${pad.l + w}" y="${y(o.median) - 4}" text-anchor="end" font-size="10" fill="var(--ink-soft)">city median</text>`;
  }
  svg += `<polyline points="${line}" fill="none" stroke="var(--accent)" stroke-width="2"/>`;
  (o.dots || []).forEach(d => {
    const i = points.findIndex(p => p.month === d.month);
    if (i === -1) return;
    svg += `<circle cx="${x(i)}" cy="${pad.t + h}" r="3" fill="var(--sev-incap)"><title>${esc(String(d.count))} ${esc(d.kind)}</title></circle>`;
  });
  svg += `<circle cx="${x(points.length - 1)}" cy="${y(last.value)}" r="3" fill="var(--accent)"/>` +
    `<text x="${x(points.length - 1) + 6}" y="${y(last.value) + 4}" font-size="12" font-weight="700" fill="var(--accent)">${esc(String(last.value))}</text>` +
    `<text x="${pad.l}" y="${o.height - 4}" font-size="10" fill="var(--ink-soft)">${esc(points[0].month)}</text>` +
    `<text x="${pad.l + w}" y="${o.height - 4}" text-anchor="end" font-size="10" fill="var(--ink-soft)">${esc(last.month)}</text></svg>`;
  return svg;
}
```

  `icsForEvent`: build lines array, join with `\r\n`; escape `,`/`;`/`\n` in text fields per RFC 5545; `DTSTART` = `startISO.replace(/[-:]/g, "").slice(0, 15)`.
- [ ] **Step 3:** `node --test tests/ui/` → PASS. Commit: `feat: trend chart, rolling-window, and calendar (.ics) helpers`.

---

### Task 8: UI — Sources page, 1-column with anchors

**Files:**
- Modify: `site/assets/js/sources.js`, `site/assets/css/style.css` (source-card rules)

**Interfaces:**
- Produces: every source card gets `id="src-{source.id}"` (e.g. `src-crashes`, `src-ward_safety_index`, `src-sr311`, `src-menu_spending`, `src-hearings`, `src-aldermen`) — Tasks 9–11 deep-link these. Chip TOC at top.
- Consumes: `BSD.badgeHTML` (tappable), `.notice` styles.

**Steps:**

- [ ] **Step 1:** Restructure render: drop the `cards-grid` wrapper (cards stack full-width). Per card:
  - `<section class="card source-card" id="src-{id}">`
  - header row: `<h2>` + tier badge (use `.card-heading`), then a one-line muted fact row: `{origin} · updated {cadence}{records ? ` · ${records} records` : ""}`.
  - body: description paragraph; then a `<dl class="source-facts">` for Raw dataset links.
  - limitations rendered as `<div class="notice">**Known limitations:** …</div>` (visual callout — currently they're typographically identical to descriptions).
  - CSS: `.source-card { scroll-margin-top: 4.5rem; }`; `.source-facts` 2-col grid ≥760px, stacked below.
- [ ] **Step 2:** Chip TOC under the h1: one link per source (`<a class="btn" href="#src-{id}">{short name}</a>` in a flex-wrap row).
- [ ] **Step 3:** Content updates in `SOURCES`:
  - `hearings` entry: origin → "City Clerk eLMS public API (api.chicityclerkelms.chicago.gov)"; description/limitations updated to say structured meetings are pulled each run with a link-out fallback, undocumented API treated as best-effort.
  - Add `aldermen` entry: name "Current Alderpersons (Ward Offices)", tier `real`, origin "Chicago Data Portal (Socrata)", cadence "weekly pipeline run", description "Official roster of current alderpersons — name, email, phone, and website per ward.", limitations "Vacant seats appear as null; the roster is the city's own and may lag a resignation by days.", link `https://data.cityofchicago.org/d/htai-wnw4`, metaId `null`.
  - Add `citywide_trend` entry: name "Citywide Crash Trend (monthly)", tier `real`, origin "Computed from Traffic Crashes", description "Monthly citywide counts of cyclist crashes, injuries, and killed-or-seriously-injured, Sept 2017 to present — the series behind the trend charts.", limitations "Counts, not rates; recent months provisional.", metaId `citywide_trend`.
  - `sources.js` "Dooring… UNDERCOUNTED" phrasing: keep (it already says undercounted; the "number that is too low" phrasing lives in findings.json, fixed in Task 5).
- [ ] **Step 4:** Remove the page-top `directional` notice (`BSD.noticeHTML("directional")`) — it belongs on density-visual pages, not the catalog. Load the page (Task 12 verification covers browser pass; here run a quick smoke: `npx serve site` or python http.server + check `sources.html#src-crashes` scrolls to the card). Commit: `feat: sources page — one column, anchors, chip TOC, callout limitations`.

---

### Task 9: UI — Downloads & Docs (contributing.html) table redesign

**Files:**
- Modify: `site/assets/js/contributing.js`

**Interfaces:**
- Consumes: `sources.html#src-{id}` anchors (Task 8), `BSD.openModal`, `.table-stack` (Task 2).
- Produces: FILES array entries gain `{ title, description, sourceId, calc? }`.

**Steps:**

- [ ] **Step 1:** Replace the FILES array with rich entries. Plain-language names/descriptions (from the communication panel, verbatim):

| file | title | description | sourceId |
|---|---|---|---|
| crashes_cyclist.geojson | Cyclist crashes | Every police-reported crash involving a cyclist since Sept 2017, with location, severity, and dooring/hit-and-run flags. | crashes |
| bike_routes.geojson | Bike lane inventory | The city's current bike infrastructure: protected, buffered, and painted lanes, greenways, trails. | bike_routes |
| wards.geojson | Ward boundaries & crash totals | Official 2023 ward boundaries with each ward's crash counts attached. | wards |
| corridors.json | Most dangerous streets | Streets ranked by cyclist crashes per kilometer of bikeway. | crashes |
| intersections.json | Crash hotspot intersections | The intersections where the most cyclist crashes cluster. | crashes |
| findings.json | Headline findings | The stats behind the Findings page, each with its caveat and map link. | crashes |
| meta.json | Build info | When this data was generated, from where, and how many records per source. | — |
| ward_311.json | 311 bike complaints by ward | Bike-related service requests residents filed with the city, totaled per ward. | sr311 |
| cameras.json | Camera violations | Speed and red-light violations at fixed cameras — a rough signal of aggressive driving. | cameras |
| obstructions_mock.geojson | Blocked-lane reports (demo only) | Fake sample data showing what real obstruction reports would look like — not real reports. | obstructions |
| planned_routes.geojson | Planned bike routes (empty) | Placeholder for future CDOT planned-route data; no structured feed exists yet. | planned_routes |
| mellow_routes.geojson | Community low-stress routes | Quiet streets tagged by riders on the volunteer-run Mellow Bike Map. | mellow_map |
| ward_safety_index.json | Ward danger scores | Each ward's 0–100 danger score (relative to other wards), with the rates behind it and 12-month trend. | ward_safety_index |
| council_records.json | City Council legislation | Street- and bike-safety ordinances and resolutions, with sponsors and status. | council_records |
| aldermen_safety_record.json | Alderperson safety records | How often each alderperson sponsored bike/traffic-safety legislation. | aldermen_safety_record |
| aldermen.json | Current alderpersons | Name and contact info for each ward's current alderperson, from the city's official roster. | aldermen |
| hearings.json | Committee hearing calendar | Upcoming transportation-committee meetings, or a link to the official calendar. | hearings |
| menu_spending.json | Ward discretionary spending | What each ward spent its infrastructure "menu" money on, with a bike/traffic-calming subtotal. | menu_spending |
| citywide_trend.json | Citywide crash trend | Monthly citywide cyclist crash, injury, and KSI counts since Sept 2017. | citywide_trend |

  (Check `sources.js` ids and use the exact ones — e.g. the mellow entry's id is `mellow_map` in SOURCES; align them.)
  For derived/proxy tiers, add `calc`: one plain sentence, e.g. ward_safety_index: `"Average of the ward's percentile ranks on crashes per 10k residents and crashes per bikeway mile — every input is in this file's row."`; aldermen_safety_record: `"Counts council records whose sponsor name exactly matches the ward's alderperson."`; ward_311/cameras/menu_spending: one sentence on what the proxy measures and its bias (reuse sources.js limitations, first clause).
- [ ] **Step 2:** New table columns `Dataset | Tier | Source | Download`. Dataset cell: `<strong>{title}</strong><div class="muted">{description}</div>` plus, when `calc` exists, `<button class="linklike" data-calc="{i}">How it's calculated</button>` opening `BSD.openModal({title: title, bodyHTML: "<p>"+esc(calc)+"</p><p><a href='sources.html#src-"+sourceId+"'>Full source detail →</a></p>"})`. Source cell: `<a href="sources.html#src-{sourceId}">{short source name}</a>` (or "—" for meta.json). Download cell: existing button + `<div><code>{filename}</code></div>`. Add class `table-stack` to the table.
- [ ] **Step 3:** Page h1 → "Downloads & Docs"; intro sentence keeps the open-source/open-data framing. Smoke-test in browser at ≤600px width (rows stack as cards). Commit: `feat: downloads table — plain-language names, source links, calc explainers`.

---

### Task 10: UI — Explore Data (table.html) clarity

**Files:**
- Modify: `site/assets/js/table.js`

**Interfaces:**
- Consumes: `BSD.openModal`, `.linklike` (Task 2); `sources.html#src-*` anchors (Task 8).

**Steps:**

- [ ] **Step 1:** Heading: `Non-Map Data Table` → `Explore the data`.
- [ ] **Step 2 (crashes tab):** Replace the two floating notices with a collapsed explainer directly above the table:

```html
<details class="fine-print"><summary>How to read this table</summary>
  <p><strong>Dooring†</strong>: structurally undercounted — dooring is excluded from "reportable"
  crash records unless damage/injury thresholds are met; treat "yes" counts as a floor.</p>
  <p><strong>Severity</strong>: as recorded by responding officers; recent months are provisional.</p>
  <p>Counts are raw — not adjusted for how many people ride each street, so busy corridors look
  worse than dangerous quiet ones.</p>
</details>
```

  Add the dagger to the Dooring column header label (`Dooring†`); clicking the header still sorts, so put the explainer reference in the `<details>` only (no per-header popover needed once the details block names the columns).
- [ ] **Step 3 (safety-index tab):** Replace the raw `data.note` dump with: badge row (already there) + `<details class="fine-print"><summary>About this score</summary><p>The danger score is the average of each ward's percentile ranks on crashes per 10k residents and crashes per bikeway mile — 0–100, higher = more dangerous relative to other wards. It compares wards to each other; it is not an absolute risk measure. <a href="sources.html#src-ward_safety_index">Full source detail →</a></p></details>`. Column header "Danger score" gets title text "0–100 vs other wards — see 'About this score'".
- [ ] **Step 4 (council tab):** Same `<details>` treatment for its `data.note`; the `SOURCE_TITLE` tooltip content moves into the details block ("**Source**: which pull produced the record — legistar rows end 2023-06-21 (system migration); councilmatic rows are current."); no_voters stay in the cell but append visibly when present (`title` alone is invisible on mobile): render `voteTd.textContent = row.vote` plus, when `no_voters.length`, a second muted line `no: {names}`.
- [ ] **Step 5:** `node --test tests/ui/` (table-datasets tests must still pass — pure functions unchanged). Browser smoke on all three tabs. Commit: `feat: explore-data tables explain themselves`.

---

### Task 11: UI — Take Action ward report (the centerpiece)

**Files:**
- Modify: `site/assets/js/action.js`
- Test: `tests/ui/action-model.test.js` (extend)

**Interfaces:**
- Consumes: `BSD.openModal`, `BSD.rollingSums`, `BSD.trendChartSVG`, `BSD.icsForEvent`, `BSD.downloadICS`, `.report*` CSS (Task 2/7); data fields `ward_safety_index.wards[].windows/monthly` (Task 5/6), `aldermen.json` real names (Task 3), `hearings.json` meetings (Task 4), `council_records.json` records with `sponsor_wards` + `intro_date` + `status`.
- Produces: pure functions (Node-exported, tested): `getUpcomingForWard(hearingsData, councilData, aldermanName, ward, today)` → `{ meetings: [...], introduced: [...] }` where `introduced` = records whose `sponsor_wards` includes the ward OR whose sponsors include `aldermanName` exactly, `status` in `{"Introduced", "Referred"}`, `intro_date` within 180 days of `today`, max 5, newest first.

**Steps:**

- [ ] **Step 1 (test first):** Extend `tests/ui/action-model.test.js` for `getUpcomingForWard`: matches by sponsor_wards, matches by exact alderman name, excludes old/passed records, caps at 5, empty-safe on null data. Run → FAIL. Implement in the pure section of action.js. → PASS.
- [ ] **Step 2 — page order:** In `render()`: (1) h1 "Take Action" + one-line intro; (2) `<h2>Get your ward's performance report</h2>` + ward picker; (3) ward report renders directly below the picker; (4) "See a problem? Report it directly" — 311/BLU as a compact 2-up `cards-grid` with one-line descriptions (use `.card-link`); (5) citywide "Upcoming committee hearings" card last, retitled `Upcoming committee hearings (citywide)`; (6) existing closing line. Replace `removeWardScopedCards` with a single `#ward-report` node swapped in place.
- [ ] **Step 3 — report container:** `renderWardReport(ward)` builds:

```html
<section class="report" id="ward-report">
  <header class="report-head">
    <span class="report-kicker">Performance report</span>
    <h2 style="margin:.1rem 0">Ward {N}</h2>
    <p class="report-meta">{Current alderperson: {name} · {email}  |  or link "Find your alderperson →" when null}
      · Crash data Sep 2017 – {meta window_end} · report built {meta.generated_at date}</p>
  </header>
  <div class="report-section">…Crashes & complaints…</div>
  <div class="report-section">…Coming up in Ward {N}…</div>
  <div class="report-section">…Safety scorecard…</div>
  <div class="report-section">…Alderperson record…</div>
  <div class="report-section">…Menu-fund spending…</div>
  <footer class="report-foot">
    <button class="linklike" id="ward-provenance">Where does this data come from?</button>
  </footer>
</section>
```

  Sections use `<h3 class="card-heading">{title} {badge}</h3>` (badge right-aligned via the flex class). The alderperson appears **only** in the header (remove it from the old talking-points body and from the alderman-record card body; the record section keeps sponsorship counts/records).
- [ ] **Step 4 — Crashes & complaints section (old Talking Points, renamed):**
  - Headline: `Cyclist crashes: <span class="stat">{windows.recent_12mo.crashes}</span> in the last 12 months` + `BSD.trendHTML(entry.crash_trend)` inline; muted second line `{cyclist_crashes} total since Sept 2017`. Fallback when `windows` absent: all-time count labeled `since Sept 2017` (never an unlabeled number).
  - Chart (first element of the section, above the numbers): `BSD.trendChartSVG(BSD.rollingSums(entry.monthly, "crashes", 12), { label: "Ward {N} cyclist crashes, trailing 12 months", median: <city median of latest trailing-12 across all wards, computed from safetyIndexData>, dots: <months where monthly.fatal>0 or monthly.ksi>0, kind "serious/fatal"> })`; render only when `entry.monthly` exists.
  - Injuries/fatalities: `Serious injuries (12 mo): {windows.recent_12mo.ksi} · Deaths (12 mo): {windows.recent_12mo.fatal}` with fallback to all-time wardData values labeled `since Sept 2017`.
  - 311 line unchanged content-wise but window-labeled: `311 bike complaints: {n} (all requests on record) {proxy badge}`.
  - **Delete** the `Citywide context` worst-corridor block and the `Density band` line (checkpoint-1 item 10 + jargon sweep).
- [ ] **Step 5 — Coming up in Ward {N} section:** From `getUpcomingForWard`. Meetings list: `{Mon DD} · {committee short name} · <a agenda_url>Agenda (PDF)</a> · <button class="btn">Add to calendar</button>`; when `comment` present render it as a fine-print line (it carries the written-comment deadline + committee email — display verbatim, don't parse). The .ics button calls `BSD.downloadICS("{committee}-{date}.ics", BSD.icsForEvent({title: committee + " — City Council", startISO: m.date, location: m.location, url: agenda_url || calendar_url, description: m.comment || ""}))`. Introduced list: `{date} · <a url>{title}</a> · {status}` under a sub-heading `Recently introduced by {alderman name}`. When both lists are empty: `Nothing scheduled for the safety committees right now — <a calendar_url>check the official calendar</a>.` When hearings data is link-out-only (`structured_data_available === false`), show the committee links exactly as the current card does.
- [ ] **Step 6 — Scorecard / record / menu sections:** Reuse existing builders' inner HTML, converted from standalone cards to `.report-section` divs: strip their per-card fine-print notes (`safetyIndexData.note`, `menuSpendingData.note`, COVERAGE_NOTICE, aldermen note) — all move into the modal (Step 7). Danger score line gains plain gloss: `Danger score: {score} / 100 <span class="muted">(vs other wards — higher is worse)</span>` and keeps rank line. "Alderman record" heading → `Alderperson record`.
- [ ] **Step 7 — provenance modal:** `#ward-provenance` opens `BSD.openModal` titled `Ward {N} report — where the data comes from`, body = a `<dl>` with one entry per stat group (spec content, adjust numbers dynamically):
  - **Cyclist crashes / injuries / deaths** — real · from official records. Chicago Police crash reports via the Chicago Data Portal. Recent months are provisional; dooring is structurally undercounted. Window: 12 months ending {window_end}. → `sources.html#src-crashes`
  - **Danger score** — derived · calculated by us. Formula: average of this ward's percentile ranks on crashes per 10k residents ({crashes_per_10k_pop}) and crashes per bikeway mile ({crashes_per_bikeway_mile}). A relative ranking across wards, not absolute risk. → `sources.html#src-ward_safety_index`
  - **311 bike complaints** — proxy · a related signal. Counts who complains, not conditions; biased toward wards with engaged 311 users. → `sources.html#src-sr311`
  - **Coming up / meetings** — real · City Clerk eLMS public API, best-effort weekly pull; verify against the official calendar. → `sources.html#src-hearings`
  - **Current alderperson** — real · city Ward Offices roster, as of {aldermen.as_of date}. → `sources.html#src-aldermen`
  - **Alderperson record** — derived · counts council records whose sponsor name exactly matches this ward's alderperson; coverage: Legistar through 2023-06-21, Councilmatic since. → `sources.html#src-aldermen_safety_record`
  - **Menu-fund spending** — proxy · Ward Wise volunteer project structuring the city's PDF reports; not independently verified. → `sources.html#src-menu_spending`
  - Footer line: `Check the math yourself: <a href="data/ward_safety_index.json" download>download ward_safety_index.json</a> — every input above is in this ward's row.`
- [ ] **Step 8:** Intro copy under the h2: `Pick your ward for local crash trends, what's coming up at City Hall, and your alderperson's record.` Keep URL `?ward=` state behavior. `node --test tests/ui/` → PASS; browser walkthrough `action.html?ward=1` (report coherent, modal opens/closes with focus return, .ics downloads, null-alderperson fallback works by testing a vacant ward if any). Commit: `feat: unified ward performance report with real calendar and provenance modal`.

---

### Task 12: UI — Findings page (What the data shows)

**Files:**
- Modify: `site/assets/js/findings.js`

**Interfaces:**
- Consumes: `site/data/findings.json` new ids (Task 5/6), `site/data/citywide_trend.json`, `BSD.rollingSums`, `BSD.trendChartSVG`, tappable badges.

**Steps:**

- [ ] **Step 1:** h1 → `What the data shows`; intro sentence: `Headline numbers and patterns worth exploring — each links to the view behind it.`
- [ ] **Step 2:** Load `citywide_trend.json` (catch → null). On the `ksi-trend` finding card, render `BSD.trendChartSVG(BSD.rollingSums(trend.months, "ksi", 12), { label: "Cyclists killed or seriously injured, trailing 12 months", width: 560, height: 140 })` between stat and description; skip silently when data absent.
- [ ] **Step 3:** `ward-concentration` card: when the finding has a `wards` array, append a line of links `Ward 27 → action.html?ward=27` etc. (`Get this ward's report →` pattern).
- [ ] **Step 4:** Replace the two page-top notices with one collapsed `<details class="fine-print"><summary>How to read these numbers</summary>` combining the directional + normalization text in the plainer voice: `These are patterns worth investigating, not statistical proof. Counts are raw — busy corridors look worse than dangerous quiet ones because no public ridership data exists to divide by.` Footer of the page keeps the generated-at/sources line; fix its hardcoded colors to `var(--line)` / `var(--ink-soft)`.
- [ ] **Step 5:** Browser smoke (cards render for every finding id present, including old data files without `wards`). Commit: `feat: findings page — KSI trend chart, ward links, plain reading guide`.

---

### Task 13: Docs sweep + full verification + PR prep

**Files:**
- Modify: `README.md` (feature list mentions), `DECISIONS.md` (verify Task 3/4 amendments read coherently), `docs/` screenshots optional
- No new code.

**Steps:**

- [ ] **Step 1:** `python -m pytest pipeline/tests -q` → all pass. `node --test tests/ui/` → all pass.
- [ ] **Step 2:** Browser verification pass (serve `site/`): every page renders with no console errors; nav shows renamed items on all pages; badges open the explainer modal everywhere (map/network pages included — they use `badgeHTML` too, so spot-check them even though their layouts are out of scope); `sources.html#src-crashes` deep-link scrolls; downloads table stacks at mobile width; `action.html?ward=27` full report + modal + .ics; findings chart renders. Screenshot before/after for the PR (action page + findings + sources), save under `docs/img/` following the existing screenshot convention from PR #10.
- [ ] **Step 3:** Confirm `git status` clean of strays; review `git log --oneline main..HEAD` reads as a coherent story.
- [ ] **Step 4:** Push branch and open the PR with `gh pr create` — title `Data-reporting clarity: OYL rebrand, unified ward report, real calendar + alderperson data`. Body: summary by theme (identity-of-every-number principle; verified eLMS + Ward Offices unlocks; findings swap rationale — including WHY painted-vs-protected was retired; screenshots; note that `refresh_reporting.py` regenerated committed reporting JSON from the existing 2026-07-10 socrata pull, and the next weekly `run_all.py` takes over from there). End body with the standard generated-with-Claude-Code footer.

---

## Phase 2 — Main routes ("rail vs bus" map hierarchy)

Implements `docs/superpowers/specs/2026-07-12-main-routes-design.md` — read it in full before
starting any Phase 2 task; it carries the roster, grade taxonomy, assignment rules, and UI spec.
The spec's §11 "open knobs" (loop bbox, stroke weights, OSM name-matching tokens, 31st/Belmont
visual cut) are implementer's judgment — decide by looking at rendered output and record the
choice in the commit message.

### Task 14: Pipeline — roster config + `build_main_routes`

**Files:**
- Create: `data/main_routes.json` (checked-in roster config — spec §5 verbatim: 5 trail lines, 13 street lines, `loop` first with its bbox clip), `pipeline/tests/test_aggregate_main_routes.py`
- Modify: `pipeline/aggregate.py` (new builder + main() wiring + meta entry), `pipeline/config.py` (`CONTRACT_VERSION = "1.8"`), `SCHEMA.md`

**Interfaces:**
- Consumes: `routes_gj` (CDOT, on-street), raw `osm_trails.geojson` (one feature per named trail, `name`, `facility_category: "trail"`, `data_tier: "crowdsourced"`), roster config.
- Produces `site/data/main_routes.geojson`: member features `{segment_id, line_id, grade, facility_category, length_m, crashes_within_30m (street only), data_tier}` + FC-level `lines` list `{id, name, termini, source, data_tier ("derived" street / "crowdsourced" trail), miles_total, miles_by_grade, pct_protected (street only), crashes_total (street only), no_data (trail lines when osm_trails is a stub)}`.
- Grade mapping (spec §4): `trail→offstreet`, `protected→protected`, `buffered|painted|greenway→painted`, `sharrow|other→none`.

**Steps (TDD, same cadence as Tasks 3–5):** write `test_aggregate_main_routes.py` first covering: first-match-wins (loop bbox claims downtown WASHINGTON before `jackson-washington`), street-name suffix normalization (`RANDOLPH ST` → `RANDOLPH`), grade mapping incl. greenway→painted and sharrow→none, pct_protected math over member miles only (gaps are holes, never fabricated), trail matching by normalized name token, stub-trails → `no_data: true` lines with zero features, `crashes_total` absent on trail lines. Then implement `build_main_routes(routes_gj, osm_trails_gj, roster)` mirroring existing builder patterns; wire into `main()` (aggregate-only — `run_all.py` untouched); add `main_routes` meta source entry (tier `derived`); works under `--fixtures` (extend fixture corridors with a roster street if none match). Document both file contracts in SCHEMA.md; bump CONTRACT_VERSION to 1.8. `pytest` green → commit `feat: main-routes builder — curated line roster with facility grades`.

### Task 15: UI — geographic map (index.html) main routes layer

**Files:**
- Create: `site/assets/js/main-routes-model.js` (pure helpers: grade→style, completion-bar segment widths, roster ordering — `window.BSDMainRoutes` + `module.exports`, same pattern as `map-model.js`), `tests/ui/main-routes-model.test.js`
- Modify: `site/assets/js/map.js`, `site/index.html` (script tag), `site/assets/css/style.css` (completion-bar rules)

**Steps:** model tests first, then: add default-on `mainroutes` layer (label "Main routes", `derived` badge); flip `infrastructure` and the full `trails` layer to default-off (keep their URL-param behavior; update the default `layers` string — roster trails stay visible inside `mainroutes`, so the trails-on-by-default decision from PR #12 is preserved in spirit); render members grouped by line — white 8px casing under 4.5px grade-colored stroke, `none` grade dashed; line click → detail panel using `.card-heading` + tappable badge: name + termini, stacked completion bar (miles_by_grade in grade colors) with printed "{pct}% protected", crashes along line (street lines, real badge) or length + crowdsourced notice (trail lines), "Where does this come from?" → `BSD.openModal` linking `sources.html#src-main_routes`; roster side-panel section listing every line (name + mini completion bar + pct, click → fitBounds + panel); stub trail lines greyed with stub badge (mirror `_mellowStub` handling). `node --test` green + browser smoke → commit `feat: main-routes layer with line report cards on the map`.

### Task 16: UI — network view (network.html) demotion

**Files:**
- Modify: `site/assets/js/network.js` (+ `network-model.js` if helpers fit there), extend `tests/ui/network-model.test.js`

**Steps:** roster lines keep the heavy metro treatment (casing + line + stations, grade colors along the line); non-roster segments drop to a 1.5px muted `#cbd5e1` background network with no stations/labels below `LABEL_MIN_ZOOM`; existing `?corridor=` deep links keep working — map line clicks onto the corridor mechanism (add `?line=` only if it falls out cheaply); roster OSM trails get heavy treatment + label. Tests green + browser smoke at multiple zooms → commit `feat: metro view — main routes heavy, local network demoted`.

### Task 17: Main-routes docs, cross-links, verification

**Files:**
- Modify: `site/assets/js/sources.js`, `site/assets/js/contributing.js`, `pipeline/aggregate.py` (protected-share finding map_state), `README.md`, `DECISIONS.md`

**Steps:** add `main_routes` source card (tier `derived`, origin "Computed from CDOT Bike Routes + OSM trails roster", limitation verbatim from spec §8: "the roster is editorial: we chose which corridors count as main routes; segment grades and mileage are computed from source data each run") with `id="src-main_routes"`; Downloads table rows for `main_routes.geojson` + the roster config; point the `protected-share` finding's `map_state` at `{screen: "map", layers: ["mainroutes"]}` and append "See the main routes →" to its card link text; README data-sources row; DECISIONS.md entry recording the curated-roster decision and rail/bus rationale; re-run `refresh_reporting.py` if the finding copy changed; full verification pass (both test suites, browser walkthrough of map + network + findings cross-link). Commit `feat: main-routes provenance, docs, and findings cross-link`.

---

## Self-review notes (already applied)

- Task 5/6 share `crash_metrics.py` so the offline refresh can't drift from the live path; the refresh script refuses non-socrata provenance (guards the known fixtures-mislabeling failure mode).
- Every UI task that shows a stat states its fallback when new data fields are absent (old data files, fixture builds) — no unlabeled numbers in any state.
- Interfaces double-checked: `rollingSums`/`trendChartSVG`/`icsForEvent`/`openModal`/`TIER_PLAIN` names are used identically in Tasks 7, 9, 11, 12; `src-{id}` anchor ids in Tasks 8, 9, 10, 11; `windows`/`monthly` field names in Tasks 5, 6, 11.
- Out of scope, deliberately: Sources+Downloads page merge (incremental IA chosen), per-ward 311 trailing windows (future pipeline follow-up), eLMS `/matter` "pending before committee" pull (noted as future work in DECISIONS amendment). Map/network layout is NO LONGER out of scope — it is Phase 2 (Tasks 14–17), per the approved main-routes handoff.
