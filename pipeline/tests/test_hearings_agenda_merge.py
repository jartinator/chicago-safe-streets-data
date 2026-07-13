import json

import aggregate as agg


HEARINGS = {
    "as_of": "2026-07-13T00:00:00+00:00",
    "structured_data_available": True,
    "note": "Meetings from the City Clerk eLMS public API.",
    "committees": [
        {"committee": "Committee on Transportation and Public Way",
         "meetings": [
             {"date": "2026-07-14T17:30:00+00:00", "status": "Scheduled & Published",
              "location": "City Hall", "agenda_url": "https://x/agenda.pdf",
              "notice_url": None, "comment": None},
             {"date": "2026-07-21T17:30:00+00:00", "status": "Scheduled",
              "location": None, "agenda_url": "https://x/unfetchable.pdf",
              "notice_url": None, "comment": None},
         ],
         "calendar_url": "https://x/cal"},
    ],
}

AGENDA_ITEMS = {
    "fetched_at": "2026-07-13T00:00:00+00:00",
    "agendas": {
        "https://x/agenda.pdf": {
            "amended": True,
            "items": [
                {"record_number": "O2026-0026797", "ward": 28, "section": "ORDINANCES",
                 "agenda_text": "HUB 32, LLC - O2026-0026797 A proposed Vacation of an alley.",
                 "title": "Vacation of alley", "type": "Ordinance",
                 "status": "4-In Committee", "sponsor": "Dept./Agency",
                 "category": "ALLEY | Vacation(s)",
                 "matter_url": "https://x/matter/1"},
                {"record_number": "O2026-0025394", "ward": None, "section": None,
                 "agenda_text": "PROTECTED BIKE LANE FOR MILWAUKEE AVE - O2026-0025394"},
                {"record_number": None, "ward": None, "section": "MAYORAL",
                 "agenda_text": "APPOINTMENT OF X - The appointment of X to the CTA board."},
            ],
        },
        # unfetchable.pdf deliberately absent — its meeting must stay untouched
    },
}

COUNCIL_RECORDS = [
    {"matter_id": "O2026-0026797", "title": "Vacation of alley"},
    {"matter_id": 12345, "title": "legacy Legistar numeric id — never matches"},
]


def _write_raw(tmp_path, hearings=HEARINGS, agenda=AGENDA_ITEMS):
    (tmp_path / "hearings.json").write_text(json.dumps(hearings))
    if agenda is not None:
        (tmp_path / "agenda_items.json").write_text(json.dumps(agenda))


def test_merge_attaches_items_flags_and_note(tmp_path, monkeypatch):
    _write_raw(tmp_path)
    monkeypatch.setattr(agg, "RAW_DIR", tmp_path)
    out = agg.build_hearings(COUNCIL_RECORDS)

    m1, m2 = out["committees"][0]["meetings"]
    assert m1["agenda_amended"] is True
    assert len(m1["agenda_items"]) == 3

    vacation, bike, appt = m1["agenda_items"]
    assert vacation["tracked"] is True          # matter_id matched in council records
    assert vacation["safety_keyword_match"] is False
    assert bike["tracked"] is False
    assert bike["safety_keyword_match"] is True  # "bike lane" hits the keyword net
    assert appt["tracked"] is False              # no record number can't be tracked

    assert out["note"].endswith("the linked PDF is authoritative.")
    # Unparsed PDF -> meeting keeps its link, no empty agenda_items fabricated.
    assert "agenda_items" not in m2 and "agenda_amended" not in m2


def test_no_agenda_file_leaves_hearings_untouched(tmp_path, monkeypatch):
    _write_raw(tmp_path, agenda=None)
    monkeypatch.setattr(agg, "RAW_DIR", tmp_path)
    out = agg.build_hearings(COUNCIL_RECORDS)
    m1 = out["committees"][0]["meetings"][0]
    assert "agenda_items" not in m1
    assert out["note"] == HEARINGS["note"]


def test_merge_survives_no_council_records():
    item = {"record_number": "O2026-1", "agenda_text": "speed hump program"}
    agg.decorate_agenda_item(item, set())
    assert item["safety_keyword_match"] is True and item["tracked"] is False
