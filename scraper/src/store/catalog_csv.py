"""CSV reader and validator for Vehicle Reference Catalog source files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.hashing import canonical_hash
from src.models import VehicleReferenceCatalogRow
from src.normalize.canonical import canonical_key
from src.store.catalog_validation import validate_vehicle_reference_catalog_row

REQUIRED_COLUMNS = (
    "market",
    "make_key",
    "make_display",
    "model_key",
    "model_display",
    "generation",
    "body_code",
    "start_year",
    "end_year",
    "facelift_start_year",
    "facelift_end_year",
    "aliases",
    "confidence",
)


class VehicleReferenceCatalogCsvError(ValueError):
    """Raised when a catalog CSV file or row is invalid."""


def read_vehicle_reference_catalog_csv(
    path: Path,
) -> tuple[list[VehicleReferenceCatalogRow], list[str]]:
    rows: list[VehicleReferenceCatalogRow] = []
    errors: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, quotechar="'")
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            return [], [f"{path.name}: missing columns: {', '.join(missing)}"]
        for line_number, raw in enumerate(reader, start=2):
            try:
                rows.append(parse_vehicle_reference_catalog_row(raw, path.name))
            except VehicleReferenceCatalogCsvError as exc:
                errors.append(f"{path.name}:{line_number}: {exc}")
    return rows, errors


def parse_vehicle_reference_catalog_row(
    raw: dict[str, str | None], source_file: str
) -> VehicleReferenceCatalogRow:
    row_payload = {key: (raw.get(key) or "").strip() for key in REQUIRED_COLUMNS}
    aliases = _parse_aliases(row_payload["aliases"])
    make_key = canonical_key(row_payload["make_key"])
    model_key = canonical_key(row_payload["model_key"])
    if make_key is None or model_key is None:
        raise VehicleReferenceCatalogCsvError("make_key and model_key are required")

    row = VehicleReferenceCatalogRow(
        id=None,
        market=row_payload["market"],
        make_key=make_key,
        make_display=row_payload["make_display"],
        model_key=model_key,
        model_display=row_payload["model_display"],
        generation=_empty(row_payload["generation"]),
        body_code=_empty(row_payload["body_code"]),
        start_year=_year(row_payload["start_year"], "start_year"),
        end_year=_year(row_payload["end_year"], "end_year"),
        facelift_start_year=_year(row_payload["facelift_start_year"], "facelift_start_year"),
        facelift_end_year=_year(row_payload["facelift_end_year"], "facelift_end_year"),
        aliases=aliases,
        confidence=row_payload["confidence"] or "manual",
        source_file=source_file,
        source_row_hash=canonical_hash(row_payload | {"aliases": aliases}),
    )
    return validate_vehicle_reference_catalog_row(row)


def _parse_aliases(value: str) -> dict[str, Any]:
    value = value.strip()
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        value = value[1:-1]
    if not value:
        return {}
    try:
        aliases = json.loads(value)
    except json.JSONDecodeError as exc:
        raise VehicleReferenceCatalogCsvError("aliases must be valid JSON") from exc
    if not isinstance(aliases, dict):
        raise VehicleReferenceCatalogCsvError("aliases must be a JSON object")
    return aliases


def _year(value: str, field_name: str) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise VehicleReferenceCatalogCsvError(f"{field_name} must be an integer") from exc


def _empty(value: str) -> str | None:
    return value or None
