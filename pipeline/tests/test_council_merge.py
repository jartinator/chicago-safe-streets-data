import json

from council_merge import load_all_council_records


def _write(path, obj):
    path.write_text(json.dumps(obj))


def test_union_tags_sources_and_flags_meta(tmp_path):
    _write(tmp_path / "council_records.json", {
        "data_frozen_at": "2023-06-21",
        "records": [{"matter_id": 100, "title": "old legistar bill"}],
    })
    _write(tmp_path / "councilmatic_records.json", {
        "source": "councilmatic", "latest_action_date": "2026-07-09",
        "records": [{"matter_id": "O2025-1", "title": "new bill", "source": "councilmatic"}],
    })

    records, meta = load_all_council_records(tmp_path)

    by_id = {r["matter_id"]: r for r in records}
    assert by_id[100]["source"] == "legistar"      # defaulted in
    assert by_id["O2025-1"]["source"] == "councilmatic"
    assert meta == {"has_councilmatic": True,
                    "legistar_frozen_at": "2023-06-21",
                    "councilmatic_latest": "2026-07-09"}


def test_missing_councilmatic_file(tmp_path):
    _write(tmp_path / "council_records.json", {
        "data_frozen_at": "2023-06-21", "records": [{"matter_id": 1, "title": "x"}]})
    records, meta = load_all_council_records(tmp_path)
    assert len(records) == 1
    assert meta["has_councilmatic"] is False
    assert meta["councilmatic_latest"] is None


def test_missing_both_files(tmp_path):
    records, meta = load_all_council_records(tmp_path)
    assert records == []
    assert meta["has_councilmatic"] is False


def test_dedupes_within_source(tmp_path):
    _write(tmp_path / "council_records.json", {"records": [
        {"matter_id": 1, "title": "a"}, {"matter_id": 1, "title": "dup"}]})
    records, _ = load_all_council_records(tmp_path)
    assert len(records) == 1


def test_same_id_across_sources_not_deduped(tmp_path):
    _write(tmp_path / "council_records.json", {"records": [
        {"matter_id": 1, "title": "legistar one"}]})
    _write(tmp_path / "councilmatic_records.json", {"source": "councilmatic", "records": [
        {"matter_id": 1, "title": "councilmatic one", "source": "councilmatic"}]})
    records, _ = load_all_council_records(tmp_path)
    assert len(records) == 2
    assert {r["source"] for r in records} == {"legistar", "councilmatic"}
