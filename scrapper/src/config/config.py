"""Centralized environment-driven configuration (FR-001..003, FR-015).

All runtime values are sourced from environment variables. Required
values fail fast with a named message. No hardcoded secrets or filesystem
paths live in source. Feature flags are configuration-driven and exist
only for operational control/debugging; business logic MUST NEVER depend
on them.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - dotenv is a declared dependency

    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False


REQUIRED_KEYS = (
    "ALGOLIA_APP_ID",
    "ALGOLIA_API_KEY",
    "ALGOLIA_INDEX",
    "ALGOLIA_URL",
    "OUTPUT_DIR",
)

DB_REQUIRED_KEYS = ("DATABASE_URL",)
STORAGE_BACKENDS = {"csv", "in-memory", "memory", "postgres"}


def _bool(value: str | None, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Config:
    """Validated configuration object."""

    algolia_app_id: str
    algolia_api_key: str
    algolia_index: str
    algolia_url: str
    hits_per_page: int
    max_pages: int
    output_dir: Path
    retry_attempts: int
    retry_backoff: float
    rate_limit_min_seconds: float
    rate_limit_max_seconds: float
    request_timeout_seconds: float
    normalization_version: str

    # Feature flags (operational only; business logic must not depend on them)
    enable_validation: bool
    enable_canonicalization: bool
    enable_replay: bool
    enable_structured_logging: bool
    enable_csv_storage: bool
    storage_backend: str = "csv"
    database_url: str | None = None
    db_pool_min: int = 1
    db_pool_max: int = 5
    db_connect_timeout: int = 10
    canonicalization_version: str = "canonical-key-1"

    def snapshot(self) -> dict[str, Any]:
        """A non-secret snapshot for run metadata / dataset version."""
        return {
            "algolia_index": self.algolia_index,
            "hits_per_page": self.hits_per_page,
            "max_pages": self.max_pages,
            "retry_attempts": self.retry_attempts,
            "retry_backoff": self.retry_backoff,
            "rate_limit_min_seconds": self.rate_limit_min_seconds,
            "rate_limit_max_seconds": self.rate_limit_max_seconds,
            "request_timeout_seconds": self.request_timeout_seconds,
            "normalization_version": self.normalization_version,
            "canonicalization_version": self.canonicalization_version,
            "output_dir": str(self.output_dir),
            "storage_backend": self.storage_backend,
        }


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


def load_config(env_path: str | os.PathLike | None = None) -> Config:
    """Load and validate configuration from the environment.

    Fails fast with a named message if a required value is missing.
    """
    if env_path is not None:
        load_dotenv(env_path)
    else:
        load_dotenv()  # loads .env from CWD if present

    missing = [k for k in REQUIRED_KEYS if not os.environ.get(k)]
    if missing:
        raise ConfigurationError("Missing required configuration values: " + ", ".join(missing))

    def _get_int(key: str, default: int) -> int:
        raw = os.environ.get(key)
        if raw is None or raw == "":
            return default
        try:
            return int(raw)
        except ValueError as exc:
            raise ConfigurationError(f"{key} must be an integer, got {raw!r}") from exc

    def _get_float(key: str, default: float) -> float:
        raw = os.environ.get(key)
        if raw is None or raw == "":
            return default
        try:
            return float(raw)
        except ValueError as exc:
            raise ConfigurationError(f"{key} must be a number, got {raw!r}") from exc

    storage_backend = os.environ.get("STORAGE_BACKEND", "csv").strip().lower() or "csv"
    if storage_backend not in STORAGE_BACKENDS:
        raise ConfigurationError(
            "STORAGE_BACKEND must be one of " + ", ".join(sorted(STORAGE_BACKENDS))
        )

    if storage_backend == "postgres":
        db_missing = [k for k in DB_REQUIRED_KEYS if not os.environ.get(k)]
        if db_missing:
            raise ConfigurationError(
                "Missing required PostgreSQL configuration values: " + ", ".join(db_missing)
            )

    db_pool_min = _get_int("DB_POOL_MIN", 1)
    db_pool_max = _get_int("DB_POOL_MAX", 5)
    if db_pool_min < 0 or db_pool_max < 1 or db_pool_min > db_pool_max:
        raise ConfigurationError("DB_POOL_MIN/DB_POOL_MAX must define a valid pool range")

    return Config(
        algolia_app_id=os.environ["ALGOLIA_APP_ID"],
        algolia_api_key=os.environ["ALGOLIA_API_KEY"],
        algolia_index=os.environ["ALGOLIA_INDEX"],
        algolia_url=os.environ["ALGOLIA_URL"],
        hits_per_page=_get_int("HITS_PER_PAGE", 20),
        max_pages=_get_int("MAX_PAGES", 500),
        output_dir=Path(os.environ["OUTPUT_DIR"]),
        retry_attempts=_get_int("RETRY_ATTEMPTS", 3),
        retry_backoff=_get_float("RETRY_BACKOFF", 1.5),
        rate_limit_min_seconds=_get_float("RATE_LIMIT_MIN_SECONDS", 0.3),
        rate_limit_max_seconds=_get_float("RATE_LIMIT_MAX_SECONDS", 0.8),
        request_timeout_seconds=_get_float("REQUEST_TIMEOUT_SECONDS", 15.0),
        normalization_version=os.environ.get("NORMALIZATION_VERSION", "norm-1"),
        canonicalization_version=os.environ.get("CANONICALIZATION_VERSION", "canonical-key-1"),
        enable_validation=_bool(os.environ.get("ENABLE_VALIDATION"), True),
        enable_canonicalization=_bool(os.environ.get("ENABLE_CANONICALIZATION"), True),
        enable_replay=_bool(os.environ.get("ENABLE_REPLAY"), True),
        enable_structured_logging=_bool(os.environ.get("ENABLE_STRUCTURED_LOGGING"), True),
        enable_csv_storage=_bool(os.environ.get("ENABLE_CSV_STORAGE"), True),
        storage_backend=storage_backend,
        database_url=os.environ.get("DATABASE_URL"),
        db_pool_min=db_pool_min,
        db_pool_max=db_pool_max,
        db_connect_timeout=_get_int("DB_CONNECT_TIMEOUT", 10),
    )


def config_as_dict(cfg: Config) -> dict[str, Any]:
    return asdict(cfg)
