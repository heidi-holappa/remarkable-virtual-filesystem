from .base_command import BaseCommand

from src.exception import RemarkableOperationError


class RefreshCommand(BaseCommand):
    """
    TODO
    """

    def handle(self, args: list[str]) -> None:
        """
        Invokes repository to handle refresh of Xochitl
        service and in-memory data

        :param workspace_manager: manager for reMarkable workspace
        """
        try:
            self._repository.restart_xochitl()
        except RemarkableOperationError as e:
            print(f"refresh: unexpected error occurred: {e}")
