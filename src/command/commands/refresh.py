"""
Implementation of refresh command
"""
from src.exception import RemarkableOperationError
from .base_command import BaseCommand

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
            print(f"refresh: unexpected error occurred: {e}")
