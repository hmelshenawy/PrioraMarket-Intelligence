from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.common.models import Listing, PersistOutcome, RawListing, RunReport, RunState, Scope
from src.config.config import Config
from src.ingestion.pipeline import IngestionPipeline
from src.marketplaces.adapter_interface import PageMetadata
from src.persistence.batch_bridge import PersistenceBatchBridge


def _raw(uuid: str, marketplace: str = "dubizzle") -> RawListing:
    return RawListing(
        marketplace=marketplace,
        marketplace_listing_id=uuid,
        uuid=uuid,
        raw_payload={"id": uuid},
        extracted_fields={},
        fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        scrape_run_id="run-1",
        condition="used",
        make_slug="toyota",
    )


def _listing(uuid: str, marketplace: str = "dubizzle") -> Listing:
    return Listing(
        uuid=uuid,
        marketplace=marketplace,
        marketplace_listing_id=uuid,
        make="Toyota",
        normalization_version="norm-1",
    )


def _report() -> RunReport:
    return RunReport(
        run_id="run-1",
        state=RunState.COMPLETED,
        marketplace="dubizzle",
        condition="used",
        make="toyota",
        dataset_version=None,
        normalization_version="norm-1",
        listings_extracted=1,
    )


@dataclass
class _Ctx:
    run_id: int = 10
    run_name: str = "run_dubizzle_used_toyota_20260704_090000"
    marketplace_source_id: int = 1
    scope: Scope = field(default_factory=lambda: Scope("dubizzle", "used", "toyota"))


class _FakeService:
    def __init__(self) -> None:
        self.begun = []
        self.persisted = []
        self.finalized = []
        self.normalization_statistics = []

    def begin_run(self, scope, config_snapshot, run_started_at, marketplace_source_code):
        self.begun.append((scope, config_snapshot, run_started_at, marketplace_source_code))
        return _Ctx(scope=scope)

    def persist_listing(self, ctx, raw, listing):
        self.persisted.append((ctx, raw, listing))
        return PersistOutcome(created=True)

    def finalize_run(self, ctx, report):
        self.finalized.append((ctx, report))

    def write_normalization_statistics(self, report):
        self.normalization_statistics.append(report)


class _PipelineAdapter:
    retry_count = 0

    def fetch(self, scope):
        yield [
            RawListing(
                marketplace=scope.marketplace,
                marketplace_listing_id="uuid-1",
                uuid="uuid-1",
                raw_payload={"id": "uuid-1", "make": "Mercedes-Benz"},
                extracted_fields={
                    "uuid": "uuid-1",
                    "make": "Mercedes-Benz",
                    "model": "C-Class",
                    "price_aed": 100000,
                    "fuel": "Gasoline",
                    "trim": "AMG Line",
                },
                fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
                scrape_run_id="run-1",
                condition=scope.condition,
                make_slug=scope.make,
            )
        ], PageMetadata(page=0, hits_on_page=1, nb_pages=1, nb_hits=1)


def _config() -> Config:
    return Config(
        algolia_app_id="x",
        algolia_api_key="x",
        algolia_index="idx",
        algolia_url="https://example.test",
        hits_per_page=20,
        max_pages=1,
        output_dir=".",
        retry_attempts=1,
        retry_backoff=0,
        rate_limit_min_seconds=0,
        rate_limit_max_seconds=0,
        request_timeout_seconds=1,
        normalization_version="norm-1",
        enable_validation=True,
        enable_canonicalization=True,
        enable_replay=True,
        enable_structured_logging=False,
        enable_csv_storage=True,
        storage_backend="postgres",
    )


def test_bridge_pairs_raw_and_listing_by_source_uuid() -> None:
    service = _FakeService()
    bridge = PersistenceBatchBridge(
        service=service,
        scope=Scope("dubizzle", "used", "toyota"),
        config_snapshot={"storage_backend": "postgres"},
        run_started_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        marketplace_source_code="dubizzle_uae",
    )

    assert bridge.write_raw([_raw("uuid-1")]) == 1
    assert bridge.write_listings([_listing("uuid-1")]) == 1
    bridge.write_report(_report())

    assert len(service.persisted) == 1
    assert service.persisted[0][1].uuid == "uuid-1"
    assert service.persisted[0][2].uuid == "uuid-1"
    assert service.finalized[0][1].failures == 0


def test_bridge_reports_unmatched_records_without_persisting_them() -> None:
    service = _FakeService()
    bridge = PersistenceBatchBridge(
        service=service,
        scope=Scope("dubizzle", "used", "toyota"),
        config_snapshot={},
        run_started_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        marketplace_source_code="dubizzle_uae",
    )

    bridge.write_raw([_raw("raw-only"), _raw("matched")])
    bridge.write_listings([_listing("listing-only"), _listing("matched")])
    report = _report()
    bridge.write_report(report)

    assert [item[1].uuid for item in service.persisted] == ["matched"]
    assert bridge.unmatched_raw_keys == [("dubizzle", "raw-only")]
    assert bridge.unmatched_listing_keys == [("dubizzle", "listing-only")]
    assert report.failures == 2
    assert report.listings_skipped == 2


def test_bridge_calls_begin_and_finalize_once() -> None:
    service = _FakeService()
    started = datetime(2026, 7, 4, tzinfo=timezone.utc)
    bridge = PersistenceBatchBridge(
        service=service,
        scope=Scope("dubizzle", "used", "toyota"),
        config_snapshot={"a": 1},
        run_started_at=started,
        marketplace_source_code="dubizzle_uae",
    )

    bridge.write_raw([_raw("uuid-1")])
    bridge.write_listings([_listing("uuid-1")])
    bridge.write_report(_report())

    assert len(service.begun) == 1
    assert service.begun[0][2] is started
    assert service.begun[0][3] == "dubizzle_uae"
    assert len(service.finalized) == 1


def test_pipeline_emits_normalization_statistics_through_bridge() -> None:
    service = _FakeService()
    scope = Scope("dubizzle", "used", "mercedes-benz")
    bridge = PersistenceBatchBridge(
        service=service,
        scope=scope,
        config_snapshot={"storage_backend": "postgres"},
        run_started_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        marketplace_source_code="dubizzle_uae",
    )
    pipeline = IngestionPipeline(_config(), _PipelineAdapter(), bridge)

    result = pipeline.run(scope, "run-1")

    assert result.report.state.value == "COMPLETED"
    assert len(service.normalization_statistics) == 1
    report = service.normalization_statistics[0]
    assert report.canonicalization_version == "canonical-key-1"
    assert any(stat.field_name == "make" for stat in report.stats)
    assert len(service.persisted) == 1
