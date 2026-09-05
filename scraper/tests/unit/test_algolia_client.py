"""Unit tests for the AlgoliaClient transport layer (T023, US2).

Verifies request construction, retry/backoff for transient failures
(timeouts, connection errors, 429/5xx), no retry for non-transient HTTP
errors, retries exhausted, and empty-results handling. No network access —
uses a stub session.
"""

from __future__ import annotations

import pytest
import requests

from src.fetch.algolia_client import RETRYABLE_STATUSES, AlgoliaClient, TransientFetchError


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
        # scripts: list of _Resp or Exception instances (last one repeats).
        self._scripts = scripts
        self.calls = 0
        self.bodies = []
        self.headers = {}

    def post(self, url, json=None, timeout=None):
        i = min(self.calls, len(self._scripts) - 1)
        out = self._scripts[i]
        self.calls += 1
        self.bodies.append(json)
        if isinstance(out, Exception):
            raise out
        return out


@pytest.fixture
def config(monkeypatch):
    for k, v in {
        "ALGOLIA_APP_ID": "app-id",
        "ALGOLIA_API_KEY": "api-key",
        "ALGOLIA_INDEX": "idx",
        "ALGOLIA_URL": "https://example/queries",
        "OUTPUT_DIR": "./data/out",
        "RETRY_ATTEMPTS": "3",
        "RETRY_BACKOFF": "0",
        "REQUEST_TIMEOUT_SECONDS": "15",
    }.items():
        monkeypatch.setenv(k, v)
    from src.config import load_config

    return load_config()


def _ok_result():
    return {"results": [{"hits": [{"uuid": "u1"}], "nbPages": 1, "nbHits": 1, "page": 0}]}


def test_successful_request_returns_first_result_and_headers(config):
    session = _ScriptedSession([_Resp(_ok_result())])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("hitsPerPage=20&page=0", page=0)
    assert result == {"hits": [{"uuid": "u1"}], "nbPages": 1, "nbHits": 1, "page": 0}
    assert retried is False
    assert client.retry_count == 0
    # Session configured with Algolia auth headers exactly once.
    assert session.headers == {
        "X-Algolia-Application-Id": "app-id",
        "X-Algolia-API-Key": "api-key",
        "Content-Type": "application/json",
    }
    # Request body uses the configured index and supplied params verbatim.
    assert session.bodies[0] == {
        "requests": [{"indexName": "idx", "params": "hitsPerPage=20&page=0"}]
    }
    assert session.calls == 1


def test_retries_429_then_succeeds(config):
    session = _ScriptedSession([_Resp(None, status_code=429), _Resp(_ok_result())])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is not None
    assert retried is True
    assert client.retry_count == 1
    assert session.calls == 2


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_retries_5xx_then_succeeds(config, status):
    session = _ScriptedSession([_Resp(None, status_code=status), _Resp(_ok_result())])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is not None
    assert retried is True
    assert client.retry_count == 1


def test_retries_timeout_then_succeeds(config):
    session = _ScriptedSession([requests.Timeout("boom"), _Resp(_ok_result())])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is not None
    assert retried is True
    assert client.retry_count == 1


def test_retries_connection_error_then_succeeds(config):
    session = _ScriptedSession([requests.ConnectionError("down"), _Resp(_ok_result())])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is not None
    assert retried is True
    assert client.retry_count == 1


def test_non_transient_4xx_does_not_retry(config):
    session = _ScriptedSession([_Resp(None, status_code=404)])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is None
    assert retried is False
    assert client.retry_count == 0
    assert session.calls == 1


def test_retries_exhausted_returns_none(config):
    session = _ScriptedSession([requests.Timeout("boom")] * 5)
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is None
    assert retried is True
    assert client.retry_count == 3  # one per attempted retry


def test_empty_results_returns_none_without_retry(config):
    session = _ScriptedSession([_Resp({"results": []})])
    client = AlgoliaClient(config, session=session)
    result, retried = client.search("page=0", page=0)
    assert result is None
    assert retried is False
    assert session.calls == 1


def test_transient_status_set_is_rate_limit_and_server_errors():
    assert RETRYABLE_STATUSES == frozenset({429, 500, 502, 503, 504})
    with pytest.raises(TransientFetchError):
        raise TransientFetchError("HTTP 429")


def test_reset_retries_clears_counter(config):
    session = _ScriptedSession([requests.Timeout("boom"), _Resp(_ok_result())])
    client = AlgoliaClient(config, session=session)
    client.search("page=0", page=0)
    assert client.retry_count == 1
    client.reset_retries()
    assert client.retry_count == 0
