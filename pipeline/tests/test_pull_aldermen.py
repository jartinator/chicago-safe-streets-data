from pull_aldermen import build_aldermen, roster_is_valid


def test_build_aldermen_fills_all_50_wards_and_normalizes():
    rows = [
        {"ward": "1", "alderman": " La Spata, Daniel ", "email": "Ward01@cityofchicago.org",
         "ward_phone": "312-555-0001", "website": {"url": "https://www.the1stward.com"}},
        {"ward": "3", "alderman": "Dowell, Pat", "email": "Ward03@cityofchicago.org"},
    ]
    wards = build_aldermen(rows)
    assert len(wards) == 50
    w1 = next(w for w in wards if w["ward"] == "1")
    assert w1["alderman"] == "La Spata, Daniel"          # trimmed
    assert w1["website"] == "https://www.the1stward.com"  # Socrata url-type unwrapped
    assert w1["phone"] == "312-555-0001"
    w2 = next(w for w in wards if w["ward"] == "2")
    assert w2["alderman"] is None                         # missing ward -> nulls, never invented
    assert w2["email"] is None


def test_validate_roster_rejects_sparse_pull():
    assert not roster_is_valid([{"ward": str(i), "alderman": None} for i in range(1, 51)])
    assert roster_is_valid([{"ward": str(i), "alderman": f"Name{i}, Test"} for i in range(1, 51)])
