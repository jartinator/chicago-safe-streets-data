import requests
import pytest
import socrata


class _MockResp:
    """Mock response object that behaves like requests.Response."""
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"{self.status_code}")

    def json(self):
        return {}


def test_get_retries_on_read_timeout(monkeypatch):
    """A request that raises ReadTimeout twice then returns 200 succeeds."""
    calls = []
    sleep_calls = []
    attempt = [0]

    def mock_get(url, params, timeout):
        calls.append((url, params, timeout))
        attempt[0] += 1
        if attempt[0] <= 2:
            raise requests.ReadTimeout("timeout")
        return _MockResp(status_code=200)

    def mock_sleep(duration):
        sleep_calls.append(duration)

    monkeypatch.setattr(socrata._SESSION, "get", mock_get)
    monkeypatch.setattr("socrata.time.sleep", mock_sleep)

    resp = socrata._get("http://example.com", {"test": "param"})

    # Should succeed on third attempt
    assert resp.status_code == 200
    assert len(calls) == 3
    # Should have slept twice (after first and second attempts)
    assert len(sleep_calls) == 2
    assert sleep_calls == [2, 4]  # 2s doubling backoff


def test_get_re_raises_exception_on_all_failures(monkeypatch):
    """A request that raises on every attempt re-raises after retries+1 attempts."""
    calls = []
    sleep_calls = []
    attempt = [0]

    def mock_get(url, params, timeout):
        calls.append((url, params, timeout))
        attempt[0] += 1
        raise requests.ConnectionError("connection failed")

    def mock_sleep(duration):
        sleep_calls.append(duration)

    monkeypatch.setattr(socrata._SESSION, "get", mock_get)
    monkeypatch.setattr("socrata.time.sleep", mock_sleep)

    with pytest.raises(requests.ConnectionError):
        socrata._get("http://example.com", {"test": "param"})

    # Should have tried retries+1 times (default retries=4 means 5 attempts)
    assert len(calls) == 5
    # Should have slept 4 times (after each of the first 4 attempts)
    assert len(sleep_calls) == 4


def test_get_retries_on_non_200_status(monkeypatch):
    """Existing non-200-then-200 retry behavior still works."""
    calls = []
    sleep_calls = []
    attempt = [0]

    def mock_get(url, params, timeout):
        calls.append((url, params, timeout))
        attempt[0] += 1
        if attempt[0] == 1:
            return _MockResp(status_code=503)  # Service unavailable
        return _MockResp(status_code=200)

    def mock_sleep(duration):
        sleep_calls.append(duration)

    monkeypatch.setattr(socrata._SESSION, "get", mock_get)
    monkeypatch.setattr("socrata.time.sleep", mock_sleep)

    resp = socrata._get("http://example.com", {"test": "param"})

    # Should succeed on second attempt
    assert resp.status_code == 200
    assert len(calls) == 2
    # Should have slept once (after first attempt)
    assert len(sleep_calls) == 1
    assert sleep_calls == [2]


def test_get_raises_for_status_on_final_non_200(monkeypatch):
    """On final attempt with non-200 status, raise_for_status is called."""
    def mock_get(url, params, timeout):
        return _MockResp(status_code=500)

    def mock_sleep(duration):
        pass

    monkeypatch.setattr(socrata._SESSION, "get", mock_get)
    monkeypatch.setattr("socrata.time.sleep", mock_sleep)

    with pytest.raises(requests.HTTPError):
        socrata._get("http://example.com", {"test": "param"})


def test_get_returns_immediately_on_200(monkeypatch):
    """A successful 200 response is returned immediately without retrying."""
    calls = []
    sleep_calls = []

    def mock_get(url, params, timeout):
        calls.append((url, params, timeout))
        return _MockResp(status_code=200)

    def mock_sleep(duration):
        sleep_calls.append(duration)

    monkeypatch.setattr(socrata._SESSION, "get", mock_get)
    monkeypatch.setattr("socrata.time.sleep", mock_sleep)

    resp = socrata._get("http://example.com", {"test": "param"})

    # Should succeed on first attempt
    assert resp.status_code == 200
    assert len(calls) == 1
    # Should not have slept at all
    assert len(sleep_calls) == 0
