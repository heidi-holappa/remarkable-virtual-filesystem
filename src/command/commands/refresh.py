"""
Implementation of refresh command
"""
from src.exception import RemarkableOperationError
from .base_command import BaseCommand
from src.event.event import OutputCommandMessage

# pylint: disable=too-few-public-methods
class RefreshCommand(BaseCommand):
    """
    Implementation of refresh command
    """

    def handle(self, args: list[str]) -> None:
        """
        Invokes repository to handle refresh of Xochitl
        service and in-memory data

        :param args: manager for reMarkable workspace
        """
        try:
            self._repository.restart_xochitl()
        except RemarkableOperationError as e:
            self._event_bus.publish(OutputCommandMessage(
                "refresh",
                f"unexpected error occurred: {e}"
            ))
