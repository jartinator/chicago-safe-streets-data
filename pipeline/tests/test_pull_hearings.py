from pull_hearings import normalize_meetings

API_ROWS = [
    {"meetingId": 1, "status": "Scheduled & Published", "date": "2026-07-14T13:00:00",
     "location": "City Hall, Room 201-A",
     "comment": "Written Public Comment deadline is July 10, 2026 12:30 PM at ctpw@cityofchicago.org",
     "files": [{"path": "https://x/agenda.pdf", "attachmentType": "Agenda"},
               {"path": "https://x/notice.pdf", "attachmentType": "Notice"}]},
    {"meetingId": 2, "status": "Cancelled", "date": "2026-07-20T10:00:00", "files": []},
    {"meetingId": 3, "status": "Scheduled", "date": "2026-01-05T10:00:00", "files": []},  # past
    {"meetingId": 4, "status": "Scheduled", "date": "not-a-date", "files": []},           # invalid
]


def test_normalize_keeps_future_scheduled_only_and_extracts_files():
    out = normalize_meetings(API_ROWS, today="2026-07-12")
    assert len(out) == 1
    m = out[0]
    assert m["date"] == "2026-07-14T13:00:00"
    assert m["status"] == "Scheduled & Published"
    assert m["location"] == "City Hall, Room 201-A"
    assert m["agenda_url"] == "https://x/agenda.pdf"
    assert m["notice_url"] == "https://x/notice.pdf"
    assert "Written Public Comment" in m["comment"]


def test_normalize_sorts_future_meetings_oldest_first():
    rows = [
        {"status": "Scheduled", "date": "2026-09-01T10:00:00", "files": []},
        {"status": "Scheduled", "date": "2026-08-01T10:00:00", "files": []},
    ]
    out = normalize_meetings(rows, today="2026-07-12")
    assert [m["date"][:10] for m in out] == ["2026-08-01", "2026-09-01"]


def test_normalize_empty_input():
    assert normalize_meetings([], today="2026-07-12") == []
    assert normalize_meetings(None, today="2026-07-12") == []
