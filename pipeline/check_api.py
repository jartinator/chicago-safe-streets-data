"""Guardrail: validate the committed agent API (site/api/v1/) against its
hand-written JSON Schemas and internal contracts.

    python check_api.py

Phase 4 of the agent-first static API (see pipeline/emit_api.py and
docs/superpowers/plans/2026-07-13-agent-api-layer.md) adds a normative schema
layer under site/api/v1/schemas/. This script is the CI-enforced check that
every committed file actually conforms to it, that no file has grown past its
size budget, that index.json's manifest matches what's really on disk, and
that every file's envelope agrees on api_version/contract_version. No
network — schema $refs resolve locally via a `referencing.Registry` built
from the committed schema files, same as the test suite.

Checks, in order (first failure wins — each prints a clear message naming the
offending file and reason before exiting 1):
  1. Every file under site/api/v1/ (recursively, excluding schemas/) is valid
     JSON and validates against its schema (mapped by convention — see
     SCHEMA_BY_PATH / _schema_name_for).
  2. Size budgets: every committed file's on-disk size is within
     API_CRASH_SLICE_BUDGET_BYTES (crashes/ward-NN.json) or
     API_SIZE_BUDGET_BYTES (everything else) — re-derived from
     pipeline/config.py, same budgets emit_api.py enforces at build time.
  3. Manifest completeness: every path/family listed in index.json's
     endpoints/families exists on disk, and every file actually on disk
     (outside schemas/) is accounted for by either an endpoints entry or a
     families path_template match — no orphan files, no dangling manifest
     entries.
  4. Provenance/version coherence: every file's _meta.contract_version and
     _meta.api_version match index.json's (check_provenance.py already
     validates index.json's own generated_at/contract_version against
     site/data/meta.json; this check is purely internal consistency across
     all api/v1 files).

Exit codes:
  0  site/api/v1/index.json doesn't exist yet (nothing to check), or every
     check above passes
  1  any check fails

Run this locally alongside check_provenance.py after `python emit_api.py`;
it also runs in CI on every PR (see .github/workflows/data-guard.yml).
"""
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from config import API_CRASH_SLICE_BUDGET_BYTES, API_SIZE_BUDGET_BYTES

REPO_ROOT = Path(__file__).resolve().parent.parent
API_DIR = REPO_ROOT / "site" / "api" / "v1"
SCHEMAS_DIR = API_DIR / "schemas"
INDEX_PATH = API_DIR / "index.json"

# Exact relative-path -> schema filename map. Files sharing a basename
# ("index.json") but living in different directories map to different
# schemas, so this can't be a pure basename lookup.
EXACT_SCHEMA_BY_PATH = {
    "index.json": "index.schema.json",
    "citywide.json": "citywide.schema.json",
    "corridors.json": "corridors.schema.json",
    "news.json": "news.schema.json",
    "proposed.json": "proposed.schema.json",
    "wards/index.json": "wards-index.schema.json",
    "routes/index.json": "routes-index.schema.json",
    "council/index.json": "council-index.schema.json",
    "council/records.json": "council-records.schema.json",
    "council/aldermen.json": "council-aldermen.schema.json",
}

# Family (per-file-pattern) -> schema filename, checked when no exact match.
FAMILY_SCHEMA_PATTERNS = [
    (re.compile(r"^wards/ward-\d+\.json$"), "ward.schema.json"),
    (re.compile(r"^crashes/ward-\d+\.json$"), "crash-slice.schema.json"),
    (re.compile(r"^routes/line-.+\.json$"), "route-line.schema.json"),
]


def _schema_name_for(rel_path):
    """Map a site/api/v1-relative path (posix separators) to its schema
    filename, or None if it doesn't match any known convention.
    """
    if rel_path in EXACT_SCHEMA_BY_PATH:
        return EXACT_SCHEMA_BY_PATH[rel_path]
    for pattern, schema_name in FAMILY_SCHEMA_PATTERNS:
        if pattern.match(rel_path):
            return schema_name
    return None


def _budget_for(rel_path):
    return API_CRASH_SLICE_BUDGET_BYTES if rel_path.startswith("crashes/") else API_SIZE_BUDGET_BYTES


def _build_registry():
    """Load every committed schemas/*.schema.json into a local
    referencing.Registry, keyed by each schema's own $id, so $ref between
    schema files (e.g. envelope.schema.json) resolves offline.
    """
    resources = []
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"FAIL: {schema_path} is not valid JSON: {e}")
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources), {
        schema_id: resource.contents for schema_id, resource in resources
    }


