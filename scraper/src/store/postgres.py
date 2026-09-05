"""PostgreSQL persistence for the ingestion flow (one connection).

PostgresStore holds the single connection the CLI opened. It does one
thing: save a raw payload plus its normalized listing. The SQL lives in
the repo modules; the connection's lifecycle (open, commit, rollback,
close) belongs to the CLI.
"""

from __future__ import annotations

from src.models import Listing, RawListing
from src.store import listing_repo


class PostgresStore:
    """Writes raw payloads and listings to PostgreSQL over one connection."""

    def __init__(self, conn):
        self.conn = conn

    def save_listing(self, raw: RawListing, listing: Listing) -> str:
        """Insert the verbatim raw payload, then insert or update the listing.

        Returns "created" for a new listing, "updated" when the listing
        already existed (first_seen_at is then preserved). The caller
        commits.
        """
        raw_id = listing_repo.insert_raw_listing(self.conn, raw)
        existing = listing_repo.find_by_source_uuid(self.conn, listing.marketplace, listing.uuid)
        if existing is None:
            listing_repo.insert_listing(self.conn, listing, raw_id=raw_id)
            print("stored to db!!", raw)
            return "created"
        listing_repo.update_listing(self.conn, existing["id"], listing, raw_id=raw_id)
        return "updated"
