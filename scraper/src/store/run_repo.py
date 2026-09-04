"""Run persistence: marketplace source resolution and ingestion_run rows."""

from __future__ import annotations

from datetime import datetime

from src.models import MarketplaceSourceRow, RunReport, RunRow
from src.store.base import MarketplaceSourceNotFoundError


def resolve_marketplace_source(store, code: str) -> MarketplaceSourceRow:
    row = store._fetchone(
        """
        SELECT id, code, name, country, base_url
        FROM marketplace_source
        WHERE code = %s
        """,
        (code,),
    )
    if row is None:
        raise MarketplaceSourceNotFoundError(code)
    return MarketplaceSourceRow(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        country=row["country"],
        base_url=row["base_url"],
    )


def resolve_run(store, run_name_or_id: str) -> RunRow | None:
    if run_name_or_id.isdigit():
        row = store._fetchone(
            "SELECT * FROM ingestion_run WHERE id = %s",
            (int(run_name_or_id),),
        )
    else:
        row = store._fetchone("SELECT * FROM ingestion_run WHERE name = %s", (run_name_or_id,))
    if row is None:
        return None
    return _run_row(row)


def insert_run(store, run: RunRow) -> int:
    row = store._fetchone(
        """
        INSERT INTO ingestion_run (
            name, marketplace_source_id, marketplace, condition, make, status,
            started_at, completed_at, pages_scraped, listings_extracted,
            listings_skipped, failures_count, duration_ms, config_snapshot, report_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            run.name,
            run.marketplace_source_id,
            run.marketplace,
            run.condition,
            run.make,
            run.status,
            run.started_at,
            run.completed_at,
            run.pages_scraped,
            run.listings_extracted,
            run.listings_skipped,
            run.failures_count,
            run.duration_ms,
            store._json(run.config_snapshot),
            store._json(run.report_json) if run.report_json is not None else None,
        ),
    )
    return int(row["id"])


def finalize_run(
    store, run_id: int, report: RunReport, status: str, completed_at: datetime
) -> None:
    duration_ms = int((report.execution_duration_seconds or 0) * 1000)
    store._execute(
        """
        UPDATE ingestion_run
        SET status = %s,
            completed_at = %s,
            pages_scraped = %s,
            listings_extracted = %s,
            listings_skipped = %s,
            failures_count = %s,
            duration_ms = %s,
            report_json = %s
        WHERE id = %s
        """,
        (
            status,
            completed_at,
            report.pages_processed,
            report.listings_extracted,
            report.listings_skipped,
            report.failures,
            duration_ms,
            store._json(report.to_dict()),
            run_id,
        ),
    )


def _run_row(row) -> RunRow:
    return RunRow(
        id=row["id"],
        name=row["name"],
        marketplace_source_id=row["marketplace_source_id"],
        marketplace=row["marketplace"],
        condition=row["condition"],
        make=row["make"],
        status=row["status"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        pages_scraped=row["pages_scraped"],
        listings_extracted=row["listings_extracted"],
        listings_skipped=row["listings_skipped"],
        failures_count=row["failures_count"],
        duration_ms=row["duration_ms"],
        config_snapshot=row["config_snapshot"],
        report_json=row["report_json"],
    )
