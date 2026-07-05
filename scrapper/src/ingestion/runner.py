"""CLI runner entry point for ingestion and replay (FR-007, FR-065..067).

Usage:
  python -m ingestion.runner run --marketplace dubizzle --condition used --make toyota
  python -m ingestion.runner replay --dataset <run_id> --normalization-version norm-1

Configuration is loaded entirely from the environment (no hardcoded
secrets/paths). The runner wires concrete adapters into the pipeline.
"""

from __future__ import annotations

import argparse
import sys
import uuid as uuid_lib
from dataclasses import replace
from datetime import datetime, timezone
from typing import Optional

from src.common.logger import configure_logging, get_logger
from src.common.models import Scope
from src.config.config import ConfigurationError, load_config
from src.ingestion.pipeline import IngestionPipeline
from src.marketplaces.dubizzle.adapter import DubizzleAdapter
from src.reporting.run_report import format_summary_text
from src.storage.csv_storage import CsvStorageAdapter
from src.storage.in_memory import InMemoryStorageAdapter


def _build_run_id(scope: Scope) -> str:
    short = uuid_lib.uuid4().hex[:8]
    return f"run_{scope.marketplace}_{scope.condition}_{scope.make}_{short}"


def _marketplace_source_code(scope: Scope) -> str:
    if scope.marketplace == "dubizzle":
        return "dubizzle_uae"
    return scope.marketplace


def _create_postgres_bridge(config, scope: Scope, run_started_at: datetime):
    from src.db.connection import DatabaseSettings, create_pool
    from src.persistence.batch_bridge import PersistenceBatchBridge
    from src.persistence.service import PersistenceService
    from src.storage.postgres_storage import PostgresStorageAdapter

    pool = create_pool(DatabaseSettings.from_config(config))
    storage = PostgresStorageAdapter(pool)
    service = PersistenceService(storage)
    return PersistenceBatchBridge(
        service=service,
        scope=scope,
        config_snapshot=config.snapshot(),
        run_started_at=run_started_at,
        marketplace_source_code=_marketplace_source_code(scope),
    )


def _create_postgres_storage(config):
    from src.db.connection import DatabaseSettings, create_pool
    from src.storage.postgres_storage import PostgresStorageAdapter

    return PostgresStorageAdapter(create_pool(DatabaseSettings.from_config(config)))


def _build_storage_adapter(config, scope: Scope, run_id: str, run_started_at: datetime):
    backend = config.storage_backend
    if backend == "csv":
        return CsvStorageAdapter(config.output_dir, run_id), config
    if backend in {"memory", "in-memory"}:
        return InMemoryStorageAdapter(), config
    if backend == "postgres":
        # The PostgreSQL bridge receives canonical listings through write_listings;
        # keep CSV behavior unchanged while ensuring postgres always gets that batch.
        return _create_postgres_bridge(config, scope, run_started_at), replace(
            config, enable_csv_storage=True
        )
    raise ConfigurationError(f"Unsupported STORAGE_BACKEND: {backend}")


def run_ingestion(
    scope: Scope,
    env_path: Optional[str] = None,
) -> int:
    """Execute one scoped ingestion run. Returns listings extracted count."""
    config = load_config(env_path)
    run_id = _build_run_id(scope)
    run_started_at = datetime.now(timezone.utc)
    log = configure_logging(run_id, structured=config.enable_structured_logging)
    log.info(
        "ingestion run starting",
        extra={"scope": scope.__dict__, "run_id": run_id},
    )
    adapter = DubizzleAdapter(config)
    storage, pipeline_config = _build_storage_adapter(config, scope, run_id, run_started_at)
    pipeline = IngestionPipeline(pipeline_config, adapter, storage)
    result = pipeline.run(scope, run_id)
    print(format_summary_text(result.report))
    return result.report.listings_extracted


