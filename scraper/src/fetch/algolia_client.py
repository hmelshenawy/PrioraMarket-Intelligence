"""Algolia HTTP transport (FR-011, US2).

Owns every transport concern for Algolia's multi-query endpoint: session
and header setup, request-body construction, retry/backoff for transient
failures (429/5xx, timeouts, connection errors), and timeout handling.
No marketplace-specific filter or parsing logic lives here — callers
supply the query ``params`` string and receive the first Algolia result.
"""

from __future__ import annotations

import random
import time
from typing import Any, Optional

import requests

from src.config import Config
from src.logging_setup import get_logger

# Statuses worth retrying: rate limiting and transient server errors.
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class TransientFetchError(Exception):
    """Retryable fetch failure (network/timeout/5xx/rate-limit)."""


class AlgoliaClient:
    """Retrying HTTP client for Algolia multi-query searches."""

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
        self.retry_count = 0

    def reset_retries(self) -> None:
        self.retry_count = 0

    def search(
        self,
        params: str,
        *,
        page: int,
    ) -> tuple[Optional[dict[str, Any]], bool]:
        """Run one Algolia query. Returns (first_result, retried).

        ``first_result`` is ``None`` on terminal failure (retries exhausted,
        non-transient HTTP error, or an empty ``results`` payload).
        """
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
                if r.status_code in RETRYABLE_STATUSES:
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
