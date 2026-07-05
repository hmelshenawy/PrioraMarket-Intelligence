from __future__ import annotations

from pathlib import Path


def test_scoped_out_generation_classification_is_absent() -> None:
    src_root = Path(__file__).parents[2] / "src"
    forbidden = (
        "generation_classification",
        "classify_generation",
        "generation_classifier",
        "predicted_generation",
        "vin_decode",
        "vin_decoder",
    )

    matches: list[str] = []
    for path in src_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text.lower():
                matches.append(f"{path.relative_to(src_root)}:{token}")

    assert matches == []
