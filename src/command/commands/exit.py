"""
Implementation of exit command
"""
import sys
from src.command.commands.base_command import BaseCommand
from src.exception import RemarkableOperationError, InvalidArgumentError
from src.event.event import OutputCommandMessage

# pylint: disable=too-few-public-methods
class ExitCommand(BaseCommand):
    """
    Exits the application
    """

    def handle(self, args: list[str]) -> None:
        """
        Exits the application.

        :param args: an empty list
        """

        try:
            if args:
                raise InvalidArgumentError("exit: command does not support args")

            self._repository.restart_xochitl()
            sys.exit(0)
        except RemarkableOperationError as e:
            self._event_bus.publish(
                OutputCommandMessage(
                    "exit",
                    f"{e}"
                )
            )
            sys.exit(1)
