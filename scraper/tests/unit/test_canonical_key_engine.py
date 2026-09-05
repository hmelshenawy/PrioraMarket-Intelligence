from __future__ import annotations

from src.normalize import canonicalize


def test_canonicalize_removes_separators_and_punctuation() -> None:
    assert canonicalize(" Mercedes-Benz ") == "mercedesbenz"
    assert canonicalize("Mercedes Benz") == "mercedesbenz"
    assert canonicalize("mercedes_benz") == "mercedesbenz"
    assert canonicalize("C-Class") == "cclass"


def test_canonicalize_preserves_semantic_letters_and_numbers() -> None:
    assert canonicalize("C200") == "c200"
    assert canonicalize("E53 AMG") == "e53amg"
    assert canonicalize("GLC300 Coupe") == "glc300coupe"
    assert canonicalize("7 Series") == "7series"


def test_canonicalize_is_stable_for_immutable_examples() -> None:
    assert canonicalize("Mercedes-Benz") == "mercedesbenz"
    assert canonicalize("C-Class") == "cclass"
    assert canonicalize("Land Rover") == "landrover"


def test_canonicalize_handles_empty_and_none() -> None:
    assert canonicalize(None) is None
    assert canonicalize("") is None
    assert canonicalize("   ") is None
