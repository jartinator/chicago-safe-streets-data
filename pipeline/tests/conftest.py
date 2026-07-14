import pathlib
import sys

# Put the pipeline/ directory (parent of tests/) on sys.path so tests can
# `import config`, `import councilmatic`, etc. the same flat way the modules do.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402  (must follow the sys.path insert above)


@pytest.fixture(autouse=True)
def _isolate_emit_api_site_dir(monkeypatch, tmp_path):
    """Safety net: emit_api.emit_all() (Phase 5) writes site/llms.txt and
    site/sitemap.xml under emit_api.SITE_DIR, a THIRD directory alongside
    SITE_DATA_DIR/SITE_API_DIR that pre-Phase-5 tests never had to
    monkeypatch. Without this, any test that calls emit_all() (or
    refresh_reporting.main(), which calls it) while patching only
    SITE_DATA_DIR/SITE_API_DIR would silently write real llms.txt/
    sitemap.xml into this repo's actual site/ directory using synthetic
    fixture data — exactly the kind of accidental contamination
    check_provenance.py exists to catch for site/data, but for two files
    outside its scope. Every test gets a safe tmp default; a test that
    deliberately wants to exercise the real SITE_DIR can still override
    this after the fixture runs (monkeypatch.setattr wins last).
    """
    import emit_api
    monkeypatch.setattr(emit_api, "SITE_DIR", tmp_path / "_autouse_site_dir_guard")
