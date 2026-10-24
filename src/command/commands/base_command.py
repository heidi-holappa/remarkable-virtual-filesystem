from abc import ABC, abstractmethod

from src.constant import ROOT_COLLECTION

from src.repository.remarkable_data_repository import RemarkableDataRepository


class BaseCommand(ABC):
    """
    Abstract base class for commands. Each command
    extends BaseCommand and implements the handle
    method.
    """

    def __init__(self, repository: RemarkableDataRepository) -> None:
        self._repository = repository

    @abstractmethod
    def handle(self, args: list[str]) -> None:
        """
        each command class specializes on handling
        a specific command.
        """

    # --------------------------
    #  Shared methods
    # --------------------------

    def _traverse_path(self, path: str) -> str | None:
        """
        Splits the provided path into a list of entries and tries to
        traverse through the given path changes. At its simplest a path
        change can be traversing to one directory above the current position
        with '..' or into a direct subdirectory.

        See the project wiki for a comprehensive list of path changing rules.

        raises:
          - `NoSuchDirectoryError`: if the only match is a DocumentType (file)
          - `NotFoundError`: if parent is not found

        :param path: a string representation of a path
        :return: an optional uuid of the target collection or None if
                    collection could not be found
        """
        directory_changes: list[str] = path.split(sep="/")
        collection_pointer: str | None = self._repository.get_current_collection()

        if directory_changes[0] == '':
            # In absolute path traversal begins at root
            collection_pointer = ROOT_COLLECTION

        for directory in directory_changes:
            match directory:
                # No directory change
                case '' | '.':
                    continue
                # Traverse to parent
                case '..':
                    collection_pointer = self._repository.get_parent(collection_pointer)
                # Traverse to descendant
                case _:
                    if not isinstance(collection_pointer, str):
                        break
                    collection_pointer = self._repository.get_collection(
                        directory, collection_pointer)
            if collection_pointer is None:
                break
        return collection_pointer