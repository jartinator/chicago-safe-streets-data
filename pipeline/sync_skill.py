"""Publish the repo's agent skill to site/, so a third-party agent can fetch it.

    python sync_skill.py           # regenerate the published copy
    python sync_skill.py --check   # exit 1 if it is out of date; write nothing

EXACTLY ONE skill is published, named by SKILL_NAME in config.py. The mapping is
.claude/skills/$SKILL_NAME/** -> site/skills/$SKILL_NAME/**. It is NOT a glob
over .claude/skills/. board/ and verify/ are internal instructions for this repo
and must never be served to the public internet.

.claude/skills/$SKILL_NAME/ is the single source of truth. It is edited by hand.
site/skills/$SKILL_NAME/ is a GENERATED COPY, published to GitHub Pages by
deploy.yml and advertised in site/llms.txt and site/api/v1/index.json. Never
hand-edit the published copy: this script overwrites it, and
pipeline/tests/test_skill_publication.py fails CI whenever the two differ.

Content is compared and written with LF line endings regardless of what git's
autocrlf left in the working tree, so the guard cannot be defeated by a checkout
setting.

After running this, run `python pipeline/emit_api.py` — index.json's
skill.files[] carries a sha256 per file, regenerated from the published copy.
"""
import argparse
import sys

from config import SITE_DIR, SKILL_NAME, SKILL_SOURCE_DIR

PUBLISHED_DIR = SITE_DIR / "skills" / SKILL_NAME


def _tree(root):
    """{posix relative path: LF-normalised bytes} for every file under root.

    Sorted by the POSIX relative-path STRING, never by Path objects.
    sorted(root.rglob("*")) compares Path objects, and PurePosixPath compares
    case-sensitively while PureWindowsPath does not — so "SKILL.md" sorts before
    "reference/..." on the Linux CI runner and after it on a Windows checkout.
    Verified:
        >>> sorted([PurePosixPath('B'), PurePosixPath('a')])
        [PurePosixPath('B'), PurePosixPath('a')]
        >>> sorted([PureWindowsPath('B'), PureWindowsPath('a')])
        [PureWindowsPath('a'), PureWindowsPath('B')]
    This dict's insertion order reaches index.json as skill.files[]'s order, so
    sorting by Path would make a generated, committed file's diff depend on which
    machine ran emit_api.py.
    """
    if not root.exists():
        return {}
    files = {
        p.relative_to(root).as_posix(): p
        for p in root.rglob("*") if p.is_file()
    }
    return {rel: files[rel].read_bytes().replace(b"\r\n", b"\n")
            for rel in sorted(files)}


def diff():
    """(only_in_source, only_in_published, differing_content) — all sorted."""
    src, pub = _tree(SKILL_SOURCE_DIR), _tree(PUBLISHED_DIR)
    return (sorted(set(src) - set(pub)),
            sorted(set(pub) - set(src)),
            sorted(k for k in set(src) & set(pub) if src[k] != pub[k]))


def sync():
    src = _tree(SKILL_SOURCE_DIR)
    if not src:
        sys.exit(f"FAIL: {SKILL_SOURCE_DIR} is empty or missing — nothing to publish.")
    for rel in sorted(set(_tree(PUBLISHED_DIR)) - set(src)):
        (PUBLISHED_DIR / rel).unlink()
    for rel, data in src.items():
        out = PUBLISHED_DIR / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    print(f"OK: published {len(src)} file(s) to site/skills/{SKILL_NAME}/. "
          "Now run `python pipeline/emit_api.py` to refresh index.json's hashes.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1; do not write")
    if ap.parse_args().check:
        missing, extra, changed = diff()
        if missing or extra or changed:
            sys.exit("FAIL: site/skills/ is out of date. "
                     f"missing={missing} extra={extra} changed={changed}. "
                     "Fix with `python pipeline/sync_skill.py`, then "
                     "`python pipeline/emit_api.py`.")
        print("OK: the published skill matches the source.")
        return
    sync()


if __name__ == "__main__":
    main()
