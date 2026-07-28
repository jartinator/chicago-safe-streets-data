"""The published skill (site/skills/) must match its source (.claude/skills/),
index.json must describe what is actually published, and the URL we advertise
must be the URL that exists.

Runs on every PR and every push to main via .github/workflows/tests.yml, which
carries NO path filter — deliberately, because a PR that edits only
.claude/skills/** or only site/skills/** triggers data-guard.yml not at all, so
the test suite is the only check either edit reliably reaches.

Fails the build. It does not warn. A published skill is a set of instructions an
arbitrary third-party agent will follow; a stale copy is a wrong instruction
served from a URL we advertised.

Note the import of SITE_DIR from `config`, not from `emit_api`: conftest.py's
autouse _isolate_emit_api_site_dir fixture patches emit_api.SITE_DIR to tmp_path
for every test in this suite. Importing it from emit_api would make all five
assertions a silent no-op against an empty temp directory.
"""
import hashlib
import json
import re

import sync_skill
from config import REPO_ROOT, SITE_BASE_URL, SITE_DIR, SKILL_ENTRY_URL, SKILL_NAME

FIX = ("Fix with `python pipeline/sync_skill.py`, then "
       "`python pipeline/emit_api.py`. Do NOT hand-edit site/skills/ to match — "
       "it is a generated copy, and the next sync overwrites it. Edit "
       f".claude/skills/{SKILL_NAME}/ instead.")

INDEX = REPO_ROOT / "site" / "api" / "v1" / "index.json"


def _index():
    return json.loads(INDEX.read_text(encoding="utf-8"))


def test_published_skill_has_the_same_files_as_the_source():
    missing, extra, _ = sync_skill.diff()
    assert not missing, f"in .claude/skills/ but not published: {missing}. {FIX}"
    assert not extra, f"published but not in .claude/skills/: {extra}. {FIX}"


def test_published_skill_content_matches_the_source():
    _, _, changed = sync_skill.diff()
    assert not changed, f"content differs (LF-normalised): {changed}. {FIX}"


def test_index_json_skill_hashes_match_the_published_files():
    if not INDEX.exists():
        return  # agent API not yet published; check_api.py skips for the same reason
    skill = _index().get("skill")
    assert skill, (
        f"index.json has no `skill` block, so nothing advertises the guide. "
        f"emit_api.py emits that key only when site/skills/{SKILL_NAME}/ exists, "
        f"so the published copy is missing or was emitted from a different "
        f"SITE_DIR. {FIX}")
    for entry in skill["files"]:
        published = REPO_ROOT / "site" / entry["path"]
        assert published.exists(), (
            f"index.json lists {entry['path']}, which is not on disk. {FIX}")
        data = published.read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], (
            f"index.json's sha256 for {entry['path']} is stale. {FIX}")
        assert len(data) == entry["bytes"], (
            f"index.json's byte count for {entry['path']} is stale. {FIX}")


