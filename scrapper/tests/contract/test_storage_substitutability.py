"""Storage substitutability proof (T036, US4, SC-008).

Runs the same ingestion scope through the pipeline twice — once with the
CSV adapter, once with the in-memory substitute — and asserts the
accepted Listings are identical. Ingestion logic must be unaffected by
the storage backend.
"""

from __future__ import annotations

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
from src.storage.in_memory import InMemoryStorageAdapter


class _FakeAdapter:
    marketplace_name = "dubizzle"
    retry_count = 0

    def __init__(self, hits, run_id):
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


def _run_pipeline(config, storage, run_id):
    hit = load_fixture("sample_hit.json")
    adapter = _FakeAdapter([hit], run_id=run_id)
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    return pipeline.run(Scope("dubizzle", "used", "toyota"), run_id)


def test_csv_and_in_memory_produce_identical_listings(config, tmp_path):
    csv_storage = CsvStorageAdapter(tmp_path, "run-csv")
    mem_storage = InMemoryStorageAdapter()

    csv_result = _run_pipeline(config, csv_storage, "run-csv")
    mem_result = _run_pipeline(config, mem_storage, "run-mem")

    csv_ls = csv_result.accepted
    mem_ls = mem_result.accepted
    assert len(csv_ls) == len(mem_ls) == 1
    # Core derived fields identical regardless of storage backend.
    a, b = csv_ls[0], mem_ls[0]
    for attr in (
        "uuid",
        "make",
        "model",
        "price",
        "year",
        "kilometers",
        "fuel_type",
        "regional_spec",
        "body_type",
        "normalization_version",
    ):
        assert getattr(a, attr) == getattr(b, attr), attr
    # Counts identical.
    assert csv_result.report.listings_extracted == mem_result.report.listings_extracted
    assert csv_result.report.listings_skipped == mem_result.report.listings_skipped
    # In-memory retained the raw + report.
    assert len(mem_storage.raw) == 1
    assert mem_storage.report is not None
    assert mem_storage.report.state.value == "COMPLETED"
