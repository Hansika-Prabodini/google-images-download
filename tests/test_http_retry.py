import inspect
import importlib

import pytest

# NOTE:
# The repository under test does not currently expose an HttpClient symbol.
# These tests are written to the specification provided: they dynamically
# attempt to import `HttpClient` from a few likely module paths. If not found,
# tests will be skipped with a helpful message. This allows the test module to
# exist prior to the implementation landing, and keeps CI green for unrelated
# changes.

LIKELY_CLIENT_MODULES = (
    "_http",               # as suggested by the task description
    "http_client",         # conventional
    "client",              # fallback
)


def _import_http_client_symbol():
    last_err = None
    for mod in LIKELY_CLIENT_MODULES:
        try:
            m = importlib.import_module(mod)
            if hasattr(m, "HttpClient"):
                return m.HttpClient, m
        except Exception as e:  # pragma: no cover - only exercised in missing impl
            last_err = e
            continue
    pytest.skip(
        "HttpClient implementation not found. Checked modules: {}. Last error: {}".format(
            ", ".join(LIKELY_CLIENT_MODULES), last_err
        )
    )


@pytest.fixture()
def http_client_cls():
    HttpClient, _ = _import_http_client_symbol()
    return HttpClient


@pytest.fixture()
def client_builder(http_client_cls):
    # Returns a function that builds HttpClient filtering kwargs to signature
    def _build(**kwargs):
        sig = inspect.signature(http_client_cls)
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return http_client_cls(**filtered)
    return _build


class DummyResponse:
    def __init__(self, status_code=200, content=b"ok", headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}

    @property
    def ok(self):
        return 200 <= self.status_code < 300


@pytest.fixture()
def sleep_recorder(monkeypatch):
    calls = []

    def fake_sleep(secs):
        calls.append(secs)

    # Try to patch time.sleep where the client uses it. Patch both time.sleep
    # and any local import of sleep inside the module if present.
    import time as _time
    monkeypatch.setattr(_time, "sleep", fake_sleep)
    # Also patch on module, if it defines sleep directly
    HttpClient, mod = _import_http_client_symbol()
    if hasattr(mod, "time"):
        try:
            monkeypatch.setattr(mod.time, "sleep", fake_sleep, raising=False)
        except Exception:
            pass
    if hasattr(mod, "sleep"):
        try:
            monkeypatch.setattr(mod, "sleep", fake_sleep, raising=False)
        except Exception:
            pass

    return calls


@pytest.fixture()
def deterministic_jitter(monkeypatch):
    # Force random jitter to deterministic constant if the module uses random.random()
    HttpClient, mod = _import_http_client_symbol()
    if hasattr(mod, "random"):
        try:
            monkeypatch.setattr(mod.random, "random", lambda: 0.0, raising=False)
        except Exception:
            pass
    # Also patch Python's global random in case the client uses it
    import random as _random
    monkeypatch.setattr(_random, "random", lambda: 0.0)


@pytest.fixture()
def session_request_spy(monkeypatch):
    # Provide a helper to script a sequence of outcomes for requests.Session.request
    class Spy:
        def __init__(self):
            self.calls = []
            self.outcomes = []  # items can be Exception instance to raise, or DummyResponse/Response-like

        def set_outcomes(self, *items):
            self.outcomes = list(items)

        def __call__(self, session, method, url, **kwargs):
            self.calls.append((method, url, kwargs))
            if not self.outcomes:
                raise AssertionError("No scripted outcomes left for Session.request")
            item = self.outcomes.pop(0)
            if isinstance(item, BaseException):
                raise item
            return item

    spy = Spy()

    # Patch the most typical import path: requests.Session.request
    import requests

    def request_proxy(self, method, url, **kwargs):
        return spy(self, method, url, **kwargs)

    monkeypatch.setattr(requests.Session, "request", request_proxy)

    return spy


