"""Integration test: env-driven config + storage substitutability (T037).

SC-007 (configurable, secret-free pipeline) and SC-008 (storage pluggable).
Drives the pipeline with configuration supplied entirely through env vars
(no code edits) and confirms feature flags take effect, then substitutes
an in-memory storage adapter behind the interface with ingestion logic
unchanged.
"""

from __future__ import annotations

import importlib
from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import Scope
from src.ingestion.canonicalizer import Canonicalizer
from src.ingestion.normalizer import Normalizer
from src.ingestion.pipeline import IngestionPipeline
from src.marketplaces.adapter_interface import PageMetadata
from src.marketplaces.dubizzle.extractor import extract
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


def _env(monkeypatch, **overrides):
    base = {
        "ALGOLIA_APP_ID": "x",
        "ALGOLIA_API_KEY": "k",
        "ALGOLIA_INDEX": "idx",
        "ALGOLIA_URL": "https://example/queries",
        "OUTPUT_DIR": "./data/out",
        "HITS_PER_PAGE": "20",
        "MAX_PAGES": "500",
        "RETRY_ATTEMPTS": "3",
        "RETRY_BACKOFF": "1.5",
        "RATE_LIMIT_MIN_SECONDS": "0",
        "RATE_LIMIT_MAX_SECONDS": "0",
        "REQUEST_TIMEOUT_SECONDS": "15",
        "NORMALIZATION_VERSION": "norm-1",
        "ENABLE_VALIDATION": "true",
        "ENABLE_CANONICALIZATION": "true",
        "ENABLE_REPLAY": "true",
        "ENABLE_STRUCTURED_LOGGING": "false",
        "ENABLE_CSV_STORAGE": "true",
    }
    base.update(overrides)
    for k, v in base.items():
        monkeypatch.setenv(k, v)


def test_fail_fast_on_missing_required_value(monkeypatch):
    _env(monkeypatch)
    monkeypatch.delenv("ALGOLIA_API_KEY", raising=False)
    from config import config as config_mod

    importlib.reload(config_mod)
    # Use a non-existent env path so the project's real .env (CWD) is NOT
    # loaded back in to satisfy the missing required value.
    with pytest.raises(config_mod.ConfigurationError) as exc:
        config_mod.load_config(env_path="does-not-exist.env")
    assert "ALGOLIA_API_KEY" in str(exc.value)


def test_env_driven_config_loads_all_feature_flags(monkeypatch):
    _env(monkeypatch, ENABLE_CANONICALIZATION="false", ENABLE_STRUCTURED_LOGGING="false")
    from config import config as config_mod

    importlib.reload(config_mod)
    cfg = config_mod.load_config()
    assert cfg.enable_canonicalization is False
    assert cfg.enable_structured_logging is False
    assert cfg.enable_validation is True
    assert cfg.enable_csv_storage is True
    assert cfg.normalization_version == "norm-1"
    # Snapshot excludes secrets.
    snap = cfg.snapshot()
    assert "algolia_api_key" not in snap
    assert "algolia_app_id" not in snap


def test_feature_flag_disables_canonicalization(monkeypatch):
    _env(monkeypatch, ENABLE_CANONICALIZATION="false")
    from config import config as config_mod

    importlib.reload(config_mod)
    cfg = config_mod.load_config()

    hit = load_fixture("sample_hit.json")
    adapter = _FakeAdapter([hit], run_id="run-flag")
    storage = InMemoryStorageAdapter()
    pipeline = IngestionPipeline(
        cfg,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    result = pipeline.run(Scope("dubizzle", "used", "toyota"), "run-flag")
    listing = result.accepted[0]
    # With canonicalization disabled, fuel/spec stay as the raw extracted form.
    assert listing.fuel_type == "Petrol"
    assert listing.regional_spec == "GCC Specs"


def test_storage_substitutability_in_memory(monkeypatch):
    _env(monkeypatch)
    from config import config as config_mod

    importlib.reload(config_mod)
    cfg = config_mod.load_config()

    hit = load_fixture("sample_hit.json")
    adapter = _FakeAdapter([hit], run_id="run-sub")
    storage = InMemoryStorageAdapter()
    pipeline = IngestionPipeline(
        cfg,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    result = pipeline.run(Scope("dubizzle", "used", "toyota"), "run-sub")
    assert result.report.state.value == "COMPLETED"
    assert len(storage.listings) == 1
    assert len(storage.raw) == 1
    assert storage.report.run_id == "run-sub"
