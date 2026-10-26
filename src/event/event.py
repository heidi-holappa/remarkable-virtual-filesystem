"""
Event data class has a base class and
event types extending it.
"""


from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    """Base class for application events."""
    pass


@dataclass(frozen=True)
class OutputMessage(Event):
    command: str
    message: str


@dataclass(frozen=True)
class ProgressUpdate(Event):
    command: str
    message: str
    current: int
    total: int


