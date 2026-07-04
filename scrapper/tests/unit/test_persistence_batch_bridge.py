from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.common.models import Listing, PersistOutcome, RawListing, RunReport, RunState, Scope
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

    def begin_run(self, scope, config_snapshot, run_started_at, marketplace_source_code):
        self.begun.append((scope, config_snapshot, run_started_at, marketplace_source_code))
        return _Ctx(scope=scope)

    def persist_listing(self, ctx, raw, listing):
        self.persisted.append((ctx, raw, listing))
        return PersistOutcome(created=True)

    def finalize_run(self, ctx, report):
        self.finalized.append((ctx, report))


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
