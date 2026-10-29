"""
Base class for UI implementations
"""
from abc import ABC, abstractmethod
from src.event.event import Event


class Ui(ABC):
    """
    A base class for UI implementations
    """

    @abstractmethod
    def loop(self) -> None:
        """
        The main UI loop that reacts to user stimuli
        """


    @abstractmethod
    def render_event(self, event: Event) -> None:
        """
        An event listen subscribes to event bus
        and handles events published from other
        application layers.

        :param event: event to output
        """
