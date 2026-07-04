"""Structured (JSON) logging with run correlation id and secret scrubbing.

Implemented on the stdlib ``logging`` package with a JSON formatter so the
runtime has no hard dependency beyond the declared ones (see ADR-011).
FR-060 (structured logging) and FR-062 (no secrets in logs).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

# Substrings scrubbed from log records. The Algolia API key and app id are
# the only secrets in this feature; scrubbing is defense-in-depth.
_SECRET_SUBSTRINGS: list[str] = []
_SECRET_KEYS = {
    "algolia_api_key",
    "api_key",
    "authorization",
    "password",
    "secret",
    "token",
}


def register_secret(value: str) -> None:
    """Register a secret value to be scrubbed from log output."""
    if value:
        _SECRET_SUBSTRINGS.append(value)


def _scrub(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: ("***REDACTED***" if k.lower() in _SECRET_KEYS else _scrub(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    if isinstance(obj, str):
        redacted = obj
        for secret in _SECRET_SUBSTRINGS:
            if secret and secret in redacted:
                redacted = redacted.replace(secret, "***REDACTED***")
        return redacted
    return obj


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach structured extras (any attribute added via extra=).
        for key, value in record.__dict__.items():
            if key in payload or key in {
                "args",
                "msg",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "name",
                "taskName",
            }:
                continue
            payload[key] = value
        payload = _scrub(payload)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(
    run_id: str,
    *,
    structured: bool = True,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure and return a logger tagged with a run correlation id."""
    root = logging.getLogger("prioramarket")
    root.setLevel(level)
    # Replace handlers to make configuration idempotent across runs.
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler()
    if structured:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    root.addHandler(handler)
    root.propagate = False
    # Use a child logger so every record carries run_id.
    logger = logging.getLogger(f"prioramarket.{run_id}")
    logger.setLevel(level)
    logger.propagate = True
    return logger


def get_logger(run_id: str = "no-run") -> logging.Logger:
    return logging.getLogger(f"prioramarket.{run_id}")
