"""Guardrail: fail if the committed site/data is a synthetic fixtures build.

    python check_provenance.py

PR #3 once regenerated site/data with `make_fixtures.py` and committed the
result, silently replacing the real Socrata pull with placeholder data. This
check exists so that can't reach `main` again: `make_fixtures.py` stamps
raw/PROVENANCE = "fixtures", which aggregate.py records as meta.json's
top-level `provenance`, so a fixtures build is detectable from meta.json alone.

Exit codes:
  0  meta.json is a real build (provenance == "socrata")
  1  fixtures build, or meta.json missing/invalid

Per-source `provenance: "fixtures"` flags (e.g. the ward-accountability layer
before its first live pull) are reported as warnings, not failures — the tier
badges already surface them in the UI and each is a non-fatal pipeline stage.
Run this locally as part of the weekly-refresh review, and it also runs in CI
on every PR and on push to main.
"""
import json
import sys
from pathlib import Path

META_PATH = Path(__file__).resolve().parent.parent / "site" / "data" / "meta.json"


def main():
    if not META_PATH.exists():
        sys.exit(f"FAIL: {META_PATH} does not exist")
    try:
        meta = json.loads(META_PATH.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: {META_PATH} is not valid JSON: {e}")

    provenance = meta.get("provenance")
    if provenance != "socrata":
        sys.exit(
            f"FAIL: site/data/meta.json provenance is {provenance!r}, expected "
            "'socrata'. This looks like a synthetic fixtures build "
            "(run_all.py --fixtures) — do not commit it to main. Regenerate with "
            "a live pull: `python pipeline/run_all.py`."
        )

    fixture_sources = [s.get("id") for s in meta.get("sources", [])
                       if s.get("provenance") == "fixtures"]
    if fixture_sources:
        print("WARNING: these sources are still synthetic fixtures pending a "
              "live pull: " + ", ".join(fixture_sources))

    print("OK: site/data/meta.json provenance is 'socrata'.")


if __name__ == "__main__":
    main()
