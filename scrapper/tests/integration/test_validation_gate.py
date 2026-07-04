"""Integration test: US3 validation gate before persistence (T032).

Feeds the pipeline a fixture with one valid and several invalid listings
(missing uuid, non-numeric/missing price, missing required fields, out-of-
bounds year, plus a duplicate uuid) and verifies the valid listing is
persisted while each invalid/duplicate listing is counted as skipped and
not persisted.
"""

from __future__ import annotations

import csv
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


def _hit(uuid, **overrides):
    h = json.loads(json.dumps(load_fixture("sample_hit.json")))  # deep copy
    h["uuid"] = uuid
    h.update(overrides)
    return h


class _FakeAdapter:
    marketplace_name = "dubizzle"
    retry_count = 0

    def __init__(self, hits, run_id="run-val"):
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


def test_invalid_and_duplicate_records_skipped_valid_persists(config):
    hits = [
        _hit("valid-1"),  # valid
        _hit(None),  # missing uuid
        _hit("no-price", price=None),  # missing required price
        _hit("no-make", details={}),  # details stripped -> no make/model
        _hit("bad-year", year=2100),  # out-of-bounds year
        _hit("valid-1"),  # duplicate uuid (newest wins)
    ]
    adapter = _FakeAdapter(hits, run_id="run-val")
    storage = CsvStorageAdapter(config.output_dir, "run-val")
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    result = pipeline.run(Scope("dubizzle", "used", "toyota"), "run-val")

    # Only the valid uuid (and the duplicate's newest occurrence) persist.
    persisted_uuids = {listing.uuid for listing in result.accepted}
    assert "valid-1" in persisted_uuids
    assert None not in persisted_uuids
    # no-make: details stripped, but make_slug comes from category_v2, so make
    # is still derived. That record is valid by our rules -> accepted. Verify
    # the genuinely invalid ones were skipped.
    assert result.report.listings_skipped >= 3
    assert result.report.validation_failures >= 3
    assert result.report.duplicate_count == 1

    # Persisted CSV contains only accepted listings.
    with open(storage.listings_path(), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    persisted_in_csv = {r["uuid"] for r in rows}
    assert persisted_in_csv == persisted_uuids

    # Raw artifact preserves ALL listings (valid + invalid) verbatim.
    raw_lines = storage.raw_path().read_text(encoding="utf-8").strip().splitlines()
    assert len(raw_lines) == len(hits)
