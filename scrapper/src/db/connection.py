"""PostgreSQL connection pool factory for Feature 002."""

from __future__ import annotations

from dataclasses import dataclass

from src.config.config import Config


class StorageConnectionError(Exception):
    """Raised when the database connection cannot be established."""


@dataclass(frozen=True)
class DatabaseSettings:
    database_url: str
    pool_min: int = 1
    pool_max: int = 5
    connect_timeout: int = 10

    @classmethod
    def from_config(cls, config: Config) -> "DatabaseSettings":
        if not config.database_url:
            raise StorageConnectionError("DATABASE_URL is required for PostgreSQL storage")
        return cls(
            config.database_url,
            config.db_pool_min,
            config.db_pool_max,
            config.db_connect_timeout,
        )


def create_pool(settings: DatabaseSettings):
    """Create a psycopg connection pool. Driver imports are confined here."""
    try:
        from psycopg_pool import ConnectionPool
    except Exception as exc:  # pragma: no cover - dependency/environment failure
        raise StorageConnectionError("psycopg_pool is not installed") from exc

    try:
        return ConnectionPool(
            settings.database_url,
            min_size=settings.pool_min,
            max_size=settings.pool_max,
            kwargs={"connect_timeout": settings.connect_timeout},
        )
    except Exception as exc:  # pragma: no cover - external service failure
        raise StorageConnectionError(f"Could not create PostgreSQL connection pool: {exc}") from exc
