"""Guardrail: fail if the committed site/data is a synthetic fixtures build.

    python check_provenance.py

PR #3 once regenerated site/data with `make_fixtures.py` and committed the
result, silently replacing the real Socrata pull with placeholder data. This
check exists so that can't reach `main` again: `make_fixtures.py` stamps
raw/PROVENANCE = "fixtures", which aggregate.py records as meta.json's
top-level `provenance`, so a fixtures build is detectable from meta.json alone.

Also checks site/api/v1/index.json (the agent-first static API, written by
emit_api.py) for the same class of problem: its `_meta` envelope must be
present, coherent, and not stale — a fixtures-built or stale API must never
be committed either. The API check is skipped (not failed) when
site/api/v1/index.json doesn't exist yet, since it's optional until first
published.

Exit codes:
  0  meta.json is a real build (provenance == "socrata"), and site/api/v1 is
     either absent or coherent with meta.json
  1  fixtures build, meta.json missing/invalid, or site/api/v1 present but
     stale/fixtures-built/invalid

Per-source `provenance: "fixtures"` flags (e.g. the ward-accountability layer
before its first live pull) are reported as warnings, not failures — the tier
badges already surface them in the UI and each is a non-fatal pipeline stage.
Run this locally as part of the weekly-refresh review, and it also runs in CI
on every PR and on push to main.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
META_PATH = REPO_ROOT / "site" / "data" / "meta.json"
API_INDEX_PATH = REPO_ROOT / "site" / "api" / "v1" / "index.json"


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

    if not API_INDEX_PATH.exists():
        print(f"note: {API_INDEX_PATH} not present — agent API not yet "
              "published; skipping API coherence check.")
        return

    try:
        api_index = json.loads(API_INDEX_PATH.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: {API_INDEX_PATH} is not valid JSON: {e}")

    api_meta = api_index.get("_meta", {})
    if api_meta.get("provenance") != "socrata":
        sys.exit(
            f"FAIL: {API_INDEX_PATH} _meta.provenance is "
            f"{api_meta.get('provenance')!r}, expected 'socrata'. This looks "
            "like a fixtures-built API — do not commit; regenerate with "
            "`python pipeline/emit_api.py` after a live pull."
        )
    if api_meta.get("generated_at") != meta.get("generated_at"):
        sys.exit(
            f"FAIL: {API_INDEX_PATH} _meta.generated_at "
            f"({api_meta.get('generated_at')!r}) does not match "
            f"site/data/meta.json's ({meta.get('generated_at')!r}) — stale "
            "API — site/api/v1 was not regenerated from the current "
            "site/data; run `python pipeline/emit_api.py`."
        )
    if api_meta.get("contract_version") != meta.get("contract_version"):
        sys.exit(
            f"FAIL: {API_INDEX_PATH} _meta.contract_version "
            f"({api_meta.get('contract_version')!r}) does not match "
            f"site/data/meta.json's ({meta.get('contract_version')!r}) — "
            "stale API — site/api/v1 was not regenerated from the current "
            "site/data; run `python pipeline/emit_api.py`."
        )

    print("OK: site/api/v1/index.json provenance/version coherent with meta.json.")


if __name__ == "__main__":
    main()
