"""Contract test for the MarketplaceAdapter interface (FR-010..015, T010).

A conforming adapter MUST: yield (listings, metadata) tuples, preserve
the raw payload verbatim in each RawListing, expose marketplace_name, and
cap pagination. The DubizzleAdapter is exercised against a stubbed HTTP
session so no network access is required.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import RawListing, Scope
from src.marketplaces.adapter_interface import MarketplaceAdapter, PageMetadata
from src.marketplaces.dubizzle.adapter import DubizzleAdapter
from src.marketplaces.dubizzle.extractor import extract


class _StubResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class _StubSession:
    """Records requests and returns canned Algolia results."""

    def __init__(self, pages):
        # pages: list of result dicts (the [0] element of results).
        self._pages = pages
        self.calls = []
        self.headers = {}

    def post(self, url, json=None, timeout=None):
        self.calls.append({"url": url, "body": json, "timeout": timeout})
        idx = min(len(self.calls) - 1, len(self._pages) - 1)
        return _StubResponse({"results": [self._pages[idx]]})


@pytest.fixture
def sample_hit():
    return load_fixture("sample_hit.json")


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
        "RATE_LIMIT_MIN_SECONDS": "0",
        "RATE_LIMIT_MAX_SECONDS": "0",
        "RETRY_BACKOFF": "0",
    }.items():
        monkeypatch.setenv(k, v)
    from config.config import load_config

    return load_config()


def test_extractor_preserves_raw_payload_verbatim(sample_hit):
    raw = extract(
        sample_hit,
        condition="used",
        scrape_run_id="run-1",
        fetched_at=datetime.now(timezone.utc),
    )
    assert isinstance(raw, RawListing)
    # Verbatim ground truth: the exact dict object passed in is preserved.
    assert raw.raw_payload is sample_hit
    assert raw.uuid == "sample-uuid-aaaa-bbbb-cccc"
    assert raw.extracted_fields["make"] == "Toyota"
    assert raw.extracted_fields["model"] == "Camry"
    assert raw.extracted_fields["url"].startswith("https://dubai.dubizzle.com")
    assert raw.extracted_fields["fuel"] == "Petrol"
    assert raw.extracted_fields["specs"] == "GCC Specs"


def test_dubizzle_adapter_satisfies_protocol(config):
    adapter = DubizzleAdapter(config, session=_StubSession([]))
    assert isinstance(adapter, MarketplaceAdapter)
    assert adapter.marketplace_name == "dubizzle"


def test_dubizzle_adapter_yields_rawlistings_and_metadata(config, sample_hit):
    page0 = {"hits": [sample_hit], "nbPages": 1, "nbHits": 1, "page": 0}
    session = _StubSession([page0])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-test")
    scope = Scope("dubizzle", "used", "toyota")

    out = list(adapter.fetch(scope))
    assert len(out) == 1
    listings, meta = out[0]
    assert isinstance(meta, PageMetadata)
    assert meta.page == 0
    assert meta.nb_pages == 1
    assert meta.nb_hits == 1
    assert len(listings) == 1
    assert isinstance(listings[0], RawListing)
    assert listings[0].raw_payload is sample_hit  # verbatim


def test_dubizzle_adapter_pagination_cap(config, sample_hit, monkeypatch):
    # 1000 reported pages, cap must clamp to MAX_PAGES (500).
    page0 = {"hits": [sample_hit], "nbPages": 1000, "nbHits": 1000, "page": 0}
    page1 = {"hits": [sample_hit], "nbPages": 1000, "nbHits": 1000, "page": 1}
    session = _StubSession([page0, page1])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-cap")
    scope = Scope("dubizzle", "used", "toyota")
    # Monkeypatch rate limit + backoff to 0 for speed.
    out = list(adapter.fetch(scope))
    assert out[0][1].nb_pages == 500


def test_dubizzle_adapter_zero_hits_short_circuits(config):
    page0 = {"hits": [], "nbPages": 0, "nbHits": 0, "page": 0}
    session = _StubSession([page0])
    adapter = DubizzleAdapter(config, session=session)
    adapter.set_run_id("run-empty")
    scope = Scope("dubizzle", "used", "toyota")
    out = list(adapter.fetch(scope))
    assert len(out) == 1
    assert out[0][1].nb_hits == 0
    assert out[0][0] == []
