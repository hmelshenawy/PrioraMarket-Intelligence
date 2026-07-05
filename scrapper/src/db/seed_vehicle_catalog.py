"""Compatibility entry point for Vehicle Reference Catalog CSV synchronization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config.config import ConfigurationError, load_config
from src.db.connection import DatabaseSettings, create_pool
from src.db.migrate import apply as apply_migrations
from src.db.vehicle_reference_catalog_sync import synchronize_vehicle_reference_catalog
from src.storage.postgres_storage import PostgresStorageAdapter


def import_vehicle_catalog(path: Path, database_url: str):
    apply_migrations(database_url)
    pool = create_pool(DatabaseSettings(database_url=database_url))
    return synchronize_vehicle_reference_catalog(PostgresStorageAdapter(pool), path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.db.seed_vehicle_catalog")
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--env", default=None)
    args = parser.parse_args(argv)

    try:
        config = load_config(args.env)
        if not config.database_url:
            raise ConfigurationError("DATABASE_URL is required")
        report = import_vehicle_catalog(args.path, config.database_url)
    except ConfigurationError as exc:
        print(f"Vehicle Reference Catalog sync error: {exc}", file=sys.stderr)
        return 2

    print(
        "Vehicle Reference Catalog sync summary: "
        f"inserted={report.inserted}, updated={report.updated}, "
        f"unchanged={report.unchanged}, rejected={report.rejected}, "
        f"conflicts={report.conflicts}, source={report.source_file}"
    )
    return 1 if report.rejected else 0


if __name__ == "__main__":
    sys.exit(main())
