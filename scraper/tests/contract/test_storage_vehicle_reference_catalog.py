from __future__ import annotations

from datetime import datetime, timezone

from src.common.models import (
    BackfillListingCandidate,
    NormalizationFieldStat,
    NormalizationStatisticsReport,
    VehicleReferenceCatalogRow,
)
from src.storage.in_memory import InMemoryStorageAdapter


def test_storage_vehicle_reference_catalog_contract() -> None:
    storage = InMemoryStorageAdapter()
    row = VehicleReferenceCatalogRow(
        id=None,
        market="global",
        make_key="mercedesbenz",
        make_display="Mercedes-Benz",
        model_key="cclass",
        model_display="C-Class",
        generation="W206",
        body_code="W206",
        start_year=2021,
        aliases={"make": ["Mercedes"], "model": ["C Class"]},
        confidence="manual",
    )

    report = storage.upsert_vehicle_reference_catalog([row], "fixture.csv")
    assert report.inserted == 1
    stored = storage.find_vehicle_reference_catalog("global", "mercedesbenz", "cclass")
    assert len(stored) == 1
    assert stored[0].make_display == row.make_display
    assert stored[0].source_file == "fixture.csv"
    assert stored[0].last_synced_at is not None


def test_storage_normalization_statistics_and_backfill_contract() -> None:
    storage = InMemoryStorageAdapter()
    stats = NormalizationStatisticsReport(
        operation="ingestion",
        market="global",
        canonicalization_version="canonical-v1",
        created_at=datetime.now(timezone.utc),
        stats=[
            NormalizationFieldStat(
                market="global",
                field_name="make",
                raw_value="Unknown Make",
                canonical_key="unknownmake",
                known=False,
            )
        ],
    )
    candidate = BackfillListingCandidate(
        id=10,
        source="dubizzle",
        uuid="dubizzle-10",
        canonical_payload={"make": "Mercedes Benz"},
    )

    storage.write_normalization_statistics(stats)
    storage.backfill_candidates.append(candidate)

    assert storage.normalization_statistics == [stats]
    assert list(storage.read_listing_backfill_candidates(batch_size=1)) == [candidate]
