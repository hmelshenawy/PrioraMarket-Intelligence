"""Contract test: every storage implementation satisfies the 5-method protocol."""

from __future__ import annotations

from pathlib import Path

from src.store.base import StorageAdapter
from src.store.csv_store import CsvStorageAdapter
from src.store.postgres import PostgresStore
from tests.fakes import InMemoryStorageAdapter


def _instances(tmp_path: Path):
    return [
        CsvStorageAdapter(tmp_path, "run-contract"),
        InMemoryStorageAdapter(),
        PostgresStore(pool=None),
    ]


def test_all_stores_satisfy_storage_adapter_protocol(tmp_path) -> None:
    for store in _instances(tmp_path):
        assert isinstance(store, StorageAdapter), type(store).__name__


def test_protocol_has_exactly_the_five_pipeline_methods(tmp_path) -> None:
    expected = {
        "write_raw",
        "write_listings",
        "write_report",
        "find_vehicle_reference_catalog",
        "write_normalization_statistics",
    }
    for store in _instances(tmp_path):
        for method in expected:
            assert callable(getattr(store, method)), (type(store).__name__, method)