def cmd_run(args: argparse.Namespace) -> int:
    scope = Scope(
        marketplace=args.marketplace,
        condition=args.condition,
        make=args.make,
    )
    return run_ingestion(scope, env_path=args.env)


def cmd_replay(args: argparse.Namespace) -> int:
    # US5 (T039..T041): offline deterministic replay over stored RawListings.
    from src.replay.replayer import Replayer  # imported lazily

    config = load_config(args.env)
    run_id = f"replay_{args.dataset}_{uuid_lib.uuid4().hex[:8]}"
    log = configure_logging(run_id, structured=config.enable_structured_logging)
    storage = CsvStorageAdapter(config.output_dir, run_id)

    # Derive scope from the stored raw data (replay has no marketplace call).
    first = next(storage.read_raw(dataset_version=args.dataset), None)
    if first is None:
        print(f"Replay {run_id}: no raw listings found for dataset {args.dataset}")
        return 0
    scope = Scope(
        marketplace=first.marketplace,
        condition=first.condition,
        make=first.make_slug or args.make or "unknown",
    )
    log.info(
        "replay starting",
        extra={
            "dataset": args.dataset,
            "scope": scope.__dict__,
            "normalization_version": args.normalization_version,
            "canonicalization_version": args.canonicalization_version,
        },
    )
    replayer = Replayer(
        storage=storage,
        normalizer_version=args.normalization_version,
        canonicalization_version=args.canonicalization_version,
        scope=scope,
    )
    listings = replayer.replay(dataset_version=args.dataset)
    if config.enable_csv_storage:
        storage.write_listings(listings)
    print(
        f"Replay {run_id}: rebuilt {len(listings)} listings from {args.dataset} "
        f"(normalization_version={args.normalization_version}, "
        f"canonicalization_version={args.canonicalization_version})"
    )
    return len(listings)


def cmd_backfill(args: argparse.Namespace) -> int:
    from src.maintenance.canonical_backfill import CanonicalBackfillService

    config = load_config(args.env)
    storage = _create_postgres_storage(config)
    service = CanonicalBackfillService(
        storage,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prioramarket-ingestion")
    parser.add_argument("--env", default=None, help="path to .env file")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="execute a scoped ingestion run")
    run_p.add_argument("--marketplace", required=True)
    run_p.add_argument("--condition", required=True, choices=["used", "new"])
    run_p.add_argument("--make", required=True, help="make slug, e.g. toyota")
    run_p.set_defaults(func=cmd_run)

    replay_p = sub.add_parser("replay", help="rebuild listings offline from raw data")
    replay_p.add_argument("--dataset", required=True, help="dataset/run id to replay")
    replay_p.add_argument(
        "--normalization-version",
        default="norm-1",
        help="explicit normalization version to apply",
    )
    replay_p.add_argument(
        "--canonicalization-version",
        default="canonical-key-1",
        help="explicit canonicalization version to apply",
    )
    replay_p.add_argument(
        "--make",
        default=None,
        help="make slug fallback (normally derived from stored raw data)",
    )
    replay_p.set_defaults(func=cmd_replay)

    backfill_p = sub.add_parser(
        "backfill",
        help="canonicalize existing listing rows without marketplace access",
    )
    mode = backfill_p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run", action="store_true", help="report changes without updating listings"
    )
    mode.add_argument(
        "--execute", action="store_true", help="apply listing canonical field updates"
    )
    backfill_p.add_argument("--batch-size", type=int, default=500)
    backfill_p.add_argument("--resume-after-id", type=int, default=None)
    backfill_p.add_argument("--market", default="global")
    backfill_p.add_argument(
        "--canonicalization-version",
        default="canonical-key-1",
        help="explicit canonicalization version to apply",
    )
    backfill_p.set_defaults(func=cmd_backfill)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except ConfigurationError as exc:
        get_logger("runner").error("configuration error", extra={"error": str(exc)})
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - top-level CLI boundary
        get_logger("runner").error("run failed", extra={"error": str(exc)})
        print(f"Run failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
