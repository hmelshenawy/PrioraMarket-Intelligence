from __future__ import annotations

from datetime import datetime, timezone

from src.run_naming import build_run_name, collision_disambiguator, slug_segment


def test_run_name_uses_utc_slugged_segments() -> None:
    started = datetime(2026, 7, 4, 9, 0, 0, tzinfo=timezone.utc)

    assert (
        build_run_name("Dubizzle UAE", "Used Cars", "Mercedes Benz", started)
        == "run_dubizzle-uae_used-cars_mercedes-benz_20260704_090000"
    )


def test_run_name_disambiguator_is_deterministic_hex_suffix() -> None:
    started = datetime(2026, 7, 4, 9, 0, 0, tzinfo=timezone.utc)
    base = build_run_name("dubizzle", "used", "toyota", started)
    suffix = collision_disambiguator(base, 42)

    assert len(suffix) == 8
    assert suffix == collision_disambiguator(base, 42)
    assert build_run_name("dubizzle", "used", "toyota", started, suffix).endswith(f"_{suffix}")


def test_slug_segment_empty_becomes_unknown() -> None:
    assert slug_segment("***") == "unknown"
