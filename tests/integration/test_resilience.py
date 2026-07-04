"""Integration test: US2 resilient ingestion with partial-failure (T027).

Forces a failed page mid-run and verifies the run completes, the failed
page is recorded in the run report's failures, listings from successful
pages are still produced, and the terminal state is PARTIAL_FAILED.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import Scope
from config.config import Config
from src.ingestion.canonicalizer import Canonicalizer
from src.ingestion.normalizer import Normalizer
from src.ingestion.pipeline import IngestionPipeline
from marketplaces.adapter_interface import PageMetadata
from marketplaces.dubizzle.extractor import extract
from src.storage.csv_storage import CsvStorageAdapter


class _ResilientFakeAdapter:
    """Yields one good page, then one failed (empty, retried) page."""

    marketplace_name = "dubizzle"
    retry_count = 2

    def __init__(self, hits, run_id="run-resilient"):
        self._hits = hits
        self.scope = None
        self._run_id = run_id

    def set_run_id(self, run_id):
        self._run_id = run_id

    def fetch(self, scope):
        self.scope = scope
        fetched_at = datetime.now(timezone.utc)
        raws = [
            extract(
                h,
                condition=scope.condition,
                scrape_run_id=self._run_id,
                fetched_at=fetched_at,
                marketplace=self.marketplace_name,
            )
            for h in self._hits
        ]
        # Page 0: success.
        yield (
            raws,
            PageMetadata(page=0, hits_on_page=len(raws), nb_pages=2, nb_hits=len(raws) + 5),
        )
        # Page 1: failed after retries (empty, retried=True).
        yield ([], PageMetadata(page=1, hits_on_page=0, retried=True))


@pytest.fixture
def config(tmp_path):
    return Config(
        algolia_app_id="x",
        algolia_api_key="k",
        algolia_index="idx",
        algolia_url="https://example/queries",
        hits_per_page=20,
        max_pages=500,
        output_dir=tmp_path,
        retry_attempts=3,
        retry_backoff=1.5,
        rate_limit_min_seconds=0.0,
        rate_limit_max_seconds=0.0,
        request_timeout_seconds=15.0,
        normalization_version="norm-1",
        enable_validation=True,
        enable_canonicalization=True,
        enable_replay=True,
        enable_structured_logging=False,
        enable_csv_storage=True,
    )


def test_failed_page_does_not_terminate_run(config):
    hit = load_fixture("sample_hit.json")
    adapter = _ResilientFakeAdapter([hit], run_id="run-res")
    storage = CsvStorageAdapter(config.output_dir, "run-res")
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    result = pipeline.run(Scope("dubizzle", "used", "toyota"), "run-res")

    # Run completed (not FAILED); terminal state reflects partial failure.
    assert result.report.state.value in {"PARTIAL_FAILED", "COMPLETED"}
    assert result.report.failures >= 1
    # Listings from the successful page are still produced.
    assert len(result.accepted) == 1
    assert result.report.listings_extracted == 1
    # Both pages were processed.
    assert result.report.pages_processed == 2
    # Stop-position recorded.
    assert result.report.failing_page == 1
    assert result.report.last_successful_page == 0

    report = json.loads(storage.report_path().read_text(encoding="utf-8"))
    assert report["failures"] >= 1
    assert report["failing_page"] == 1
    assert report["last_successful_page"] == 0
    # Retry count surfaced from adapter.
    assert report["retry_count"] == 2


def test_record_level_failure_isolated(config):
    # A normalizer that throws on one record should not kill the run.
    hit = load_fixture("sample_hit.json")
    adapter = _ResilientFakeAdapter([hit], run_id="run-rec")
    storage = CsvStorageAdapter(config.output_dir, "run-rec")

    class _BoomNormalizer(Normalizer):
        def normalize(self, raw, scope):
            if raw.uuid == "sample-uuid-aaaa-bbbb-cccc":
                raise ValueError("boom")
            return super().normalize(raw, scope)

    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=_BoomNormalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    result = pipeline.run(Scope("dubizzle", "used", "toyota"), "run-rec")
    # The failing record was skipped, not fatal.
    assert result.report.listings_skipped >= 1
    assert result.report.state.value in {"PARTIAL_FAILED", "COMPLETED"}
    assert result.report.failing_stage == "normalizing"