def _all_files(api_dir):
    """Every file under api_dir, recursively, excluding schemas/ — as
    (absolute Path, posix-style relative path) pairs.
    """
    out = []
    for path in sorted(api_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(api_dir).as_posix()
        if rel.startswith("schemas/"):
            continue
        out.append((path, rel))
    return out


def _check_schema_conformance(registry, schemas_by_id, base_url):
    """Check 1: every file is valid JSON and validates against its schema.
    Returns {rel_path: parsed_json} for every checked file (reused by later
    checks so nothing is re-parsed from disk).
    """
    parsed = {}
    for path, rel in _all_files(API_DIR):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"FAIL: site/api/v1/{rel} is not valid JSON: {e}")

        schema_name = _schema_name_for(rel)
        if schema_name is None:
            sys.exit(
                f"FAIL: site/api/v1/{rel} has no known schema mapping — "
                "add it to EXACT_SCHEMA_BY_PATH or FAMILY_SCHEMA_PATTERNS "
                "in check_api.py, or it's an orphan file that shouldn't be "
                "committed.")

        schema_id = f"{base_url}/api/v1/schemas/{schema_name}"
        if schema_id not in schemas_by_id:
            sys.exit(
                f"FAIL: site/api/v1/{rel} maps to schema {schema_name!r}, "
                f"but site/api/v1/schemas/{schema_name} does not exist.")

        validator = Draft202012Validator(schemas_by_id[schema_id], registry=registry)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        if errors:
            first = errors[0]
            loc = "/".join(str(p) for p in first.absolute_path) or "<root>"
            sys.exit(
                f"FAIL: site/api/v1/{rel} does not validate against "
                f"{schema_name} at {loc!r}: {first.message}")

        parsed[rel] = data

    print(f"OK: {len(parsed)} site/api/v1 files validate against their schemas.")
    return parsed


def _check_size_budgets():
    """Check 2: no committed file exceeds its size budget."""
    checked = 0
    for path, rel in _all_files(API_DIR):
        size = path.stat().st_size
        budget = _budget_for(rel)
        if size > budget:
            budget_name = ("API_CRASH_SLICE_BUDGET_BYTES" if rel.startswith("crashes/")
                          else "API_SIZE_BUDGET_BYTES")
            sys.exit(
                f"FAIL: site/api/v1/{rel} is {size:,} bytes, over the "
                f"{budget_name} budget of {budget:,} bytes.")
        checked += 1
    print(f"OK: all {checked} site/api/v1 files are within their size budgets.")


def _family_pattern(path_template):
    """Turn an index.json families[].path_template (e.g.
    "wards/ward-{NN}.json") into a regex matching real relative paths.
    """
    escaped = re.escape(path_template)
    pattern = re.sub(r"\\\{[^}]+\\\}", ".+", escaped)
    return re.compile(f"^{pattern}$")


def _check_manifest_completeness(index):
    """Check 3: index.json's endpoints/families cover exactly the files on
    disk — no orphan files, no dangling manifest entries.
    """
    # index.json isn't self-listed in its own endpoints (see build_index's
    # docstring in emit_api.py) — exclude it from the orphan check rather
    # than treating it as uncovered.
    on_disk = {rel for _, rel in _all_files(API_DIR)} - {"index.json"}

    endpoint_paths = {e["path"] for e in index["endpoints"]}
    missing_endpoints = endpoint_paths - on_disk
    if missing_endpoints:
        sys.exit(
            "FAIL: index.json lists endpoint(s) not present on disk: "
            + ", ".join(sorted(missing_endpoints)))

    accounted = set(endpoint_paths)
    family_patterns = [_family_pattern(f["path_template"]) for f in index["families"]]
    for rel in on_disk:
        if rel in accounted:
            continue
        if any(p.match(rel) for p in family_patterns):
            accounted.add(rel)

    orphans = on_disk - accounted
    if orphans:
        sys.exit(
            "FAIL: file(s) on disk not covered by any index.json endpoint "
            "or family: " + ", ".join(sorted(orphans)))

    for family in index["families"]:
        pattern = _family_pattern(family["path_template"])
        actual_count = sum(1 for rel in on_disk if pattern.match(rel))
        if actual_count != family["count"]:
            sys.exit(
                f"FAIL: index.json family {family['path_template']!r} claims "
                f"count {family['count']}, but {actual_count} matching files "
                "are on disk.")

    print("OK: index.json's endpoints/families exactly cover site/api/v1's files on disk.")


def _check_version_coherence(index, parsed):
    """Check 4: every file's _meta.contract_version/api_version match
    index.json's (purely internal consistency — check_provenance.py already
    checks index.json itself against site/data/meta.json).
    """
    want_contract = index["_meta"]["contract_version"]
    want_api = index["_meta"]["api_version"]
    mismatches = []
    for rel, data in parsed.items():
        meta = data.get("_meta", {})
        if meta.get("contract_version") != want_contract or meta.get("api_version") != want_api:
            mismatches.append(
                f"{rel} (contract_version={meta.get('contract_version')!r}, "
                f"api_version={meta.get('api_version')!r})")
    if mismatches:
        sys.exit(
            f"FAIL: file(s) whose _meta contract_version/api_version don't "
            f"match index.json's (contract_version={want_contract!r}, "
            f"api_version={want_api!r}): " + "; ".join(mismatches))
    print(f"OK: all {len(parsed)} site/api/v1 files agree with index.json on "
         "contract_version/api_version.")


def main():
    if not INDEX_PATH.exists():
        print(f"note: {INDEX_PATH} not present — agent API not yet "
              "published; skipping check_api.py.")
        return

    try:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: {INDEX_PATH} is not valid JSON: {e}")

    base_url = index["_meta"]["schema"].rsplit("/api/v1/schemas/", 1)[0]

    registry, schemas_by_id = _build_registry()
    parsed = _check_schema_conformance(registry, schemas_by_id, base_url)
    _check_size_budgets()
    _check_manifest_completeness(index)
    _check_version_coherence(index, parsed)


if __name__ == "__main__":
    main()
