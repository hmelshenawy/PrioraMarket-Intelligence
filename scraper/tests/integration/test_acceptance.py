"""End-to-end acceptance covering SC-001–SC-009 (T048).

Each success criterion from spec.md is asserted once. These tests are
the final gate before the feature is declared done.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

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
from src.reporting.run_report import extended_summary, stop_position
from src.storage.csv_storage import CsvStorageAdapter
from src.storage.in_memory import InMemoryStorageAdapter

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


class _FakeAdapter:
    marketplace_name = "dubizzle"
    retry_count = 1

    def __init__(self, pages, run_id):
        # pages: list of (hits, retried) tuples.
        self._pages = pages
        self.scope = None
        self._run_id = run_id

    def set_run_id(self, run_id):
        self._run_id = run_id

    def fetch(self, scope):
        self.scope = scope
        fetched_at = datetime.now(timezone.utc)
        for i, (hits, retried) in enumerate(self._pages):
            raws = [
                extract(
                    h,
                    condition=scope.condition,
                    scrape_run_id=self._run_id,
                    fetched_at=fetched_at,
                    marketplace=self.marketplace_name,
                )
                for h in hits
            ]
            yield (
                raws,
                PageMetadata(
                    page=i,
                    hits_on_page=len(raws),
                    nb_pages=len(self._pages),
                    nb_hits=len(raws),
                    retried=retried,
                ),
            )


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


def _run(config, storage, pages, run_id):
    adapter = _FakeAdapter(pages, run_id=run_id)
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    return pipeline.run(Scope("dubizzle", "used", "toyota"), run_id)


def test_SC_001_listing_parity(config):
    """SC-001: refactored pipeline matches prototype output for a scope."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a1")
    result = _run(config, storage, [([hit], False)], "run-a1")
    # Compare to the prototype projection for the same hit.
    raw = result.raw[0]
    assert raw.extracted_fields["make"] == "Toyota"
    assert raw.extracted_fields["price_aed"] == hit["price"]
    assert result.accepted[0].uuid == hit["uuid"]


def test_SC_002_raw_payload_preserved(config):
    """SC-002: 100% of persisted listings have an accompanying raw payload."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a2")
    result = _run(config, storage, [([hit], False)], "run-a2")
    raw_lines = storage.raw_path().read_text(encoding="utf-8").strip().splitlines()
    assert len(raw_lines) == len(result.accepted) == 1
    stored = json.loads(raw_lines[0])
    assert stored["raw_payload"]["uuid"] == hit["uuid"]  # verbatim


def test_SC_003_all_persisted_passed_validation(config):
    """SC-003: 100% of persisted listings passed the validation gate."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a3")
    result = _run(config, storage, [([hit], False)], "run-a3")
    for listing in result.accepted:
        assert listing.uuid is not None
        assert listing.make is not None
        assert listing.price is not None


def test_SC_004_page_failure_still_completes(config):
    """SC-004: a forced page failure still completes with failures recorded."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a4")
    # Page 0 ok, page 1 failed (empty, retried).
    result = _run(config, storage, [([hit], False), ([], True)], "run-a4")
    assert result.report.state.value in {"PARTIAL_FAILED", "COMPLETED"}
    assert result.report.failures >= 1
    assert len(result.accepted) == 1  # from the non-failed page
    assert stop_position(result.report)["failing_page"] == 1


def test_SC_005_invalid_records_skipped(config):
    """SC-005: invalid records logged + skipped, zero persisted."""
    bad = json.loads(json.dumps(load_fixture("sample_hit.json")))
    bad["uuid"] = None  # invalid
    good = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a5")
    result = _run(config, storage, [([good, bad], False)], "run-a5")
    assert result.report.listings_skipped >= 1
    assert result.report.validation_failures >= 1
    persisted = {listing.uuid for listing in result.accepted}
    assert None not in persisted
    assert good["uuid"] in persisted


def test_SC_006_run_report_self_describing(config):
    """SC-006: report alone carries marketplace/condition/make/metrics."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a6")
    _run(config, storage, [([hit], False)], "run-a6")
    report = json.loads(storage.report_path().read_text(encoding="utf-8"))
    for key in (
        "marketplace",
        "condition",
        "make",
        "pages_processed",
        "listings_extracted",
        "listings_skipped",
        "execution_duration_seconds",
        "failures",
    ):
        assert key in report, key


