"""Schema migrations (yoyo). Invoked via the ``migrate`` CLI command."""

from __future__ import annotations

from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "store" / "migrations"


class MigrationError(Exception):
    """Raised when migration tooling fails."""


def _backend(database_url: str):
    try:
        from yoyo import get_backend, read_migrations
    except Exception as exc:  # pragma: no cover - dependency/environment failure
        raise MigrationError("yoyo-migrations is not installed") from exc
    return get_backend(database_url), read_migrations(str(MIGRATIONS_DIR))


def apply(database_url: str) -> None:
    backend, migrations = _backend(database_url)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


def rollback(database_url: str) -> None:
    backend, migrations = _backend(database_url)
    with backend.lock():
        to_rollback = backend.to_rollback(migrations)
        if to_rollback:
            backend.rollback_migrations(to_rollback[-1:])


def status(database_url: str) -> None:
    backend, migrations = _backend(database_url)
    applied = {migration.id for migration in backend.to_rollback(migrations)}
    for migration in migrations:
        state = "applied" if migration.id in applied else "pending"
        print(f"{migration.id}: {state}")


def sync_catalog(database_url: str, path: Path) -> None:
    from src.store.catalog_sync import synchronize_vehicle_reference_catalog
    from src.store.pool import DatabaseSettings, create_pool
    from src.store.postgres import PostgresStore

    pool = create_pool(DatabaseSettings(database_url=database_url))
    report = synchronize_vehicle_reference_catalog(PostgresStore(pool), path)
    print(
        "Vehicle Reference Catalog sync: "
        f"inserted={report.inserted}, updated={report.updated}, "
        f"unchanged={report.unchanged}, rejected={report.rejected}, "
        f"conflicts={report.conflicts}, source={report.source_file}"
    )
