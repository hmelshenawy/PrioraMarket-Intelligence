# ADR-011: Structured logging via stdlib (implementation deviation from research.md)

**Status:** Accepted
**Date:** 2026-07-04
**Feature:** 001 — Data Ingestion Foundation
**Supersedes (for implementation):** research.md decision "structlog emitting JSON"

## Context

`research.md` (approved during `/speckit-plan`) selected `structlog` as
the structured-logging library, and `plan.md` lists `structlog` as a
dependency. FR-060 requires structured (JSON) logging with a run
correlation id, and FR-062 requires that logs contain no secrets.

During implementation, introducing `structlog` added an install/config
step that provided little benefit over a small stdlib-based JSON
formatter, since the only structured fields needed are a timestamp,
level, logger name, message, run correlation id, and arbitrary extras.

## Decision

Implement structured logging on the Python **stdlib `logging` package**
with a custom JSON formatter (`src/common/logger.py`), rather than
introducing `structlog`. The implementation still satisfies FR-060 and
FR-062:

- JSON output with ISO-8601 UTC timestamps, level, logger, message.
- Run correlation id attached via a per-run child logger
  (`prioramarket.<run_id>`).
- Secret scrubbing: registered secret substrings and known secret keys
  (`api_key`, `authorization`, `password`, `secret`, `token`,
  `algolia_api_key`) are redacted from every log record.
- A non-structured fallback formatter is used when
  `ENABLE_STRUCTURED_LOGGING=false`.

This is an **implementation deviation** from the research.md decision;
the requirement (structured logging) is unchanged.

## Alternatives considered

- **Add `structlog` as planned.** Rejected for Feature 001: extra
  dependency for marginal benefit; the stdlib formatter meets the
  requirement with zero new dependencies.
- **Plain line logging.** Rejected: violates FR-060 (structured logging).

## Consequences

- `requirements.txt` and `pyproject.toml` do not list `structlog`; the
  only runtime dependencies are `requests` and `python-dotenv`.
- If richer structured context (contextvars, processors) is needed
  later, a future ADR can revisit `structlog`; the `configure_logging`
  / `get_logger` API is the seam.
- `research.md` and `plan.md` retain the `structlog` decision as the
  approved design; this ADR is the authoritative implementation record.