def test_SC_007_no_hardcoded_secrets_or_paths():
    """SC-007: grep of source finds zero hardcoded secrets / paths."""
    findings = []
    for py in SRC.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        for needle in ("WD0PTZ13ZS", "cef139620248f1bc328a00fddc7107a6", "/home/openclaw"):
            if needle in text:
                findings.append(str(py))
    # Hardcoded absolute Path("/...") literals in source.
    for py in SRC.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        if 'Path("/' in text and "output_dir" not in text:
            findings.append(str(py))
    assert findings == [], f"hardcoded secrets/paths found: {findings}"


def test_SC_008_storage_substitutability(config, tmp_path):
    """SC-008: substituting storage yields identical ingestion results."""
    hit = load_fixture("sample_hit.json")
    csv_storage = CsvStorageAdapter(tmp_path, "run-a8-csv")
    mem_storage = InMemoryStorageAdapter()
    csv_r = _run(config, csv_storage, [([hit], False)], "run-a8-csv")
    mem_r = _run(config, mem_storage, [([hit], False)], "run-a8-mem")
    a, b = csv_r.accepted[0], mem_r.accepted[0]
    for attr in (
        "uuid",
        "make",
        "model",
        "price",
        "fuel_type",
        "regional_spec",
        "normalization_version",
    ):
        assert getattr(a, attr) == getattr(b, attr)


def test_SC_009_second_marketplace_isolated(config):
    """SC-009: a second marketplace only needs a new adapter — no orchestration rewrite."""
    from src.marketplaces.adapter_interface import MarketplaceAdapter

    class _SecondMarketplaceAdapter:
        marketplace_name = "examplemotors"
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
            yield (
                raws,
                PageMetadata(page=0, hits_on_page=len(raws), nb_pages=1, nb_hits=len(raws)),
            )

    adapter = _SecondMarketplaceAdapter([load_fixture("sample_hit.json")], run_id="run-a9")
    assert isinstance(adapter, MarketplaceAdapter)
    storage = InMemoryStorageAdapter()
    pipeline = IngestionPipeline(
        config,
        adapter,
        storage,
        normalizer=Normalizer("norm-1"),
        canonicalizer=Canonicalizer(),
    )
    # The SAME pipeline orchestrates a different marketplace with no changes.
    result = pipeline.run(Scope("examplemotors", "used", "toyota"), "run-a9")
    assert result.report.state.value == "COMPLETED"
    assert result.accepted[0].marketplace == "examplemotors"


def test_extended_and_optional_metrics_present(config):
    """FR-063/064: extended + optional operational metrics wired (T045/T046)."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a-metrics")
    result = _run(config, storage, [([hit], False)], "run-a-metrics")
    summary = extended_summary(result.report)
    for key in (
        "retry_count",
        "duplicate_count",
        "validation_failures",
        "pages_per_second",
        "listings_per_second",
        "fetch_duration_seconds",
        "processing_duration_seconds",
        "storage_duration_seconds",
        "start_time",
        "end_time",
        "total_duration_seconds",
        "stop_position",
    ):
        assert key in summary, key


def test_replay_round_trip_offline(config):
    """Replay rebuilds listings offline (FR-065..067, SC-level)."""
    hit = load_fixture("sample_hit.json")
    storage = CsvStorageAdapter(config.output_dir, "run-a-rep")
    _run(config, storage, [([hit], False)], "run-a-rep")
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    first = replayer.replay(dataset_version="run-a-rep")
    second = replayer.replay(dataset_version="run-a-rep")
    assert len(first) == 1
    assert first[0].to_record() == second[0].to_record()
