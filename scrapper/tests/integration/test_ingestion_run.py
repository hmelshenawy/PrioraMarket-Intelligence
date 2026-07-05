"""Integration test: US1 scoped ingestion run (T022, SC-001/002/003).

Runs the full pipeline against a fake marketplace adapter (no network)
and verifies: (a) normalized listings are produced with parity fields,
(b) a raw payload artifact is written per listing, (c) a run report with
basic metrics is emitted. Uses a temporary output directory.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from config.config import Config
from src.common.models import Scope
from src.ingestion.canonicalizer import Canonicalizer
from src.ingestion.normalizer import Normalizer
from src.ingestion.pipeline import IngestionPipeline
from src.marketplaces.adapter_interface import PageMetadata
from src.marketplaces.dubizzle.extractor import extract
from src.storage.csv_storage import CsvStorageAdapter


class _FakeAdapter:
    """Deterministic, offline adapter yielding RawListings from fixtures."""

    marketplace_name = "dubizzle"

    def __init__(self, hits, run_id="run-fake"):
        self._hits = hits
        self.scope = None
        self.retry_count = 0
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
        yield (raws, PageMetadata(page=0, hits_on_page=len(raws), nb_pages=1, nb_hits=len(raws)))


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


def test_scoped_run_produces_listings_raw_and_report(config):
    hit = load_fixture("sample_hit.json")
    adapter = _FakeAdapter([hit], run_id="run-it")
    storage = CsvStorageAdapter(config.output_dir, "run-it")
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    scope = Scope("dubizzle", "used", "toyota")
    result = pipeline.run(scope, "run-it")

    # (a) parity listing fields match the prototype extract() projection.
    assert result.report.state.value == "COMPLETED"
    assert len(result.accepted) == 1
    listing = result.accepted[0]
    assert listing.uuid == "sample-uuid-aaaa-bbbb-cccc"
    assert listing.make == "toyota"
    assert listing.model == "camry"
    assert listing.price == 85000.0
    assert listing.year == 2021
    assert listing.kilometers == 45000.0
    assert listing.fuel_type == "petrol"  # canonicalized
    assert listing.regional_spec == "gcc"  # canonicalized
    assert listing.body_type == "sedan"
    assert listing.canonicalization_version == "canonical-key-1"
    assert listing.source_url.startswith("https://dubai.dubizzle.com")
    assert listing.normalization_version == "norm-1"
    assert listing.dataset_version is not None
    assert listing.lineage["scrape_run_id"] == "run-it"

    # (b) raw payload artifact written, one line per listing, verbatim.
    raw_path = storage.raw_path()
    assert raw_path.exists()
    lines = raw_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    stored = json.loads(lines[0])
    assert stored["raw_payload"]["id"] == hit["id"]
    assert stored["raw_payload"]["uuid"] == hit["uuid"]

    # (c) run report with basic metrics.
    report_path = storage.report_path()
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["state"] == "COMPLETED"
    assert report["marketplace"] == "dubizzle"
    assert report["condition"] == "used"
    assert report["make"] == "toyota"
    assert report["pages_processed"] == 1
    assert report["listings_extracted"] == 1
    assert report["listings_skipped"] == 0
    assert report["dataset_version"] is not None
    assert report["normalization_version"] == "norm-1"

    # Listings CSV written.
    assert storage.listings_path().exists()
