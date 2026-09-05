"""Unit tests for the consolidated CLI (run | backfill | migrate | catalog-sync)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cli import build_parser, cmd_backfill, cmd_catalog_sync, cmd_migrate, cmd_run, main
from src.config import ConfigurationError


class _StubConfig:
    def __init__(self, database_url):
        self.database_url = database_url


def test_parser_parses_run_command():
    args = build_parser().parse_args(
        ["run", "--marketplace", "dubizzle", "--condition", "used", "--make", "toyota"]
    )
    assert args.func is cmd_run
    assert args.marketplace == "dubizzle" and args.make == "toyota"


def test_parser_parses_backfill_modes():
    parser = build_parser()
    dry = parser.parse_args(["backfill", "--dry-run"])
    execute = parser.parse_args(["backfill", "--execute"])
    assert dry.func is cmd_backfill and dry.dry_run and not dry.execute
    assert execute.func is cmd_backfill and execute.execute
    with pytest.raises(SystemExit):
        parser.parse_args(["backfill"])


def test_parser_parses_migrate_and_catalog_sync():
    parser = build_parser()
    assert parser.parse_args(["migrate", "apply"]).func is cmd_migrate
    assert parser.parse_args(["migrate", "rollback"]).migrate_command == "rollback"
    sync = parser.parse_args(["catalog-sync"])
    assert sync.func is cmd_catalog_sync
    assert sync.catalog_path.endswith("vehicle_reference_catalog.csv")


def test_migrate_requires_database_url(monkeypatch):
    args = build_parser().parse_args(["migrate", "apply"])
    monkeypatch.setattr("src.cli.load_config", lambda env_path=None: _StubConfig(database_url=None))
    with pytest.raises(ConfigurationError):
        cmd_migrate(args)


def test_catalog_sync_passes_a_path_object(monkeypatch):
    received = {}

    def _sync_catalog(database_url, path):
        received["path"] = path

    args = build_parser().parse_args(["catalog-sync", "--catalog-path", "ref/catalog"])
    monkeypatch.setattr("src.cli.load_config", lambda env_path=None: _StubConfig(database_url="x"))
    monkeypatch.setattr("src.migrate.sync_catalog", _sync_catalog)
    assert cmd_catalog_sync(args) == 0
    assert isinstance(received["path"], Path)
    assert received["path"] == Path("ref/catalog")


def test_main_returns_2_on_configuration_error(monkeypatch):
    def _raise(env_path=None):
        raise ConfigurationError("Missing required configuration values")

    monkeypatch.setattr("src.cli.load_config", _raise)
    argv = ["run", "--marketplace", "dubizzle", "--condition", "used", "--make", "toyota"]
    assert main(argv) == 2
