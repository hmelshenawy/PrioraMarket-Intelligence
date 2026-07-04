# ADR-010: Marketplace adapter behavior (streaming, retry, pagination)

**Status:** Accepted
**Date:** 2026-07-04
**Feature:** 001 — Data Ingestion Foundation

## Context

The Constitution (Principle III Domain-Driven Architecture, Principle XI
Scalability by Design) requires marketplace-specific logic to be isolated
and the architecture to support multiple marketplaces without
orchestration rewrites. The prototype scraper mixed HTTP, pagination,
parsing, and CSV writing in one 250-line script, with hardcoded Algolia
credentials and a hardcoded output path. Feature 001 must preserve the
prototype's data behavior (SC-001 parity) while making the marketplace
boundary a clean, replaceable adapter.

The adapter must also satisfy Constitution Principle XIV (Security by
Default: rate limiting, secure secrets, validation, protection against
malformed external data) and the resilience requirement that a failed
page must not terminate the run.

## Decision

Define a `MarketplaceAdapter` interface
(`src/marketplaces/adapter_interface.py`) as a streaming `Protocol`:
`fetch(scope)` yields `(list[RawListing], PageMetadata)` tuples, one per
fetched page. The single Dubizzle implementation lives in
`src/marketplaces/dubizzle/`:

- `adapter.py` — `DubizzleAdapter`: owns HTTP, request construction,
  pagination (cap `MAX_PAGES=500`, preserving the prototype's
  `min(nbPages, 500)` and `nbHits == 0` short-circuit), retry/backoff
  with jitter, rate limiting, and response parsing. No business logic.
- `extractor.py` — `extract(hit, ...)`: the only module that knows
  Dubizzle field names; mirrors the prototype's `extract()` for parity
  and preserves the raw payload **verbatim** (identity-preserving: the
  same dict object is stored on `RawListing.raw_payload`).

Streaming (iterable) output is preferred over buffering the full
dataset so the pipeline can process pages as they arrive and so memory
stays bounded. This is **not** async — Feature 001 is explicitly
single-threaded (no parallel execution, distributed workers, or message
queues).

Transient failures (timeouts, connection errors, HTTP 429/5xx) are
retried with exponential backoff + jitter, up to `RETRY_ATTEMPTS`.
Non-transient HTTP errors (e.g. 404) are not retried. A page that
exhausts retries yields an empty listing set with `retried=True`; the
pipeline isolates it as a recorded failure rather than aborting.

Secrets (Algolia app id / API key) are read from `Config` only; no
hardcoded values in source (SC-007). External data is treated as
untrusted: every hit flows through extraction → normalization →
canonicalization → validation before persistence.

## Alternatives considered

- **Buffer all pages, then return.** Rejected: unbounded memory and
  loses the ability to record per-page progress/stop-position.
- **Async streaming.** Rejected: out of scope for Feature 001
  (explicitly excluded: parallel execution, distributed workers, queues).
- **Retry at the pipeline level.** Rejected: retries are a
  marketplace-transport concern and belong in the adapter; the pipeline
  handles failure isolation, not transport retry.
- **Parsing in the pipeline.** Rejected: would leak Dubizzle field names
  into orchestration, breaking marketplace isolation (SC-009).

## Consequences

- Adding a second marketplace (SC-009) requires only a new adapter
  package implementing `MarketplaceAdapter`; no orchestration code
  changes.
- The adapter is the sole network boundary, simplifying security review
  and future rate-limit/circuit-breaker hardening.
- `PageMetadata` on page 0 (`nb_pages`, `nb_hits`) drives the
  pagination cap; adapters must populate it.
- Retry and rate-limit parameters are env-driven, so operators can tune
  politeness without code changes.