"""Backfill malformed Dubizzle listing URLs from preserved raw payloads.

Safe by default: runs in dry-run mode unless --apply is passed. The script
updates only Dubizzle rows whose current URL is missing or is the internal
/countries/... route, and it derives the replacement with the same extractor
logic used by live ingestion.
"""

from __future__ import annotations

import argparse
import os
from urllib.parse import quote

from dotenv import load_dotenv
from psycopg.rows import dict_row

from src.fetch.dubizzle_extract import extract
from src.hashing import canonical_hash, canonical_payload
from src.models import RawListing, Scope
from src.normalize.canonical import CanonicalizationEngine
from src.normalize.normalizer import Normalizer


def _safe_dsn(dsn: str) -> str:
    if "://" not in dsn or "@" not in dsn:
        return dsn
    scheme, rest = dsn.split("://", 1)
    userinfo, hostpath = rest.rsplit("@", 1)
    if ":" not in userinfo:
        return dsn
    user, password = userinfo.split(":", 1)
    return f"{scheme}://{quote(user, safe='')}:{quote(password, safe='')}@{hostpath}"


def _raw_listing(row) -> RawListing:
    raw_payload = row["raw_payload"] or {}
    return RawListing(
        marketplace=row["source"],
        marketplace_listing_id=(
            str(raw_payload.get("id")) if raw_payload.get("id") is not None else row["uuid"]
        ),
        uuid=row["uuid"],
        raw_payload=raw_payload,
        extracted_fields={},
        fetched_at=row["extracted_at"],
        scrape_run_id=str(row["ingestion_run_id"]),
        condition=row["condition"],
        make_slug=row["make"],
    )


def run(*, env: str | None, apply: bool, limit: int | None, normalization_version: str) -> int:
    load_dotenv(env)
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    from src.store.pool import DatabaseSettings, create_pool

    pool = create_pool(
        DatabaseSettings(database_url=_safe_dsn(database_url), pool_min=1, pool_max=1)
    )
    canonicalizer = CanonicalizationEngine()
    updates = []
    skipped = 0
    samples = []

    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    l.id AS listing_id,
                    l.uuid,
                    l.url AS old_url,
                    rl.source,
                    rl.raw_payload,
                    rl.extracted_at,
                    rl.ingestion_run_id,
                    r.condition,
                    r.make
                FROM listing l
                JOIN raw_listing rl ON rl.id = l.current_raw_listing_id
                JOIN ingestion_run r ON r.id = rl.ingestion_run_id
                WHERE l.source = 'dubizzle'
                  AND (l.url IS NULL OR l.url LIKE %s)
                ORDER BY l.id
                """ + (" LIMIT %s" if limit else ""),
                ("%/countries/%", limit) if limit else ("%/countries/%",),
            )
            rows = cur.fetchall()

            for row in rows:
                raw = _raw_listing(row)
                enriched = extract(
                    raw.raw_payload,
                    condition=raw.condition,
                    scrape_run_id=raw.scrape_run_id,
                    fetched_at=raw.fetched_at,
                    marketplace=raw.marketplace,
                )
                new_url = enriched.extracted_fields.get("url")
                if not new_url:
                    skipped += 1
                    continue
                listing = Normalizer(normalization_version).normalize(
                    enriched,
                    Scope(raw.marketplace, raw.condition, raw.make_slug or "unknown"),
                )
                listing = canonicalizer.canonicalize_listing(listing)
                payload = canonical_payload(listing)
                updates.append(
                    (
                        row["listing_id"],
                        row["old_url"],
                        new_url,
                        canonical_hash(payload),
                    )
                )
                if len(samples) < 10:
                    samples.append((row["listing_id"], row["old_url"], new_url))

            if apply and updates:
                cur.executemany(
                    """
                    UPDATE listing
                    SET url = %s,
                        canonical_hash = %s,
                        normalization_version = %s,
                        updated_at = now()
                    WHERE id = %s
                      AND source = 'dubizzle'
                      AND (url IS NULL OR url LIKE %s)
                    """,
                    [
                        (new_url, listing_hash, normalization_version, listing_id, "%/countries/%")
                        for listing_id, _old_url, new_url, listing_hash in updates
                    ],
                )
                conn.commit()
            else:
                conn.rollback()

    print(f"mode={'apply' if apply else 'dry-run'}")
    print(f"candidates={len(updates)}")
    print(f"skipped={skipped}")
    for listing_id, old_url, new_url in samples:
        print(f"sample|{listing_id}|{old_url}|{new_url}")
    return len(updates)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill malformed Dubizzle listing URLs")
    parser.add_argument("--env", default=None, help="optional .env file path")
    parser.add_argument("--apply", action="store_true", help="write updates; default is dry-run")
    parser.add_argument("--limit", type=int, default=None, help="optional row limit")
    parser.add_argument("--normalization-version", default="norm-url-backfill-1")
    args = parser.parse_args()
    run(
        env=args.env,
        apply=args.apply,
        limit=args.limit,
        normalization_version=args.normalization_version,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
