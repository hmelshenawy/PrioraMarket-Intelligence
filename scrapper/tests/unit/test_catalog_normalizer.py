from __future__ import annotations

from src.normalization.catalog_normalizer import canonicalize_key, normalize_make, normalize_model


def test_canonicalize_key_removes_case_spacing_and_separators() -> None:
    assert canonicalize_key(" Mercedes-Benz ") == "mercedesbenz"
    assert canonicalize_key("Mercedes Benz") == "mercedesbenz"
    assert canonicalize_key("mercedes_benz") == "mercedesbenz"
    assert canonicalize_key("C-Class") == "cclass"
    assert canonicalize_key("C Class") == "cclass"
    assert canonicalize_key("7 Series") == "7series"


def test_normalize_make_aliases() -> None:
    assert normalize_make("Mercedes-Benz") == "mercedesbenz"
    assert normalize_make("Mercedes Benz") == "mercedesbenz"
    assert normalize_make("Mercedes") == "mercedesbenz"
    assert normalize_make("VW") == "volkswagen"
    assert normalize_make("Chevy") == "chevrolet"


def test_normalize_model_aliases_by_make() -> None:
    assert normalize_model("mercedesbenz", "C-Class") == "cclass"
    assert normalize_model("Mercedes Benz", "C Class") == "cclass"
    assert normalize_model("mercedesbenz", "GLE") == "gleclass"
    assert normalize_model("bmw", "7 Series") == "7series"
    assert normalize_model("audi", "A4") == "a4"


def test_unknown_values_return_canonicalized_value_without_guessing() -> None:
    assert normalize_make("UnknownBrand") == "unknownbrand"
    assert normalize_model("unknownbrand", "Mystery Model") == "mysterymodel"


def test_catalog_lookup_uses_normalized_keys() -> None:
    catalog_rows = {
        ("global", "mercedesbenz", "cclass"): "global-mercedes-benz-c-class-w205",
        ("global", "bmw", "7series"): "global-bmw-7-series-g11",
    }

    make_key = normalize_make("Mercedes Benz")
    model_key = normalize_model(make_key, "C Class")

    assert catalog_rows[("global", make_key, model_key)] == "global-mercedes-benz-c-class-w205"
