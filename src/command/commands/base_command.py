from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    Abstract base class for commands. Each command
    extends BaseCommand and implements the handle
    method.
    """

    @abstractmethod
    def handle(self, args: list[str]) -> None:
        """
        each command class specializes on handling
        a specific command.
        """