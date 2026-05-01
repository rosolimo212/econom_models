"""
Stub for messenger-style subscribers.

Real Telegram/Discord bots would subscribe to EventBus and forward
`snapshot` / `period_end` payloads. This module only records messages
for tests or future wiring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from econom_sim.events import EventBus


@dataclass
class MessengerStub:
    bus: EventBus
    messages: list[tuple[str, Any]] = field(default_factory=list)

    def attach(self) -> None:
        self.bus.subscribe(self._on_event)

    def _on_event(self, topic: str, payload: Any) -> None:
        self.messages.append((topic, payload))
