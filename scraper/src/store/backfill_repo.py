"""Listing backfill persistence: candidate reads and canonical-field updates."""

from __future__ import annotations

from typing import Iterator

from src.models import BackfillListingCandidate


def read_listing_backfill_candidates(
    conn, batch_size: int, after_id: int | None = None
) -> Iterator[BackfillListingCandidate]:
    where = "WHERE id > %s" if after_id is not None else ""
    params = (after_id, batch_size) if after_id is not None else (batch_size,)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, source, uuid, make, model, trim, condition, fuel_type,
                   transmission, regional_spec, body_type, seller_type,
                   vehicle_condition, specs, color, canonical_hash,
                   normalization_version, canonicalization_version, current_raw_listing_id
            FROM listing
            {where}
            ORDER BY id
            LIMIT %s
            """,
            params,
        )
        rows = cur.fetchall()
    return (
        BackfillListingCandidate(
            id=row["id"],
            source=row["source"],
            uuid=row["uuid"],
            canonical_payload=_candidate_payload(row),
            normalization_version=row.get("normalization_version"),
            current_raw_listing_id=row.get("current_raw_listing_id"),
        )
        for row in rows
    )


def update_listing_backfill_payload(
    conn,
    listing_id: int,
    canonical_payload: dict,
    canonical_hash: str,
    normalization_version: str,
    canonicalization_version: str,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE listing
            SET make = %(make)s,
                model = %(model)s,
                trim = %(trim)s,
                condition = %(condition)s,
                fuel_type = %(fuel_type)s,
                transmission = %(transmission)s,
                regional_spec = %(regional_spec)s,
                body_type = %(body_type)s,
                seller_type = %(seller_type)s,
                vehicle_condition = %(vehicle_condition)s,
                specs = %(specs)s,
                color = %(color)s,
                canonical_hash = %(canonical_hash)s,
                normalization_version = %(normalization_version)s,
                canonicalization_version = %(canonicalization_version)s,
                updated_at = now()
            WHERE id = %(listing_id)s
            """,
            {
                "listing_id": listing_id,
                "make": canonical_payload.get("make"),
                "model": canonical_payload.get("model"),
                "trim": canonical_payload.get("trim"),
                "condition": canonical_payload.get("condition"),
                "fuel_type": canonical_payload.get("fuel_type"),
                "transmission": canonical_payload.get("transmission"),
                "regional_spec": canonical_payload.get("regional_spec"),
                "body_type": canonical_payload.get("body_type"),
                "seller_type": canonical_payload.get("seller_type"),
                "vehicle_condition": canonical_payload.get("vehicle_condition"),
                "specs": canonical_payload.get("specs"),
                "color": canonical_payload.get("color"),
                "canonical_hash": canonical_hash,
                "normalization_version": normalization_version,
                "canonicalization_version": canonicalization_version,
            },
        )


def _candidate_payload(row) -> dict:
    return {
        "make": row.get("make"),
        "model": row.get("model"),
        "trim": row.get("trim"),
        "condition": row.get("condition"),
        "fuel_type": row.get("fuel_type"),
        "transmission": row.get("transmission"),
        "regional_spec": row.get("regional_spec"),
        "body_type": row.get("body_type"),
        "seller_type": row.get("seller_type"),
        "vehicle_condition": row.get("vehicle_condition"),
        "specs": row.get("specs"),
        "color": row.get("color"),
        "canonicalization_version": row.get("canonicalization_version"),
    }
