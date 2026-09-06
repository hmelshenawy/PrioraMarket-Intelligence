"""Dubizzle marketplace adapter.

Fetches Dubizzle listings from the Algolia backend and streams them as
RawListings. Owns Dubizzle filters, page params, pagination (capped at
MAX_PAGES), hit extraction and the between-page rate limit; HTTP
transport (session, retry, backoff) is delegated to ``AlgoliaClient``.
Secrets are read from Config only — never hardcoded (Constitution XIV).
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from typing import Iterator, Optional

import requests

from src.config import Config
from src.fetch.algolia_client import AlgoliaClient
from src.fetch.dubizzle_extract import extract
from src.logging_setup import get_logger
from src.models import RawListing

# Attribute list preserved exactly from the prototype for parity (SC-001).
ATTRIBUTES_TO_RETRIEVE = (
    "id,uuid,name,price,year,kilometers,details,category_v2,seller_type,"
    "user,is_verified_user,seller_account_type,neighbourhood,places,uri,"
    "added,photos_count,motors_trim,url,permalink,absolute_url,canonical_url,"
    "web_url,share_url"
)


def build_filter(make_slug: str, condition: str) -> str:
    """Algolia filter expression for one (make, condition) scope."""
    return f'("category_v2.slug_paths":"motors/{condition}-cars/{make_slug}") ' f'AND ("site.id":2)'


class DubizzleAdapter:
    """Streaming Dubizzle adapter."""

    def __init__(self, config: Config, session: Optional[requests.Session] = None):
        self._config = config
        self._client = AlgoliaClient(config, session=session)
        self._log = get_logger("adapter")
        self.failures = 0
        print("dubbizleAdaptor!! ",self._client)

    @property
    def retry_count(self) -> int:
        """Total retries the underlying client has performed."""
        return self._client.retry_count

    def fetch(self, make: str, condition: str) -> Iterator[RawListing]:
        """Yield RawListings for every hit on every fetched page."""
        self.failures = 0
        self._client.reset_retries()
        filters = build_filter(make, condition)
        page = 0
        total_pages = 1
        fetched_at = datetime.now(timezone.utc)
        scrape_run_id = f"dubizzle_{fetched_at:%Y%m%dT%H%M%S}"

        while page < total_pages:
            params = self._build_params(filters=filters, page=page)
            result, retried = self._client.search(params, page=page)
            if result is None:
                # Page failed terminally after retries — stop pagination.
                self.failures += 1
                self._log.error("page fetch failed terminally", extra={"page": page})
                return

            if page == 0:
                total_pages = min(result.get("nbPages", 1), self._config.max_pages)
                if result.get("nbHits", 0) == 0:
                    return

            for hit in result.get("hits", []) or []: # loop inside the hit array to get each car alone
                yield extract(
                    hit,
                    condition=condition,
                    scrape_run_id=scrape_run_id,
                    fetched_at=fetched_at,
                )
            page += 1  # increase page number inside the while loop to get next page hits / cars
            self._rate_limit_sleep()
            print("fetch!! ",self.__class__.__name__)

    def _build_params(self, *, filters: str, page: int) -> str:
        bo2loz =  "&".join(
            [
                f"hitsPerPage={self._config.hits_per_page}",
                f"page={page}",
                f"filters={filters}",
                f"attributesToRetrieve={ATTRIBUTES_TO_RETRIEVE}",
            ]
        ) 
        print("prams!! ", bo2loz)
        return bo2loz

    def _rate_limit_sleep(self) -> None:
        lo = self._config.rate_limit_min_seconds
        hi = self._config.rate_limit_max_seconds
        time.sleep(random.uniform(lo, hi))