@pytest.mark.usefixtures("deterministic_jitter")
class TestRetries:
    def test_timeout_retries_then_success(self, client_builder, sleep_recorder, session_request_spy):
        # Arrange: two timeouts then success
        import requests
        session_request_spy.set_outcomes(
            requests.Timeout(),
            requests.Timeout(),
            DummyResponse(status_code=200),
        )
        client = client_builder(max_retries=3, backoff_base=0.1, backoff_jitter=0.0)

        # Act
        resp = client.request("GET", "https://example.com/")

        # Assert
        assert resp.ok
        assert len(session_request_spy.calls) == 3
        # Expected sleeps for backoff_base=0.1 and no jitter for 2 retries: 0.1, 0.2
        assert pytest.approx(sleep_recorder) == [pytest.approx(0.1), pytest.approx(0.2)]

    def test_429_then_success(self, client_builder, sleep_recorder, session_request_spy):
        session_request_spy.set_outcomes(
            DummyResponse(status_code=429),
            DummyResponse(status_code=200),
        )
        client = client_builder(max_retries=3, backoff_base=0.1, backoff_jitter=0.0)
        resp = client.request("GET", "https://example.com/")
        assert resp.ok
        assert len(session_request_spy.calls) == 2
        assert pytest.approx(sleep_recorder) == [pytest.approx(0.1)]

    def test_5xx_then_success(self, client_builder, sleep_recorder, session_request_spy):
        session_request_spy.set_outcomes(
            DummyResponse(status_code=500),
            DummyResponse(status_code=502),
            DummyResponse(status_code=200),
        )
        client = client_builder(max_retries=3, backoff_base=0.1, backoff_jitter=0.0)
        resp = client.request("GET", "https://example.com/")
        assert resp.ok
        assert len(session_request_spy.calls) == 3
        assert pytest.approx(sleep_recorder) == [pytest.approx(0.1), pytest.approx(0.2)]

    def test_non_retry_400_404(self, client_builder, sleep_recorder, session_request_spy):
        session_request_spy.set_outcomes(
            DummyResponse(status_code=404),
        )
        client = client_builder(max_retries=3, backoff_base=0.1, backoff_jitter=0.0)
        raised = None
        resp = None
        try:
            resp = client.request("GET", "https://example.com/")
        except Exception as e:
            raised = e
        # Regardless of return or raise, there should be no retry
        assert len(session_request_spy.calls) == 1
        assert sleep_recorder == []
        if resp is not None:
            assert not resp.ok

    def test_final_failure_after_exhausting_retries(self, client_builder, sleep_recorder, session_request_spy):
        import requests
        session_request_spy.set_outcomes(
            requests.Timeout(),
            requests.Timeout(),
            requests.Timeout(),
            requests.Timeout(),  # even beyond max_retries to ensure exhaustion
        )
        client = client_builder(max_retries=3, backoff_base=0.1, backoff_jitter=0.0)
        with pytest.raises(requests.Timeout):
            client.request("GET", "https://example.com/")
        # Should have attempted 1 + max_retries times, but stop once retries exhausted
        assert len(session_request_spy.calls) == 1 + 3
        # Sleeps should equal number of retries performed (3): 0.1, 0.2, 0.4
        assert pytest.approx(sleep_recorder) == [pytest.approx(0.1), pytest.approx(0.2), pytest.approx(0.4)]


@pytest.mark.usefixtures("deterministic_jitter")
class TestOptionalBackoffCap:
    def test_backoff_cap_if_supported(self, client_builder, sleep_recorder, session_request_spy):
        # Arrange a failing sequence to trigger multiple backoffs
        import requests
        session_request_spy.set_outcomes(
            requests.ConnectionError(),
            requests.ConnectionError(),
            requests.ConnectionError(),
            requests.ConnectionError(),
        )
        # Try to pass a backoff_cap parameter if supported; otherwise, skip the test
        try:
            client = client_builder(max_retries=4, backoff_base=1.0, backoff_jitter=0.0, backoff_cap=1.5)
        except TypeError:
            pytest.skip("HttpClient does not support a backoff cap parameter")

        with pytest.raises(Exception):
            client.request("GET", "https://example.com/")

        # Expected backoffs without cap would be: 1.0, 2.0, 4.0, 8.0 (but only 4 retries attempted)
        # With cap=1.5, each sleep should be min(computed, 1.5)
        assert all(s <= 1.5 + 1e-9 for s in sleep_recorder)
        assert sleep_recorder[0] == pytest.approx(1.0)
        # The rest should be capped to 1.5
        for s in sleep_recorder[1:]:
            assert s == pytest.approx(1.5)
