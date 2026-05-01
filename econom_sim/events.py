"""Lightweight event bus for UI / bots."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class EventBus:
    _subs: list[Callable[[str, Any], None]] | None = None

    def __post_init__(self) -> None:
        if self._subs is None:
            self._subs = []

    def subscribe(self, fn: Callable[[str, Any], None]) -> None:
        assert self._subs is not None
        self._subs.append(fn)

    def publish(self, topic: str, payload: Any = None) -> None:
        assert self._subs is not None
        for fn in list(self._subs):
            fn(topic, payload)
