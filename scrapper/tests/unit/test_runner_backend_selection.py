from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from src.common.models import Scope
from src.config.config import Config
from src.ingestion import runner
from src.persistence.batch_bridge import PersistenceBatchBridge
from src.storage.csv_storage import CsvStorageAdapter
from src.storage.in_memory import InMemoryStorageAdapter


def _config(tmp_path, backend: str = "csv", enable_csv_storage: bool = True) -> Config:
    return Config(
        algolia_app_id="x",
        algolia_api_key="k",
        algolia_index="idx",
        algolia_url="https://example/queries",
        hits_per_page=20,
        max_pages=1,
        output_dir=tmp_path,
        retry_attempts=3,
        retry_backoff=1.5,
        rate_limit_min_seconds=0.0,
        rate_limit_max_seconds=0.0,
        request_timeout_seconds=15.0,
        normalization_version="norm-1",
        enable_validation=True,
        enable_canonicalization=True,
        enable_replay=True,
        enable_structured_logging=False,
        enable_csv_storage=enable_csv_storage,
        storage_backend=backend,
        database_url="postgres://user:pass@localhost:5432/db" if backend == "postgres" else None,
    )


def test_run_parser_does_not_accept_storage_backend_flag() -> None:
    parser = runner.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "run",
                "--marketplace",
                "dubizzle",
                "--condition",
                "used",
                "--make",
                "toyota",
                "--storage-backend",
                "postgres",
            ]
        )


def test_csv_backend_uses_csv_adapter_and_preserves_config(tmp_path) -> None:
    config = _config(tmp_path, "csv")
    storage, pipeline_config = runner._build_storage_adapter(
        config,
        Scope("dubizzle", "used", "toyota"),
        "run-1",
        datetime.now(timezone.utc),
    )

    assert isinstance(storage, CsvStorageAdapter)
    assert pipeline_config is config


@pytest.mark.parametrize("backend", ["memory", "in-memory"])
def test_memory_backend_uses_in_memory_adapter(tmp_path, backend) -> None:
    config = _config(tmp_path, backend)
    storage, pipeline_config = runner._build_storage_adapter(
        config,
        Scope("dubizzle", "used", "toyota"),
        "run-1",
        datetime.now(timezone.utc),
    )

    assert isinstance(storage, InMemoryStorageAdapter)
    assert pipeline_config is config


def test_postgres_backend_uses_persistence_bridge_and_forces_listing_batch(
    tmp_path, monkeypatch
) -> None:
    config = _config(tmp_path, "postgres", enable_csv_storage=False)
    expected = object()

    def fake_create_bridge(config_arg, scope_arg, started_arg):
        assert config_arg is config
        assert scope_arg == Scope("dubizzle", "used", "toyota")
        assert started_arg.tzinfo is not None
        return expected

    monkeypatch.setattr(runner, "_create_postgres_bridge", fake_create_bridge)

    storage, pipeline_config = runner._build_storage_adapter(
        config,
        Scope("dubizzle", "used", "toyota"),
        "run-1",
        datetime.now(timezone.utc),
    )

    assert storage is expected
    assert pipeline_config == replace(config, enable_csv_storage=True)


def test_postgres_bridge_type_is_the_expected_boundary() -> None:
    assert PersistenceBatchBridge.__name__ == "PersistenceBatchBridge"
