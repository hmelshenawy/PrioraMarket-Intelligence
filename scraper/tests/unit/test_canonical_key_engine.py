from __future__ import annotations

from src.normalize.canonical import canonical_key


def test_canonical_key_removes_separators_and_punctuation() -> None:
    assert canonical_key(" Mercedes-Benz ") == "mercedesbenz"
    assert canonical_key("Mercedes Benz") == "mercedesbenz"
    assert canonical_key("mercedes_benz") == "mercedesbenz"
    assert canonical_key("C-Class") == "cclass"


def test_canonical_key_preserves_semantic_letters_and_numbers() -> None:
    assert canonical_key("C200") == "c200"
    assert canonical_key("E53 AMG") == "e53amg"
    assert canonical_key("GLC300 Coupe") == "glc300coupe"
    assert canonical_key("7 Series") == "7series"


def test_canonical_key_is_stable_for_immutable_examples() -> None:
    assert canonical_key("Mercedes-Benz") == "mercedesbenz"
    assert canonical_key("C-Class") == "cclass"
    assert canonical_key("Land Rover") == "landrover"
