"""
Implementation of the change directory command
"""

from src.constant import (
    ROOT_COLLECTION,
    NOT_A_DIRECTORY,
    NO_SUCH_FILE_OR_DIRECTORY)

from src.exception import (
    NoSuchFileOrDirectoryError,
    NoSuchDirectoryError
)
from .base_command import BaseCommand

# pylint: disable=too-few-public-methods
class ChangeDirectoryCommand(BaseCommand):
    """
    Implementation of the change directory command
    """


    def handle(self, args: list[str]) -> None:
        """
        Handles command to change directory

        Usage examples:
          - cd foo
          - cd ../foo
          - cd /foo/bar

        :param args: the path to which directory should be changed to
        """

        if len(args) == 0:
            self._repository.set_current_collection(ROOT_COLLECTION)
        elif len(args) > 1:
            print("Usage: cd OR cd <path>")
            return
        else:
            try:
                operand: str = args[0]
                self._change_collection(operand)
            except (NoSuchFileOrDirectoryError,
                    NoSuchDirectoryError) as e:
                print(f"cd: {str(e)}")


    def _change_collection(self, operand_path: str) -> None:
        """
        Attempts to change current collection to the provided
        collection. If traversal of given path fails to locate
        a collection, InvalidPathError is raised.

        raises:
          - NoSuchDirectoryError: instead of passing the raised exception a
          new one is thrown to include the full path in error message
          - NoSuchFileOrDirectoryError: no matching file or directory was found

        :param operand_path: a string representation of a path operand
        """

        try:
            collection_pointer = self._traverse_path(operand_path)
        except NoSuchDirectoryError as e:
            raise NoSuchDirectoryError(f"{operand_path}: {NOT_A_DIRECTORY}") from e
        if collection_pointer is None:
            raise NoSuchFileOrDirectoryError(f"{operand_path}: {NO_SUCH_FILE_OR_DIRECTORY}")

        self._repository.set_current_collection(collection_pointer)
