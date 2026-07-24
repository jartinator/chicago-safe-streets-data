---
name: verify
description: How to run and verify this project end-to-end — pipeline scripts plus the static site in a browser.
---

# Verifying changes in this repo

Two surfaces: the Python pipeline (scripts under `pipeline/`) and the static
site (`site/`, vanilla JS, no build step).

## Pipeline

Run the touched module directly — every `pull_*.py` is a standalone script
writing to `pipeline/raw/` (gitignored):

```
cd pipeline
python pull_hearings.py          # example; prints a one-line summary
python pull_agenda_items.py      # consumes raw/hearings.json
```

To regenerate one published `site/data/*.json` without a full (slow, live)
`run_all.py`, call the matching `build_*` function in `aggregate.py` from a
snippet and write with `socrata.write_json`. Full test suites:

```
python -m pytest pipeline/tests -q          # from repo root
for f in tests/ui/*.test.js; do node "$f"; done
```

## Site

No build. Serve `site/` statically and drive it with **Playwright**:

**Do not use the in-app Browser pane** (`preview_start`, `mcp__Claude_Browser__*`)
on this repo. Opening a browser preview here crashes the desktop app's GPU
process 3–5 seconds later and kills the whole app — reproduced 3 times on
2026-07-23, evidence in `C:\Users\jared\projects\claude-crash-evidence`.
Playwright runs in its own process, so a browser crash can't take the app down.

```
pip install playwright && python -m playwright install chromium   # one time
python -m http.server 8741 --directory site &                     # serve
```

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto("http://localhost:8741/ward.html?ward=28")
    print(page.inner_text("body")[:2000])   # text evidence
    page.screenshot(path="/tmp/ward28.png", full_page=True)
```

- Pages are `?`-param addressable: `action.html?ward=28`, `ward.html?ward=28`.
- The ward one-pager has Brief / Plain language toggle buttons — check both.

Gotchas:

- `site/data/*.json` is committed; local regeneration dirties the tree —
  intentional only for deliberate data commits (weekly refresh is the normal
  path, see DECISIONS.md #23).
- `hearings.json` meetings are date-filtered against *today*; stale committed
  data can render "nothing scheduled" honestly.
- Playwright's `page.inner_text(...)` dumps are the cheapest reliable evidence;
  screenshots are for visual/layout changes only. (The old Browser-pane
  `screenshot` timeouts noted here were an early symptom of the GPU crash.)
