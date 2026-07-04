"""Integration test: US5 offline deterministic replay (T042).

Runs a live ingestion to populate stored RawListings, then replays them
with an explicit Normalization Version and verifies: (a) Listings are
rebuilt with no marketplace access, (b) results are identical on a second
replay, (c) RawListings are unchanged.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import Scope
from src.config.config import Config
from src.ingestion.canonicalizer import Canonicalizer
from src.ingestion.normalizer import Normalizer
from src.ingestion.pipeline import IngestionPipeline
from src.marketplaces.adapter_interface import PageMetadata
from src.marketplaces.dubizzle.extractor import extract
from src.replay.replayer import Replayer
from src.storage.csv_storage import CsvStorageAdapter


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


def test_replay_rebuilds_offline_deterministically(config):
    # 1. Live run to populate raw storage.
    hit = load_fixture("sample_hit.json")
    run_id = "run-replay-src"
    adapter = _FakeAdapter([hit], run_id=run_id)
    storage = CsvStorageAdapter(config.output_dir, run_id)
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    live = pipeline.run(Scope("dubizzle", "used", "toyota"), run_id)
    assert live.report.state.value == "COMPLETED"

    # Snapshot raw payload to prove immutability through replay.
    raw_before = storage.raw_path().read_text(encoding="utf-8")

    # 2. Replay with explicit version, reading via read_raw.
    replayer = Replayer(
        storage=storage,  # reads from the live run's dir
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    first = replayer.replay(dataset_version=run_id)
    second = replayer.replay(dataset_version=run_id)

    # (a) Listings rebuilt, no marketplace access (Replayer has no adapter).
    assert len(first) == 1
    assert first[0].make == "Toyota"
    assert first[0].fuel_type == "Petrol"
    assert first[0].normalization_version == "norm-1"

    # (b) Deterministic: identical across runs.
    assert len(first) == len(second)
    for a, b in zip(first, second):
        assert a.to_record() == b.to_record()

    # (c) RawListings unchanged on disk.
    assert storage.raw_path().read_text(encoding="utf-8") == raw_before


def test_replay_with_different_normalization_version(config):
    hit = load_fixture("sample_hit.json")
    run_id = "run-replay-v2"
    adapter = _FakeAdapter([hit], run_id=run_id)
    storage = CsvStorageAdapter(config.output_dir, run_id)
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    pipeline.run(Scope("dubizzle", "used", "toyota"), run_id)

    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-2",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    listings = replayer.replay(dataset_version=run_id)
    assert len(listings) == 1
    # Explicit version is stamped on the replayed Listings.
    assert listings[0].normalization_version == "norm-2"
