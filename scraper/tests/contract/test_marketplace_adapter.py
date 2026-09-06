"""The adapter protocol is the only marketplace contract."""

from __future__ import annotations

import inspect

from src.fetch.algolia import DubizzleAdapter
from src.fetch.base import MarketplaceAdapter


def test_dubizzle_adapter_satisfies_the_protocol() -> None:
    assert isinstance(DubizzleAdapter, MarketplaceAdapter) or issubclass(
        DubizzleAdapter, MarketplaceAdapter
    )
    signature = inspect.signature(DubizzleAdapter.fetch)
    assert list(signature.parameters) == ["self", "make", "condition"]
