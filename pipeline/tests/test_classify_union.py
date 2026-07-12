import json
import os
import sys

import classify_safety_topic as cls


def test_classify_tags_councilmatic_records_via_union(tmp_path, monkeypatch):
    # No API key -> deterministic keyword_fallback path (no network).
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cls, "RAW_DIR", tmp_path)
    # main() calls argparse.parse_args(); pin argv so it doesn't parse pytest's args.
    monkeypatch.setattr(sys, "argv", ["classify_safety_topic.py"])

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
