"""Vehicle Reference Catalog persistence: lookup and idempotent upsert."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from psycopg.types.json import Jsonb

from src.models import CatalogSyncReport, VehicleReferenceCatalogRow
from src.normalize import canonicalize


def find_vehicle_reference_catalog(
    conn, market: str, make_key: str, model_key: str | None = None
) -> list[VehicleReferenceCatalogRow]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM vehicle_reference_catalog
            WHERE market = %s AND make_key = %s
            ORDER BY model_key, generation NULLS LAST, body_code NULLS LAST
            """,
            (market, make_key),
        )
        rows = cur.fetchall()
    catalog_rows = [_vehicle_reference_catalog_row(row) for row in rows]
    if model_key is None:
        return catalog_rows
    key = canonicalize(model_key)
    return [
        row for row in catalog_rows if row.model_key == key or key in _catalog_aliases(row, "model")
    ]


def upsert_vehicle_reference_catalog(
    conn, rows: Iterable[VehicleReferenceCatalogRow], source_file: str
) -> CatalogSyncReport:
    inserted = updated = unchanged = conflicts = 0
    synced_at = datetime.now(timezone.utc)
    for row in rows:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM vehicle_reference_catalog
                WHERE market = %s
                  AND make_key = %s
                  AND model_key = %s
                  AND generation IS NOT DISTINCT FROM %s
                  AND body_code IS NOT DISTINCT FROM %s
                """,
                (row.market, row.make_key, row.model_key, row.generation, row.body_code),
            )
            existing = cur.fetchone()
        params = {
            "market": row.market,
            "make_key": row.make_key,
            "make_display": row.make_display,
            "model_key": row.model_key,
            "model_display": row.model_display,
            "generation": row.generation,
            "body_code": row.body_code,
            "start_year": row.start_year,
            "end_year": row.end_year,
            "facelift_start_year": row.facelift_start_year,
            "facelift_end_year": row.facelift_end_year,
            "aliases": Jsonb(row.aliases),
            "confidence": row.confidence,
            "source_file": source_file,
            "source_row_hash": row.source_row_hash,
            "last_synced_at": synced_at,
        }
        if existing is None:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO vehicle_reference_catalog (
                        market, make_key, make_display, model_key, model_display,
                        generation, body_code, start_year, end_year, facelift_start_year,
                        facelift_end_year, aliases, confidence, source_file,
                        source_row_hash, last_synced_at, updated_at
                    )
                    VALUES (
                        %(market)s, %(make_key)s, %(make_display)s, %(model_key)s,
                        %(model_display)s, %(generation)s, %(body_code)s, %(start_year)s,
                        %(end_year)s, %(facelift_start_year)s, %(facelift_end_year)s,
                        %(aliases)s, %(confidence)s, %(source_file)s, %(source_row_hash)s,
                        %(last_synced_at)s, now()
                    )
                    """,
                    params,
                )
            inserted += 1
            continue
        if existing.get("source_row_hash") == row.source_row_hash:
            unchanged += 1
            continue
        if existing.get("source_file") and existing.get("source_file") != source_file:
            conflicts += 1
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE vehicle_reference_catalog
                SET make_display = %(make_display)s,
                    model_display = %(model_display)s,
                    start_year = %(start_year)s,
                    end_year = %(end_year)s,
                    facelift_start_year = %(facelift_start_year)s,
                    facelift_end_year = %(facelift_end_year)s,
                    aliases = %(aliases)s,
                    confidence = %(confidence)s,
                    source_file = %(source_file)s,
                    source_row_hash = %(source_row_hash)s,
                    last_synced_at = %(last_synced_at)s,
                    updated_at = now()
                WHERE id = %(id)s
                """,
                params | {"id": existing["id"]},
            )
        updated += 1
    return CatalogSyncReport(
        source_file=source_file,
        inserted=inserted,
        updated=updated,
        unchanged=unchanged,
        conflicts=conflicts,
        synced_at=synced_at,
    )


def _vehicle_reference_catalog_row(row) -> VehicleReferenceCatalogRow:
    return VehicleReferenceCatalogRow(
        id=row.get("id"),
        market=row["market"],
        make_key=row["make_key"],
        make_display=row["make_display"],
        model_key=row["model_key"],
        model_display=row["model_display"],
        generation=row.get("generation"),
        body_code=row.get("body_code"),
        start_year=row.get("start_year"),
        end_year=row.get("end_year"),
        facelift_start_year=row.get("facelift_start_year"),
        facelift_end_year=row.get("facelift_end_year"),
        aliases=row.get("aliases") or {},
        confidence=row.get("confidence") or "manual",
        source_file=row.get("source_file"),
        source_row_hash=row.get("source_row_hash"),
        last_synced_at=row.get("last_synced_at"),
    )


def _catalog_aliases(row: VehicleReferenceCatalogRow, field_name: str) -> set[str]:
    aliases = row.aliases.get(field_name, []) if isinstance(row.aliases, dict) else []
    if isinstance(aliases, str):
        aliases = [aliases]
    if not isinstance(aliases, list):
        return set()
    return {key for alias in aliases if (key := canonicalize(alias)) is not None}
