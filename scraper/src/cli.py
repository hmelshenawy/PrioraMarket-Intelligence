"""PrioraMarket ingestion CLI.

Commands:
  run           fetch a scope from Algolia and save it to PostgreSQL
  backfill      re-canonicalize existing listing rows (no marketplace access)
  migrate       apply | status | rollback the schema migrations
  catalog-sync  synchronize the Vehicle Reference Catalog from CSV files

Configuration comes entirely from the environment (no hardcoded secrets).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import psycopg
from psycopg.rows import dict_row

from src.backfill import CanonicalBackfillService
from src.config import ConfigurationError, load_config
from src.fetch.algolia import DubizzleAdapter
from src.logging_setup import configure_logging, get_logger
from src.normalize import normalize
from src.store import catalog_repo
from src.store.postgres import PostgresStore
from src.validation import validate


def cmd_run(args: argparse.Namespace) -> int:
    config = load_config(args.env)
    log = configure_logging(
        f"run_{args.marketplace}_{args.condition}_{args.make}",
        structured=config.enable_structured_logging,
    )

    adapter = DubizzleAdapter(config)

    conn = psycopg.connect(config.database_url, row_factory=dict_row)
    store = PostgresStore(conn)
    catalog = _catalog_lookup(conn)

    counts = {"fetched": 0, "valid": 0, "skipped": 0, "listings_created": 0, "listings_updated": 0}
    try:
        for raw in adapter.fetch(make=args.make, condition=args.condition):
            counts["fetched"] += 1
            try:
                listing = normalize(raw, catalog)
            except Exception:
                counts["skipped"] += 1
                log.exception("could not normalize listing %s", raw.uuid)
                continue

            if not validate(listing):
                counts["skipped"] += 1
                log.info("Invalid listing skipped: %s", listing.uuid)
                continue

            counts["valid"] += 1
            counts[f"listings_{store.save_listing(raw, listing)}"] += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    log.info("ingestion run finished", extra=counts)
    print(
        f"Fetched: {counts['fetched']} | Valid: {counts['valid']} | Skipped: {counts['skipped']}"
        f" | Created: {counts['listings_created']} | Updated: {counts['listings_updated']}"
    )
    return 0


def _catalog_lookup(conn):
    """Vehicle Reference Catalog lookup used by normalization."""

    def lookup(make_key, model_key):
        return catalog_repo.find_vehicle_reference_catalog(conn, "global", make_key, model_key)

    return lookup


def cmd_backfill(args: argparse.Namespace) -> int:
    config = load_config(args.env)
    conn = psycopg.connect(config.database_url, row_factory=dict_row)
    try:
        service = CanonicalBackfillService(
            conn,
            canonicalization_version=args.canonicalization_version,
            market=args.market,
        )
        report = service.run(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            resume_after_id=args.resume_after_id,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
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
    sync_catalog(config.database_url, Path(args.catalog_path))
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
