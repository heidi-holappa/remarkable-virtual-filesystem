"""
Event bus provides a publisher/subscriber service.
Through it different application layers can publish
events for UI to process
"""

from collections.abc import Callable
from src.event.event import Event

EventHandler = Callable[[Event], None]

class EventBus:
    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: EventHandler) -> None:
        self._handlers.remove(handler)

    def publish(self, event: Event) -> None:
        for handler in tuple(self._handlers):
            handler(event)