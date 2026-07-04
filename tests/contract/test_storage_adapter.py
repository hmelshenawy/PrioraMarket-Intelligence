"""Contract test for the StorageAdapter interface (T033, US4).

Both the CSV adapter and the in-memory substitute MUST satisfy the
StorageAdapter protocol and behave identically for the operations the
ingestion pipeline relies on (write_raw, write_listings, write_report,
read_raw).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import Listing, RawListing, RunReport, RunState
from src.storage.csv_storage import CsvStorageAdapter
from src.storage.in_memory import InMemoryStorageAdapter
from src.storage.interface import StorageAdapter


def _raw():
    hit = load_fixture("sample_hit.json")
    return RawListing(
        marketplace="dubizzle",
        marketplace_listing_id="1",
        uuid="sample-uuid-aaaa-bbbb-cccc",
        raw_payload=hit,
        extracted_fields={"make": "Toyota"},
        fetched_at=datetime.now(timezone.utc),
        scrape_run_id="run-1",
        condition="used",
        make_slug="toyota",
    )


def _listing():
    return Listing(
        uuid="sample-uuid-aaaa-bbbb-cccc",
        marketplace="dubizzle",
        marketplace_listing_id="1",
        make="Toyota",
        price=85000.0,
        normalization_version="norm-1",
    )


def _report():
    return RunReport(
        run_id="run-1",
        state=RunState.COMPLETED,
        marketplace="dubizzle",
        condition="used",
        make="toyota",
        dataset_version="dataset_1",
        normalization_version="norm-1",
        pages_processed=1,
        listings_extracted=1,
    )


@pytest.fixture(params=["csv", "memory"])
def adapter(request, tmp_path):
    if request.param == "csv":
        return CsvStorageAdapter(tmp_path, "run-1")
    return InMemoryStorageAdapter()


def test_both_adapters_satisfy_protocol(adapter):
    assert isinstance(adapter, StorageAdapter)


def test_write_and_read_raw_roundtrip(adapter):
    n = adapter.write_raw([_raw()])
    assert n == 1
    read_back = list(adapter.read_raw())
    assert len(read_back) == 1
    assert read_back[0].uuid == "sample-uuid-aaaa-bbbb-cccc"
    # Verbatim payload preserved.
    assert read_back[0].raw_payload["id"] == load_fixture("sample_hit.json")["id"]


def test_write_listings_returns_count(adapter):
    n = adapter.write_listings([_listing()])
    assert n == 1


def test_write_report_persists(adapter):
    report = _report()
    adapter.write_report(report)
    # CSV stores on disk; memory stores on attribute. Both must retain it.
    if isinstance(adapter, InMemoryStorageAdapter):
        assert adapter.report is report
    else:
        import json

        data = json.loads(adapter.report_path().read_text(encoding="utf-8"))
        assert data["run_id"] == "run-1"
        assert data["state"] == "COMPLETED"


def test_read_raw_empty_when_none_written(adapter):
    # An adapter with no raw written yields nothing (not an error).
    if isinstance(adapter, InMemoryStorageAdapter):
        assert list(adapter.read_raw()) == []
    else:
        # CSV: read_raw on a fresh adapter dir yields nothing.
        assert list(adapter.read_raw()) == []
