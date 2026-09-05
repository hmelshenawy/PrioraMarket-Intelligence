"""Unit tests for configuration defaults and validation.

Imports are resolved inside each test because other tests reload
``src.config`` (importlib.reload), which orphans module-level imports.
"""

from __future__ import annotations

import pytest


def _env(monkeypatch, **overrides):
    # Earlier integration tests leak load_dotenv() values into os.environ;
    # scrub everything this module asserts on so tests are order-independent.
    for leaked in (
        "DATABASE_URL",
        "STORAGE_BACKEND",
        "DB_POOL_MIN",
        "DB_POOL_MAX",
        "DB_CONNECT_TIMEOUT",
        "HITS_PER_PAGE",
        "MAX_PAGES",
        "RETRY_ATTEMPTS",
        "RETRY_BACKOFF",
        "RATE_LIMIT_MIN_SECONDS",
        "RATE_LIMIT_MAX_SECONDS",
        "REQUEST_TIMEOUT_SECONDS",
        "NORMALIZATION_VERSION",
        "CANONICALIZATION_VERSION",
        "ENABLE_STRUCTURED_LOGGING",
    ):
        monkeypatch.delenv(leaked, raising=False)
    base = {
        "ALGOLIA_APP_ID": "x",
        "ALGOLIA_API_KEY": "k",
        "ALGOLIA_INDEX": "idx",
        "ALGOLIA_URL": "https://example/queries",
        "OUTPUT_DIR": "./data/out",
        "DATABASE_URL": "postgresql://user:pass@localhost/db",
    }
    base.update(overrides)
    for key, value in base.items():
        monkeypatch.setenv(key, value)
    # Do not let load_dotenv() pick up the developer's real scraper/.env.
    monkeypatch.setattr("src.config.load_dotenv", lambda *a, **k: False)


def test_missing_database_url_is_rejected(monkeypatch):
    from src.config import ConfigurationError, load_config

    _env(monkeypatch)
    monkeypatch.delenv("DATABASE_URL")
    with pytest.raises(ConfigurationError, match="DATABASE_URL"):
        load_config()


def test_unknown_backend_is_rejected(monkeypatch):
    from src.config import ConfigurationError, load_config

    _env(monkeypatch, STORAGE_BACKEND="csv")
    with pytest.raises(ConfigurationError, match="STORAGE_BACKEND"):
        load_config()


def test_snapshot_excludes_secrets(monkeypatch):
    from src.config import load_config

    snap = load_config().snapshot()
    assert "algolia_api_key" not in snap
    assert "algolia_app_id" not in snap
    assert "database_url" not in snap
    assert snap["normalization_version"] == "norm-1"
    assert snap["canonicalization_version"] == "canonical-key-1"


def test_invalid_pool_range_is_rejected(monkeypatch):
    from src.config import ConfigurationError, load_config

    _env(monkeypatch, DB_POOL_MIN="5", DB_POOL_MAX="1")
    with pytest.raises(ConfigurationError, match="pool range"):
        load_config()