def test_the_advertised_skill_url_is_one_string_everywhere():
    """F1. Change SKILL_NAME and every generator follows it; only the string a
    third party actually reads can be left behind. Bind all SIX together:
    llms.txt, index.json's skill.entry_point, its files[] entry, the file on
    disk, and the two human-facing pages that advertise the same URL to a
    person (site/assets/js/home.js and site/assets/js/contributing.js).

    The last two are the reason this test grew. They are static JS assets and
    cannot import SKILL_ENTRY_URL from config.py, so they are checked as text.
    See the two blocks at the end for which check is exact and which is not.
    """
    entry_rel = f"skills/{SKILL_NAME}/SKILL.md"

    llms_path = SITE_DIR / "llms.txt"
    assert llms_path.is_file(), (
        f"site/llms.txt does not exist, so nothing advertises "
        f"{SKILL_ENTRY_URL} on the primary discovery route. Regenerate with "
        f"`python pipeline/emit_api.py`. {FIX}")
    llms = llms_path.read_text(encoding="utf-8")
    assert SKILL_ENTRY_URL in llms, (
        f"site/llms.txt does not advertise {SKILL_ENTRY_URL}. llms.txt is the "
        f"primary discovery route: if it names a different URL, an agent that "
        f"reads only llms.txt gets a 404 and index.json never sees it. "
        f"Regenerate with `python pipeline/emit_api.py`. Do NOT edit llms.txt "
        f"by hand and do NOT hard-code the skill name in build_llms_txt — "
        f"build the URL from SKILL_ENTRY_URL in config.py. {FIX}")

    skill = _index().get("skill")
    assert skill, f"index.json has no `skill` block to compare against. {FIX}"
    assert skill["entry_point"] == SKILL_ENTRY_URL, (
        f"index.json's skill.entry_point is {skill['entry_point']!r} but "
        f"llms.txt advertises {SKILL_ENTRY_URL!r}. Two discovery surfaces are "
        f"pointing at different files. {FIX}")

    named = [f for f in skill["files"] if f["path"] == entry_rel]
    assert len(named) == 1, (
        f"skill.files[] has {len(named)} entries for {entry_rel}, expected 1. {FIX}")
    assert named[0]["url"] == SKILL_ENTRY_URL, (
        f"skill.files[] gives {named[0]['url']!r} for the entry point but "
        f"skill.entry_point says {SKILL_ENTRY_URL!r}. {FIX}")

    # Every other published file's url must end in its own path. Without this,
    # only the entry point is bound and the two reference URLs could point
    # anywhere — they are the files SKILL.md tells an agent to join by hand.
    for entry in skill["files"]:
        assert entry["url"].endswith(entry["path"]), (
            f"skill.files[] gives url {entry['url']!r} for path "
            f"{entry['path']!r}; the url must end with the path. {FIX}")

    assert (SITE_DIR / entry_rel).is_file(), (
        f"every surface advertises {SKILL_ENTRY_URL}, and site/{entry_rel} is "
        f"not on disk, so the deployed URL will 404. Do NOT change the "
        f"advertised URL to match whatever is published — publish the file. {FIX}")

    # --- copies 5 and 6: the human-facing pages -----------------------------
    # A person who is handed a stale URL gets the same 404 an agent does, and
    # nothing regenerates these two files. They are plain JS assets, so this is
    # a text check on the shipped source rather than a value comparison.

    # contributing.js carries the URL as ONE literal inside <code>, so this
    # check is exact: the byte sequence a reader copies is the byte sequence
    # config.py declares.
    contributing = SITE_DIR / "assets" / "js" / "contributing.js"
    assert contributing.is_file(), (
        f"site/assets/js/contributing.js is missing; it is one of the two "
        f"human-facing surfaces that advertise {SKILL_ENTRY_URL}. {FIX}")
    assert SKILL_ENTRY_URL in contributing.read_text(encoding="utf-8"), (
        f"site/assets/js/contributing.js does not contain {SKILL_ENTRY_URL}. A "
        f"person reading the Downloads & Docs page is handed that URL by hand; "
        f"nothing regenerates this file, so it goes stale silently while every "
        f"agent-facing surface moves. Update the <code> literal in metadataDiv. "
        f"Do NOT delete the paragraph to make this pass — that reopens the "
        f"human-side parity gap this test exists to keep closed.")

    # home.js builds the URL from its own SITE_ORIGIN constant, following the
    # convention the file already uses for llms.txt. So the full URL is not one
    # contiguous literal and a substring search would not find it. Reconstruct
    # it instead — which is a STRONGER check, because it also binds home.js's
    # SITE_ORIGIN to config.py's SITE_BASE_URL. Nothing else in this repo
    # checks that, and they are two hand-written copies of the same origin.
    home = SITE_DIR / "assets" / "js" / "home.js"
    assert home.is_file(), (
        f"site/assets/js/home.js is missing; it is one of the two human-facing "
        f"surfaces that advertise {SKILL_ENTRY_URL}. {FIX}")
    home_text = home.read_text(encoding="utf-8")

    origins = re.findall(r'SITE_ORIGIN\s*=\s*"([^"]+)"', home_text)
    assert len(origins) == 1, (
        f"expected exactly one SITE_ORIGIN assignment in home.js, found "
        f"{len(origins)}: {origins}. This test reconstructs the advertised "
        f"skill URL from it. Keep the origin in one constant.")
    assert origins[0] == SITE_BASE_URL, (
        f"home.js's SITE_ORIGIN is {origins[0]!r} but config.py's "
        f"SITE_BASE_URL is {SITE_BASE_URL!r}. Every URL this page prints is "
        f"built from the first and every URL the API prints is built from the "
        f"second, so the whole human side of the site is pointing at a "
        f"different host from the agent side. Fix home.js, not config.py — "
        f"config.py is what the generated files use.")

    path_suffix = f"/skills/{SKILL_NAME}/SKILL.md"
    assert path_suffix in home_text, (
        f"site/assets/js/home.js does not contain {path_suffix!r}, so the "
        f"'Ask an AI assistant' section's copy-paste block is advertising a "
        f"different skill path from the one this repo publishes. A reader "
        f"pastes that line into their own assistant and it 404s. Rebuild the "
        f"`skill` const in agentHTML(). Do NOT hard-code the whole origin "
        f"again — it is already in SITE_ORIGIN one line above.")
    assert origins[0] + path_suffix == SKILL_ENTRY_URL, (
        f"home.js advertises {origins[0] + path_suffix!r} but config.py "
        f"declares {SKILL_ENTRY_URL!r}.")


def test_site_skills_holds_exactly_the_one_published_skill():
    """F3. sync_skill.sync() deletes extras INSIDE the published directory. It
    owns no namespace above it, and nothing under site/ is pruned by anything."""
    published = SITE_DIR / "skills"
    assert published.is_dir(), (
        f"site/skills/ does not exist, but llms.txt and index.json advertise a "
        f"URL underneath it. Run `python pipeline/sync_skill.py`. {FIX}")
    names = sorted(p.name for p in published.iterdir())
    assert names == [SKILL_NAME], (
        f"site/skills/ holds {names}, expected exactly ['{SKILL_NAME}']. "
        f"Nothing prunes site/, so an extra directory here is served by GitHub "
        f"Pages forever, advertised nowhere, guarded by nothing. If you renamed "
        f"the skill, delete the old directory in this PR. "
        f"Do NOT add another .claude/skills/ directory here to make this pass: "
        f"board/ and verify/ are internal repo instructions, and "
        f"verify/SKILL.md tells its reader to start a local HTTP server and "
        f"drive a browser at it — that is not something to hand an arbitrary "
        f"agent off the open internet. Publishing a second skill is a config "
        f"change plus a deliberate widening of this assertion.")
