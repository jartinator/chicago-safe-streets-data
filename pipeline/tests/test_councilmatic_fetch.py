import councilmatic


def test_query_builds_url_params_and_returns_rows(monkeypatch):
    calls = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return [{"x": 42}]

        def raise_for_status(self):
            raise AssertionError("raise_for_status should not be called on 200")

    def fake_get(url, params, timeout):
        calls["url"] = url
        calls["params"] = params
        return FakeResp()

    monkeypatch.setattr(councilmatic._SESSION, "get", fake_get)

    rows = councilmatic.query("select 42 as x")

    assert rows == [{"x": 42}]
    assert calls["url"] == "https://puddle.datamade.us/chicago_council.json"
    assert calls["params"] == {"sql": "select 42 as x", "_shape": "array"}
