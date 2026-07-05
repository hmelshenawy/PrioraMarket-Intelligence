"""Migration CLI for Feature 002.

Usage: python -m src.db.migrate apply|status|rollback
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config.config import ConfigurationError, load_config

MIGRATIONS_DIR = Path(__file__).with_name("migrations")


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
    from src.db.connection import DatabaseSettings, create_pool
    from src.db.vehicle_reference_catalog_sync import synchronize_vehicle_reference_catalog
    from src.storage.postgres_storage import PostgresStorageAdapter

    pool = create_pool(DatabaseSettings(database_url=database_url))
    report = synchronize_vehicle_reference_catalog(PostgresStorageAdapter(pool), path)
    print(
        "Vehicle Reference Catalog sync: "
        f"inserted={report.inserted}, updated={report.updated}, "
        f"unchanged={report.unchanged}, rejected={report.rejected}, "
        f"conflicts={report.conflicts}, source={report.source_file}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.db.migrate")
    parser.add_argument("command", choices=["apply", "status", "rollback", "sync-catalog"])
    parser.add_argument("--env", default=None)
    parser.add_argument(
        "--catalog-path",
        type=Path,
        default=Path("data/reference/vehicle_reference_catalog.csv"),
    )
    args = parser.parse_args(argv)
    try:
        config = load_config(args.env)
        if not config.database_url:
            raise ConfigurationError("DATABASE_URL is required for migrations")
        if args.command == "sync-catalog":
            sync_catalog(config.database_url, args.catalog_path)
        else:
            command = {"apply": apply, "status": status, "rollback": rollback}[args.command]
            command(config.database_url)
    except (ConfigurationError, MigrationError) as exc:
        print(f"Migration error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
