from __future__ import annotations

from pathlib import Path

from src.common.models import CatalogSyncReport
from src.db import seed_vehicle_catalog


def test_seed_vehicle_catalog_delegates_to_vehicle_reference_sync(monkeypatch) -> None:
    calls = []

    def fake_apply(database_url: str) -> None:
        calls.append(("apply", database_url))

    def fake_create_pool(settings):
        calls.append(("pool", settings.database_url))
        return object()

    class FakeStorage:
        def __init__(self, pool):
            calls.append(("storage", pool is not None))

    def fake_sync(storage, path: Path):
        calls.append(("sync", path.name, storage.__class__.__name__))
        return CatalogSyncReport(source_file=path.name, inserted=1)

    monkeypatch.setattr(seed_vehicle_catalog, "apply_migrations", fake_apply)
    monkeypatch.setattr(seed_vehicle_catalog, "create_pool", fake_create_pool)
    monkeypatch.setattr(seed_vehicle_catalog, "PostgresStorageAdapter", FakeStorage)
    monkeypatch.setattr(seed_vehicle_catalog, "synchronize_vehicle_reference_catalog", fake_sync)

    report = seed_vehicle_catalog.import_vehicle_catalog(Path("catalog.csv"), "postgres://db")

    assert report.inserted == 1
    assert calls == [
        ("apply", "postgres://db"),
        ("pool", "postgres://db"),
        ("storage", True),
        ("sync", "catalog.csv", "FakeStorage"),
    ]
