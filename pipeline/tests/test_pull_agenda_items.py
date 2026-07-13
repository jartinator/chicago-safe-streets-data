import pull_agenda_items as pai

# Page texts shaped like real pypdf output from a 2026 Transportation committee
# agenda (cover page; RULE 45; mayoral appointments with no record numbers;
# a "()" citywide item whose record number wraps to the next line; a "(28)"
# ward item with a description after the record number).
COVER = "AMENDED \n \nMEETING AGENDA \nCOMMITTEE ON TRANSPORTATION AND PUBLIC WAY \nCommittee Meeting Held on July 14, 2026 \n"
PAGE_RULE45 = "2 \n \nRULE 45: \n \nApproval of the Rule 45 report for the Committee on Transportation and Public Way meeting \nheld on July 8, 2026. \n"
PAGE_MAYORAL = (
    "3 \n \nMAYORAL \nWARD \n APPOINTMENT OF OSWALDO ALVAREZ AS A MEMBER OF THE NORTHERN ILLINOIS \n"
    "TRANSIT AUTHORITY BOARD AND CHICAGO TRANSIT BOARD – \n"
    "The appointment of Oswaldo Alvarez as a member of the NITA Board and Chicago Transit Board \n"
    "for a term effective September 1, 2026. \n \n"
    " APPOINTMENT OF LESTER BARCLAY AS A MEMBER OF THE NORTHERN ILLINOIS \n"
    "TRANSIT AUTHORITY BOARD – \n"
    "The appointment of Lester Barclay for a term effective September 1, 2026. \n"
)
PAGE_CODE = (
    "5 \n \nAMENDMENT OF MUNICIPAL CODE CHAPTERS \nWARD \n"
    "    () AMENDMENT OF MUNICIPAL CODE CHAPTER 9-64 ESTABLISHING ELECTRIC VEHICLE \n"
    "CURBSIDE CHARGING PILOT PROGRAM – O2026-0025394 \n"
)
PAGE_VACATION = (
    "6 \n \nORDINANCES FOR VACATIONS, DEDICATIONS, OPENINGS AND CLOSINGS OF STREETS AND \nALLEYS: \nWARD \n"
    "(28) HUB 32, LLC – O2026-0026797 \n"
    "A proposed Vacation of a portion of the 16-foot, east-west alley. This \n"
    "property is located in the 28th Ward. \n"
)
PAGES = [COVER, PAGE_RULE45, PAGE_MAYORAL, PAGE_CODE, PAGE_VACATION]


def _by_record(parsed):
    return {i["record_number"]: i for i in parsed["items"] if i["record_number"]}


def test_parse_detects_amended_cover():
    assert pai.parse_agenda_pages(PAGES)["amended"] is True
    assert pai.parse_agenda_pages([COVER.replace("AMENDED", "")])["amended"] is False


def test_parse_extracts_record_number_items_with_ward_and_section():
    parsed = pai.parse_agenda_pages(PAGES)
    by_rn = _by_record(parsed)
    assert set(by_rn) == {"O2026-0025394", "O2026-0026797"}

    ev = by_rn["O2026-0025394"]  # "()" = citywide, record number wrapped to line 2
    assert ev["ward"] is None
    assert ev["section"] == "AMENDMENT OF MUNICIPAL CODE CHAPTERS"
    assert "ELECTRIC VEHICLE CURBSIDE CHARGING PILOT PROGRAM" in ev["agenda_text"]

    vac = by_rn["O2026-0026797"]
    assert vac["ward"] == 28
    assert vac["section"].startswith("ORDINANCES FOR VACATIONS")
    assert not vac["section"].endswith(":")
    assert not vac["agenda_text"].startswith("(28)")
    assert "A proposed Vacation" in vac["agenda_text"]


def test_parse_keeps_items_without_record_numbers_verbatim():
    parsed = pai.parse_agenda_pages(PAGES)
    no_rn = [i for i in parsed["items"] if not i["record_number"]]
    sections = {i["section"] for i in no_rn}
    assert "MAYORAL" in sections and "RULE 45" in sections
    appointments = [i for i in no_rn if i["section"] == "MAYORAL"]
    assert len(appointments) == 2
    assert "Oswaldo Alvarez" in appointments[0]["agenda_text"]


def test_parse_dedupes_repeated_record_numbers_and_handles_prefixes():
    pages = ["cover", "2 \n \n(1) FIRST – Or2026-0000001 \n \n"
                      "(1) FIRST AGAIN – Or2026-0000001 \n \n"
                      "() SUBSTITUTE – SO2026-0000002 \n"]
    items = pai.parse_agenda_pages(pages)["items"]
    assert [i["record_number"] for i in items] == ["Or2026-0000001", "SO2026-0000002"]


def test_enrich_item_maps_matter_fields_and_survives_no_match():
    item = {"record_number": "O2026-0026797", "ward": 28, "section": None,
            "agenda_text": "HUB 32, LLC - O2026-0026797 A proposed Vacation."}
    matter = {"matterId": "ABC-123", "title": "Vacation of alley in block bounded by W Maypole Ave",
              "type": "Ordinance", "statusDescription": "4-In Committee",
              "filingSponsor": "Dept./Agency", "matterCategory": "ALLEY | Vacation(s)"}
    pai.enrich_item(item, matter)
    assert item["title"].startswith("Vacation of alley")
    assert item["type"] == "Ordinance"
    assert item["status"] == "4-In Committee"
    assert item["sponsor"] == "Dept./Agency"
    assert item["category"] == "ALLEY | Vacation(s)"
    assert item["matter_url"].endswith("matterId=ABC-123")

    bare = {"record_number": "O2026-0000009", "ward": None, "section": None,
            "agenda_text": "SOMETHING - O2026-0000009"}
    pai.enrich_item(bare, None)
    assert "title" not in bare  # PDF text stands alone; nothing fabricated


def test_build_agendas_is_nonfatal_per_url_and_caches_matter_lookups():
    lookups = []

    def fake_fetch_pdf(url):
        return b"%PDF" if url == "https://x/good.pdf" else None

    def fake_extract(pdf_bytes):
        return ["cover", "2 \n \n(3) A – O2026-0000003 \n \n(4) B – O2026-0000003 \n"]

    def fake_fetch_matter(rn):
        lookups.append(rn)
        return {"matterId": "G1", "title": "Real title", "type": "Ordinance"}

    orig = pai.extract_pdf_pages
    pai.extract_pdf_pages = fake_extract
    try:
        agendas = pai.build_agendas(["https://x/bad.pdf", "https://x/good.pdf"],
                                    fetch_pdf_fn=fake_fetch_pdf,
                                    fetch_matter_fn=fake_fetch_matter)
    finally:
        pai.extract_pdf_pages = orig

    assert list(agendas) == ["https://x/good.pdf"]  # bad URL absent, not fatal
    assert lookups == ["O2026-0000003"]  # deduped parse -> single cached lookup
    assert agendas["https://x/good.pdf"]["items"][0]["title"] == "Real title"


def test_agenda_urls_flattens_and_dedupes():
    hearings = {"committees": [
        {"meetings": [{"agenda_url": "https://x/a.pdf"}, {"agenda_url": None}]},
        {"meetings": [{"agenda_url": "https://x/a.pdf"}, {"agenda_url": "https://x/b.pdf"}]},
    ]}
    assert pai.agenda_urls(hearings) == ["https://x/a.pdf", "https://x/b.pdf"]
