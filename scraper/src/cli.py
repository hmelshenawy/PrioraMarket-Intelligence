"""PrioraMarket ingestion CLI.

Commands:
  run           fetch a scope from Algolia and store it (postgres or CSV)
  backfill      re-canonicalize existing listing rows (no marketplace access)
  migrate       apply | status | rollback the schema migrations
  catalog-sync  synchronize the Vehicle Reference Catalog from CSV files

Configuration comes entirely from the environment (no hardcoded secrets).
"""

from __future__ import annotations

import argparse
import sys
import uuid as uuid_lib
from dataclasses import replace
from datetime import datetime, timezone
from typing import Optional

from src.config import ConfigurationError, load_config
from src.fetch.algolia import DubizzleAdapter
from src.logging_setup import configure_logging, get_logger
from src.models import Scope
from src.pipeline import IngestionPipeline
from src.report import format_summary_text
from src.store.csv_store import CsvStorageAdapter


def _build_run_id(scope: Scope) -> str:
    short = uuid_lib.uuid4().hex[:8]
    return f"run_{scope.marketplace}_{scope.condition}_{scope.make}_{short}"


def _marketplace_source_code(scope: Scope) -> str:
    if scope.marketplace == "dubizzle":
        return "dubizzle_uae"
    return scope.marketplace


def _create_postgres_store(
    config,
    scope: Scope | None = None,
    run_started_at: datetime | None = None,
):
    from src.store.pool import DatabaseSettings, create_pool
    from src.store.postgres import PostgresStore

    pool = create_pool(DatabaseSettings.from_config(config))
    return PostgresStore(
        pool,
        scope=scope,
        config_snapshot=config.snapshot() if scope else None,
        run_started_at=run_started_at,
        marketplace_source_code=_marketplace_source_code(scope) if scope else None,
    )


def run_ingestion(scope: Scope, env_path: Optional[str] = None) -> int:
    """Execute one scoped ingestion run. Returns listings extracted count."""
    config = load_config(env_path)
    run_id = _build_run_id(scope)
    run_started_at = datetime.now(timezone.utc)
    log = configure_logging(run_id, structured=config.enable_structured_logging)
    log.info("ingestion run starting", extra={"scope": scope.__dict__, "run_id": run_id})

    adapter = DubizzleAdapter(config)
    if config.storage_backend == "csv":
        storage, pipeline_config = CsvStorageAdapter(config.output_dir, run_id), config
    elif config.storage_backend == "postgres":
        # PostgresStore buffers via write_listings; keep CSV artifacts on too.
        storage = _create_postgres_store(config, scope, run_started_at)
        pipeline_config = replace(config, enable_csv_storage=True)
    else:
        raise ConfigurationError(f"Unsupported STORAGE_BACKEND: {config.storage_backend}")

    pipeline = IngestionPipeline(pipeline_config, adapter, storage)
    result = pipeline.run(scope, run_id)
    print(format_summary_text(result.report))
    return result.report.listings_extracted


def cmd_run(args: argparse.Namespace) -> int:
    scope = Scope(marketplace=args.marketplace, condition=args.condition, make=args.make)
    return run_ingestion(scope, env_path=args.env)


def cmd_backfill(args: argparse.Namespace) -> int:
    from src.backfill import CanonicalBackfillService

    config = load_config(args.env)
    service = CanonicalBackfillService(
        _create_postgres_store(config),
        canonicalization_version=args.canonicalization_version,
        market=args.market,
        progress=print,
    )
    report = service.run(
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        resume_after_id=args.resume_after_id,
    )
    print(
        "Canonical backfill summary: "
        f"dry_run={report.dry_run}, scanned={report.scanned}, changed={report.changed}, "
        f"updated={report.updated}, unchanged={report.unchanged}, skipped={report.skipped}, "
        f"failures={report.failures}, last_processed_id={report.last_processed_id}"
    )
    return 1 if report.failures else 0


def cmd_migrate(args: argparse.Namespace) -> int:
    from src import migrate as migrations

    config = load_config(args.env)
    if not config.database_url:
        raise ConfigurationError("DATABASE_URL is required for migrations")
    command = {
        "apply": migrations.apply,
        "status": migrations.status,
        "rollback": migrations.rollback,
    }[args.migrate_command]
    command(config.database_url)
    return 0


def cmd_catalog_sync(args: argparse.Namespace) -> int:
    from src.migrate import sync_catalog

    config = load_config(args.env)
    if not config.database_url:
        raise ConfigurationError("DATABASE_URL is required for catalog sync")
    sync_catalog(config.database_url, args.catalog_path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prioramarket")
    parser.add_argument("--env", default=None, help="path to .env file")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="execute a scoped ingestion run")
    run_p.add_argument("--marketplace", required=True)
    run_p.add_argument("--condition", required=True, choices=["used", "new"])
    run_p.add_argument("--make", required=True, help="make slug, e.g. toyota")
    run_p.set_defaults(func=cmd_run)

    backfill_p = sub.add_parser(
        "backfill",
        help="canonicalize existing listing rows without marketplace access",
    )
    mode = backfill_p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="report changes without updating")
    mode.add_argument("--execute", action="store_true", help="apply canonical field updates")
    backfill_p.add_argument("--batch-size", type=int, default=500)
    backfill_p.add_argument("--resume-after-id", type=int, default=None)
    backfill_p.add_argument("--market", default="global")
    backfill_p.add_argument(
        "--canonicalization-version",
        default="canonical-key-1",
        help="explicit canonicalization version to apply",
    )
    backfill_p.set_defaults(func=cmd_backfill)

    migrate_p = sub.add_parser("migrate", help="manage the PostgreSQL schema")
    migrate_p.add_argument("migrate_command", choices=["apply", "status", "rollback"])
    migrate_p.set_defaults(func=cmd_migrate)

    catalog_p = sub.add_parser(
        "catalog-sync", help="synchronize the Vehicle Reference Catalog from CSV"
    )
    catalog_p.add_argument(
        "--catalog-path",
        type=str,
        default="data/reference/vehicle_reference_catalog.csv",
    )
    catalog_p.set_defaults(func=cmd_catalog_sync)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except ConfigurationError as exc:
        get_logger("cli").error("configuration error", extra={"error": str(exc)})
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - top-level CLI boundary
        get_logger("cli").error("run failed", extra={"error": str(exc)})
        print(f"Run failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
