"""
Event bus provides a publisher/subscriber service.
Through it different application layers can publish
events for UI to process
"""

from collections.abc import Callable
from src.event.event import Event

EventHandler = Callable[[Event], None]

class EventBus:
    """
    Event bus provides a publisher/subscriber service.
    Through it different application layers can publish
    events for UI to process
    """

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> None:
        """
        Registers an event handler to receive published events.

        :param handler: event handler
        """
        self._handlers.append(handler)

    def unsubscribe(self, handler: EventHandler) -> None:
        """
        Removes a registered event handler.

        :param handler: event handler
        """
        self._handlers.remove(handler)

    def publish(self, event: Event) -> None:
        """
        Dispatches an event to all registered handlers.

        :param event: an event to dispatch
        """
        for handler in tuple(self._handlers):
            handler(event)
