from __future__ import annotations

import csv

from src.db.vehicle_reference_catalog_csv import read_vehicle_reference_catalog_csv


def _row(**overrides):
    row = {
        "market": "global",
        "make_key": "Mercedes-Benz",
        "make_display": "Mercedes-Benz",
        "model_key": "C-Class",
        "model_display": "C-Class",
        "generation": "W206",
        "body_code": "W206",
        "start_year": "2021",
        "end_year": "",
        "facelift_start_year": "",
        "facelift_end_year": "",
        "aliases": '{"make":["Mercedes"],"model":["C Class"]}',
        "confidence": "manual",
    }
    row.update(overrides)
    return row


def _write(path, rows, fieldnames=None):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames or list(_row().keys()),
            quotechar="'",
        )
        writer.writeheader()
        writer.writerows(rows)


def test_vehicle_reference_catalog_csv_reads_valid_rows(tmp_path) -> None:
    path = tmp_path / "catalog.csv"
    _write(path, [_row()])

    rows, errors = read_vehicle_reference_catalog_csv(path)

    assert errors == []
    assert rows[0].make_key == "mercedesbenz"
    assert rows[0].model_key == "cclass"
    assert rows[0].source_file == "catalog.csv"
    assert rows[0].source_row_hash


def test_vehicle_reference_catalog_csv_reports_invalid_rows(tmp_path) -> None:
    path = tmp_path / "catalog.csv"
    _write(path, [_row(start_year="not-a-year")])

    rows, errors = read_vehicle_reference_catalog_csv(path)

    assert rows == []
    assert "start_year must be an integer" in errors[0]


def test_vehicle_reference_catalog_csv_reports_missing_columns(tmp_path) -> None:
    path = tmp_path / "catalog.csv"
    _write(path, [{"market": "global"}], fieldnames=["market"])

    rows, errors = read_vehicle_reference_catalog_csv(path)

    assert rows == []
    assert "missing columns" in errors[0]
