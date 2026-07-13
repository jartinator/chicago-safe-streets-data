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

No build. Serve `site/` statically and browse:

- `.claude/launch.json` defines a `site` config (`python -m http.server 8741
  --directory site`) for the Browser pane's preview_start.
- Pages are `?`-param addressable: `action.html?ward=28`, `ward.html?ward=28`.
- The ward one-pager has Brief / Plain language toggle buttons — check both.

Gotchas:

- `site/data/*.json` is committed; local regeneration dirties the tree —
  intentional only for deliberate data commits (weekly refresh is the normal
  path, see DECISIONS.md #23).
- `hearings.json` meetings are date-filtered against *today*; stale committed
  data can render "nothing scheduled" honestly.
- Browser-pane `screenshot` sometimes times out on these pages; the
  accessibility tree (`read_page`) and small `javascript_exec` text dumps are
  reliable evidence.
