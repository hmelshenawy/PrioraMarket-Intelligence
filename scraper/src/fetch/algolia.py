"""Dubizzle marketplace adapter (FR-010..015, FR-016..019).

Owns all HTTP communication with Dubizzle's Algolia backend: request
construction, pagination (capped at MAX_PAGES), retry/backoff, rate
limiting, and response parsing. Yields RawListings verbatim via the
extractor. No business logic lives here.

Secrets are read from Config only — never hardcoded (Constitution XIV).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Iterator, Optional, Protocol, runtime_checkable

import requests

from src.config import Config
from src.fetch.dubizzle_extract import extract
from src.logging_setup import get_logger
from src.models import RawListing, Scope

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


class TransientFetchError(Exception):
    """Retryable fetch failure (network/timeout/5xx/rate-limit)."""


class DubizzleAdapter:
    """Streaming Dubizzle adapter. Implements MarketplaceAdapter."""

    marketplace_name = "dubizzle"

    def __init__(self, config: Config, session: Optional[requests.Session] = None):
        self._config = config
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "X-Algolia-Application-Id": config.algolia_app_id,
                "X-Algolia-API-Key": config.algolia_api_key,
                "Content-Type": "application/json",
            }
        )
        self._log = get_logger("adapter")
        self.scope: Optional[Scope] = None
        self.retry_count = 0
        self.failures = 0

    def fetch(self, scope: Scope) -> Iterator[tuple[list[RawListing], PageMetadata]]:
        """Yield (page_listings, metadata) per page for the scope."""
        self.scope = scope
        self.retry_count = 0
        self.failures = 0
        filters = build_filter(scope.make, scope.condition)
        page = 0
        total_pages = 1
        fetched_at = datetime.now(timezone.utc)

        while page < total_pages:
            params = "&".join(
                [
                    f"hitsPerPage={self._config.hits_per_page}",
                    f"page={page}",
                    f"filters={filters}",
                    f"attributesToRetrieve={ATTRIBUTES_TO_RETRIEVE}",
                ]
            )
            result, retried = self._fetch_page(params, page)
            if result is None:
                # Page failed terminally after retries — stop pagination.
                yield ([], PageMetadata(page=page, hits_on_page=0, retried=retried))
                self.failures += 1
                return

            if page == 0:
                total_pages = min(result.get("nbPages", 1), self._config.max_pages)
                nb_hits = result.get("nbHits", 0)
                if nb_hits == 0:
                    yield (
                        [],
                        PageMetadata(
                            page=0, hits_on_page=0, nb_pages=total_pages, nb_hits=0, retried=retried
                        ),
                    )
                    return
            else:
                nb_hits = result.get("nbHits")

            hits = result.get("hits", []) or []
            listings = [
                extract(
                    h,
                    condition=scope.condition,
                    scrape_run_id=self._scrape_run_id(),
                    fetched_at=fetched_at,
                    marketplace=self.marketplace_name,
                )
                for h in hits
            ]
            yield (
                listings,
                PageMetadata(
                    page=page,
                    hits_on_page=len(hits),
                    nb_pages=total_pages,
                    nb_hits=nb_hits,
                    retried=retried,
                ),
            )
            page += 1
            self._rate_limit_sleep()

    def _scrape_run_id(self) -> str:
        # The pipeline sets this on the adapter before fetching.
        return getattr(self, "_run_id", "unknown-run")

    def set_run_id(self, run_id: str) -> None:
        self._run_id = run_id

    def _fetch_page(self, params: str, page: int) -> tuple[Optional[dict[str, Any]], bool]:
        """Fetch one page with retry/backoff. Returns (result, retried)."""
        body = {"requests": [{"indexName": self._config.algolia_index, "params": params}]}
        retried = False
        last_exc: Optional[Exception] = None
        for attempt in range(self._config.retry_attempts):
            try:
                r = self._session.post(
                    self._config.algolia_url,
                    json=body,
                    timeout=self._config.request_timeout_seconds,
                )
                if r.status_code in {429, 500, 502, 503, 504}:
                    raise TransientFetchError(f"HTTP {r.status_code}")
                r.raise_for_status()
                results = r.json().get("results", [])
                if not results:
                    return (None, retried)
                return (results[0], retried)
            except (TransientFetchError, requests.Timeout, requests.ConnectionError) as exc:
                retried = True
                self.retry_count += 1
                last_exc = exc
                self._log.warning(
                    "page fetch retrying",
                    extra={"page": page, "attempt": attempt + 1, "error": str(exc)},
                )
                self._backoff_sleep(attempt)
            except requests.HTTPError as exc:
                # Non-transient HTTP error — do not retry.
                self._log.error(
                    "page fetch failed (non-transient)",
                    extra={"page": page, "error": str(exc)},
                )
                return (None, retried)
        self._log.error(
            "page fetch exhausted retries",
            extra={"page": page, "error": str(last_exc) if last_exc else "unknown"},
        )
        return (None, retried)

    def _backoff_sleep(self, attempt: int) -> None:
        delay = self._config.retry_backoff ** (attempt + 1)
        # Light jitter to avoid synchronized retry storms.
        delay *= random.uniform(0.8, 1.2)
        time.sleep(delay)

    def _rate_limit_sleep(self) -> None:
        lo = self._config.rate_limit_min_seconds
        hi = self._config.rate_limit_max_seconds
        time.sleep(random.uniform(lo, hi))


@dataclass
class PageMetadata:
    """Per-page fetch metadata emitted alongside RawListings."""

    page: int
    hits_on_page: int
    nb_pages: Optional[int] = None
    nb_hits: Optional[int] = None
    retried: bool = False


@runtime_checkable
class MarketplaceAdapter(Protocol):
    """Stream RawListings for a single scope (marketplace, condition, make)."""

    scope: Scope

    def fetch(self, scope: Scope) -> Iterable[tuple[list[RawListing], PageMetadata]]:
        """Yield (page_listings, metadata) tuples, one per fetched page.

        Page 0 metadata MUST include nb_pages / nb_hits so the pipeline can
        apply the pagination cap. Each RawListing preserves the marketplace
        payload verbatim in ``raw_payload``.
        """
        ...

    @property
    def marketplace_name(self) -> str:
        """Stable marketplace identifier (e.g. "dubizzle")."""
        ...
