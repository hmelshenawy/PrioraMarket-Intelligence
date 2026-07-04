"""Pytest configuration shared across the test suite."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make src/ importable without installation.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FIXTURES = ROOT / "tests" / "fixtures"


def load_fixture(name: str):
    with open(FIXTURES / name, encoding="utf-8") as f:
        return json.load(f)
