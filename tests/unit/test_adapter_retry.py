"""Unit test for adapter retry/backoff and timeout handling (T023, US2).

Verifies the DubizzleAdapter retries transient failures (timeouts,
connection errors, 429/5xx), does not retry non-transient HTTP errors,
and records retry counts. No network access — uses a stub session.
"""

from __future__ import annotations

import pytest
import requests
from conftest import load_fixture

from src.common.models import Scope
from marketplaces.dubizzle.adapter import DubizzleAdapter


class _Resp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.HTTPError(f"HTTP {self.status_code}")
            err.response = self
            raise err

    def json(self):
        return self._payload


class _ScriptedSession:
    """Returns canned responses or raises scripted exceptions per call."""

    def __init__(self, scripts):
        # scripts: list of either _Resp or Exception instances.
        self._scripts = scripts
        self.calls = 0
        self.headers = {}

    def post(self, url, json=None, timeout=None):
        i = min(self.calls, len(self._scripts) - 1)
        out = self._scripts[i]
        self.calls += 1
        if isinstance(out, Exception):
            raise out
        return out


@pytest.fixture
def config(monkeypatch):
    for k, v in {
        "ALGOLIA_APP_ID": "x",
        "ALGOLIA_API_KEY": "k",
        "ALGOLIA_INDEX": "idx",
        "ALGOLIA_URL": "https://example/queries",
        "OUTPUT_DIR": "./data/out",
        "HITS_PER_PAGE": "20",
        "MAX_PAGES": "500",
        "RETRY_ATTEMPTS": "3",
        "RETRY_BACKOFF": "0",
        "RATE_LIMIT_MIN_SECONDS": "0",
        "RATE_LIMIT_MAX_SECONDS": "0",
        "REQUEST_TIMEOUT_SECONDS": "15",
    }.items():
        monkeypatch.setenv(k, v)
    from config.config import load_config

    return load_config()


def _ok_page(hit):
    return _Resp({"results": [{"hits": [hit], "nbPages": 1, "nbHits": 1, "page": 0}]})


def test_retries_transient_timeout_then_succeeds(config):
    hit = load_fixture("sample_hit.json")
    session = _ScriptedSession([requests.Timeout("boom"), _ok_page(hit)])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-retry")
    out = list(adapter.fetch(Scope("dubizzle", "used", "toyota")))
    assert len(out) == 1
    assert out[0][1].retried is True
    assert adapter.retry_count >= 1
    # Page 0 ultimately succeeded with one hit.
    assert len(out[0][0]) == 1


def test_retries_connection_error_then_succeeds(config):
    hit = load_fixture("sample_hit.json")
    session = _ScriptedSession([requests.ConnectionError("down"), _ok_page(hit)])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-retry-conn")
    out = list(adapter.fetch(Scope("dubizzle", "used", "toyota")))
    assert out[0][1].retried is True
    assert len(out[0][0]) == 1


def test_retries_rate_limit_429_then_succeeds(config):
    hit = load_fixture("sample_hit.json")
    session = _ScriptedSession([_Resp(None, status_code=429), _ok_page(hit)])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-429")
    out = list(adapter.fetch(Scope("dubizzle", "used", "toyota")))
    assert out[0][1].retried is True
    assert len(out[0][0]) == 1


def test_exhausted_retries_recorded_as_failure(config):
    session = _ScriptedSession([requests.Timeout("boom")] * 5)
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-dead")
    out = list(adapter.fetch(Scope("dubizzle", "used", "toyota")))
    # One page attempted, no listings, marked as failed.
    assert len(out) == 1
    assert out[0][0] == []
    assert adapter.failures >= 1
    assert adapter.retry_count >= 3


def test_non_transient_http_error_not_retried(config):
    # 404 is not in the transient set; adapter should stop immediately.
    session = _ScriptedSession([_Resp(None, status_code=404)])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-404")
    out = list(adapter.fetch(Scope("dubizzle", "used", "toyota")))
    assert session.calls == 1  # no retry attempted
    assert out[0][0] == []
