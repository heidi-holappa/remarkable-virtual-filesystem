"""
Event data class has a base class and
event types extending it.
"""


from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    """Base class for application events."""

@dataclass(frozen=True)
class OutputMessage(Event):
    """
    Outputs a message to the UI for the user
    """
    command: str
    message: str


@dataclass(frozen=True)
class ProgressUpdate(Event):
    """
    Special output containing a progress update.
    Useful for processes that want to update
    progress to the user, as remote copy.
    """
    command: str
    message: str
    current: int
    total: int
