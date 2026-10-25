"""
Implementation of make directory command
"""

from src.exception import (
    RemarkableWriteError, InvalidPathError)
from src.constant import (
    VALID_VISIBLE_NAME_REGEX)
from .base_command import BaseCommand

# pylint: disable=too-few-public-methods
class MakeDirectoryCommand(BaseCommand):
    """
    Implementation of make directory command
    """

    def handle(self, args: list[str]) -> None:
        """
        Tries to create a new directory

        :param args: arguments provided for the mkdir command
        """
        if len(args) != 1:
            print("mkdir: usage: mkdir <path>")
            return


        operand_path = args[0]
        self._process_mkdir(operand_path)

    # -------------------------
    # mkdir
    # -------------------------
    def _process_mkdir(self, operand_path: str, parent: str | None = None) -> None:
        """
        Tries to create a new subdirectory to the current
        parent.

        Handles possible raised errors:
          - InvalidPathError if path is not valid
          - RemarkableWriteError if an error occurs while
            communicating with the remarkable device

        :param operand_path: path to create
        :param parent: optional UUID of parent collection.
                        Defaults to current parent collection
        """

        if not parent:
            parent = self._repository.get_current_collection()

        try:
            self._validate_path(operand_path)

            self._create_collection_metadata_and_invoke_write(
                parent, operand_path)

        except InvalidPathError as e:
            print(f"mkdir: {operand_path}: {e}: hint: try help mkdir")
        except RemarkableWriteError as e:
            print(f"mkdir: {operand_path}: error writing to remarkable: {e}")


    def _validate_path(self, path: str) -> None:
        """
        Validates a provided path. Currently, a valid
        path name meets the following conditions:

        * path name can not be None or an empty string
        * parent must not have child path with same name
        * path name can contain: alphanumeric characters
          (a-zA-Z0-9), slash (-), underscore (_) and dots (.)

        raises:
          - InvalidPathError: if validation fails

        :param path: path to validate
        """

        if not path:
            raise InvalidPathError("path cannot be an empty string")

        if self._parent_has_child_path_with_given_name(
                self._repository.get_current_collection(), path):
            raise InvalidPathError("path with same name already exists")

        if '/' in path:
            raise InvalidPathError("relative or absolute paths are not yet supported")

        if not bool(VALID_VISIBLE_NAME_REGEX.fullmatch(path)):
            raise InvalidPathError("path contains invalid characters")
