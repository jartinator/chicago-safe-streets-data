import json

import aggregate


def _seed(raw_dir, with_councilmatic):
    (raw_dir / "council_records.json").write_text(json.dumps({
        "data_frozen_at": "2023-06-21",
        "records": [{"matter_id": 100, "title": "Old bike ordinance", "type": "Ordinance",
                     "status": "Passed", "intro_date": "2022-01-01T00:00:00",
                     "sponsors": ["Legacy, L"], "url": "http://legistar/100"}],
    }))
    tags = [{"matter_id": 100, "topic_relevant": True, "topic_reason": "r",
             "tagged_by": "llm"}]
    if with_councilmatic:
        (raw_dir / "councilmatic_records.json").write_text(json.dumps({
            "source": "councilmatic", "latest_action_date": "2026-07-09",
            "records": [{"matter_id": "O2025-1", "title": "New protected lane",
                         "type": "ordinance", "status": "Passed",
                         "intro_date": "2025-02-01T00:00:00", "sponsors": ["Hopkins, Brian"],
                         "url": "http://cm/O2025-1", "source": "councilmatic",
                         "recorded_votes": {"date": "2025-03-01", "yes": 30, "no": 18,
                                            "absent": 2, "no_voters": ["No, N"],
                                            "result": "pass"}}],
        }))
        tags.append({"matter_id": "O2025-1", "topic_relevant": True,
                     "topic_reason": "r", "tagged_by": "llm"})
    (raw_dir / "safety_topic_tags.json").write_text(json.dumps(tags))


def test_merge_carries_source_and_votes_and_flips_note(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    _seed(tmp_path, with_councilmatic=True)

    out, records = aggregate.build_council_records({})

    by_id = {r["matter_id"]: r for r in records}
    assert by_id[100]["source"] == "legistar"
    assert by_id["O2025-1"]["source"] == "councilmatic"
    assert by_id["O2025-1"]["recorded_votes"]["no"] == 18
    assert "current through 2026-07-09" in out["note"]


def test_note_stays_frozen_without_councilmatic(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    _seed(tmp_path, with_councilmatic=False)

    out, records = aggregate.build_council_records({})

    assert len(records) == 1
    assert "only current through 2023-06-21" in out["note"]
